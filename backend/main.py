from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer import oauth_authorized
import requests, os
from functools import wraps
import markdown
import base64

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.secret_key = os.getenv("SECRET_KEY", "dev")
CORS(app)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["github_analyzer"]
searches = db["search_logs"]
users = db["users"]

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else None,
    "User-Agent": "GitHub-Profile-Analyzer"
}
# Clean up None values
HEADERS = {k: v for k, v in HEADERS.items() if v is not None}

github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_OAUTH_CLIENT_SECRET"))
app.register_blueprint(github_bp, url_prefix="/github_login")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search")
def search_user():
    username = request.args.get("username")
    if not username:
        return redirect(url_for("home"))
    try:
        url = f"https://api.github.com/users/{username}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            flash(f"User '{username}' not found on GitHub.", "error")
            return redirect(url_for("home"))

        data = response.json()
        searches.insert_one({"username": username, "ip": request.remote_addr})
    except requests.exceptions.RequestException as e:
        print("GitHub API error:", e)
        return render_template("summary.html", user={}, error="GitHub API error")
    return redirect(url_for("summary", username=username))

@app.route("/summary/<username>")
def summary(username):
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated"

    user_response = requests.get(user_url, headers=HEADERS)
    repos_response = requests.get(repos_url, headers=HEADERS)
    

    if user_response.status_code != 200:
        return render_template("summary.html", user={}, repos=[])

    user_data = user_response.json()
    repos_data = repos_response.json() if repos_response.status_code == 200 else []

    return render_template("summary.html", user=user_data, repos=repos_data)

@app.route("/dashboard/<username>")
def dashboard(username):
    # Determine user session state
    logged_in_email = session.get("user")
    github_id = session.get("github_id")
    is_email_only = logged_in_email and not github_id
    is_github_connected = github_id == username

    # Determine target user to fetch (searched user or self)
    target_username = request.args.get("username") or (github_id if github_id else None)

    if is_email_only and not target_username:
        # Email-only user with no GitHub search
        return render_template("dashboard.html",
                               user=None,
                               repos=[],
                               github_connected=False,
                               logged_in_username=username)

    if not target_username:
        flash("GitHub account not connected.", "warning")
        return redirect(url_for("dashboard", username=username))

    # Fetch GitHub user & repos
    user_url = f"https://api.github.com/users/{target_username}"
    repos_url = f"https://api.github.com/users/{target_username}/repos?sort=updated"

    try:
        user_response = requests.get(user_url, headers=HEADERS)
        repos_response = requests.get(repos_url, headers=HEADERS)
    except Exception as e:
        print("GitHub API error:", e)
        flash("Failed to fetch GitHub data.", "error")
        return redirect(url_for("dashboard", username=username))

    if user_response.status_code != 200:
        flash(f"GitHub user '{target_username}' not found.", "error")
        return redirect(url_for("dashboard", username=username))

    user_data = user_response.json()
    repos_data = repos_response.json() if repos_response.status_code == 200 else []

    # Optional: compute language chart data
    language_totals = {}
    total_bytes = 0
    for repo in repos_data:
        lang_url = repo.get("languages_url")
        if not lang_url: continue
        lang_resp = requests.get(lang_url, headers=HEADERS)
        if lang_resp.ok:
            for lang, bytes in lang_resp.json().items():
                language_totals[lang] = language_totals.get(lang, 0) + bytes
                total_bytes += bytes

    language_data = None
    if total_bytes > 0:
        language_data = {
            "labels": list(language_totals.keys()),
            "values": [round((v / total_bytes) * 100, 2) for v in language_totals.values()]
        }

    return render_template("dashboard.html",
                           user=user_data,
                           repos=repos_data,
                           language_data=language_data,
                           github_connected=is_github_connected,
                           logged_in_username=username)

@app.route("/dashboard")
def dashboard_redirect():
    if "github_id" in session:
        return redirect(url_for("dashboard", username=session["github_id"]))
    elif "user" in session:
        user = users.find_one({"email": session["user"]})
        if user and "github_id" in user:
            return redirect(url_for("dashboard", username=user["github_id"]))
        else:
            # Email-only user, no GitHub linked
            return redirect(url_for("dashboard", username=""))
    flash("Login required.", "danger")
    return redirect(url_for("login"))

def get_repo_tree(username, repo_name, path=""):
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{path}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        contents = response.json()
    except Exception as e:
        print("GitHub API error:", e)
        return []

    tree = []
    for item in contents:
        if item["type"] == "file":
            tree.append({"name": item["name"], "type": "file"})
        elif item["type"] == "dir":
            tree.append({
                "name": item["name"],
                "type": "dir",
                "children": get_repo_tree(username, repo_name, item["path"])
            })
    return tree

@app.route("/repo/<username>/<repo_name>")
def repo_detail(username, repo_name):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    # Repo metadata
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    repo_resp = requests.get(repo_url, headers=headers)
    if not repo_resp.ok:
        flash("Failed to fetch repository details", "danger")
        return redirect(url_for("dashboard_redirect"))
    repo = repo_resp.json()

    # Language usage
    lang_url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
    lang_resp = requests.get(lang_url, headers=headers)
    languages = lang_resp.json() if lang_resp.ok else {}

    # README
    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    readme_resp = requests.get(readme_url, headers=headers)
    readme_html = ""
    if readme_resp.ok:
        readme_data = readme_resp.json()
        content = base64.b64decode(readme_data["content"]).decode("utf-8")
        readme_html = markdown.markdown(content)

    # File structure
    file_tree = get_repo_tree(username, repo_name)
    color_palette = ['#60a5fa', '#f472b6', '#34d399', '#fbbf24', '#a78bfa', '#fb7185', '#facc15', '#fdba74', '#4ade80']

    return render_template(
        "repo_detail.html",
        username=username,
        repo_name=repo_name,
        repo=repo,  # ✅ Pass this to the template
        languages=languages,
        readme_html=readme_html,
        file_tree=file_tree,
        color_palette=color_palette
    )

@app.route("/api/repos/<username>")
def get_more_repos(username):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 6))
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page={per_page}&page={page}"

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        print("Repo fetch failed:", e)
        return jsonify([]), 500

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Login required to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        submitted = True  # Track form submission
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Basic validations
        if not name or not email or not password:
            flash("Please fill in all fields", "danger")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format", "danger")
        elif users.find_one({"email": email}):
            flash("Email already registered", "danger")
        else:
            users.insert_one({
                "name": name,
                "email": email,
                "password": generate_password_hash(password)
            })
            flash("Registered successfully. Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").lower()
        password = request.form.get("password")

        user = users.find_one({"email": email})
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))

        session["user"] = user["email"]
        flash("Logged in successfully!", "success")
        return redirect(url_for("home"))  # adjust to your landing route

    return render_template("login.html")


@app.route("/login/github")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))

    resp = github.get("/user")
    if not resp.ok:
        flash("GitHub login failed.", "danger")
        return redirect(url_for("login"))

    github_data = resp.json()
    github_id = github_data["login"]

    existing_user = users.find_one({"github_id": github_id})
    if not existing_user:
        users.insert_one({
            "github_id": github_id,
            "name": github_data.get("name"),
            "email": github_data.get("email"),
            "avatar_url": github_data.get("avatar_url"),
            "github_profile": github_data.get("html_url")
        })

    session["github_id"] = github_id
    flash("Logged in with GitHub successfully", "success")
    return redirect(url_for("dashboard", username=github_id))

if __name__ == '__main__':
    app.run(debug=True)