from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_cors import CORS
from pymongo import MongoClient
from collections import Counter
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer import oauth_authorized
import requests, os
from functools import wraps
import markdown
import base64
import re

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
    "User-Agent": "GitHub-Profile-Analyzer"}
# Clean up None values
HEADERS = {k: v for k, v in HEADERS.items() if v is not None}

github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_OAUTH_CLIENT_SECRET"))
app.register_blueprint(github_bp, url_prefix="/github_login")

@app.route("/")
def home():
    
    projects = [
    {
        'title': 'Financia:',
        'desc': 'A personal finance tracker to help you stay on top of your expenses and income.',
        'image': '/static/images/financia-logo.png',
        'link': 'https://github.com/Kabya002/Financia'
    },
    {
        'title': 'Blog:',
        'desc': 'A clean, minimalist space where anyone can share their thoughts and stories—like a cozy corner of the internet.',
        'image': '/static/images/blog-logo.png',
        'link': 'https://blog-c0p3.onrender.com/'
    },
    {
        'title': 'Portfolio Website',
        'desc': 'A beautifully crafted personal website to showcase projects, skills, and a journey in tech.',
        'image': '/static/images/portfolio-logo.png',
        'link': 'https://github.com/Kabya002/Portfolio'
    }
]

    if "github_id" in session:
        return redirect(url_for("dashboard", username=session["github_id"]))
    elif "user" in session:
        return redirect(url_for("dashboard", username=session["user"]))
    return render_template("home.html", projects=projects)

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
    # Determine session state
    logged_in_email = session.get("user")
    github_id = session.get("github_id")

    is_email_only = logged_in_email and not github_id
    is_github_connected = github_id == username
    logged_in_username = github_id or logged_in_email

    # Determine who to display: searched user or self
    target_username = request.args.get("username") or (github_id if github_id else None)

    # If email-only user without a GitHub search
    if is_email_only and not target_username:
        return render_template(
            "dashboard.html",
            user=None,
            repos=[],
            language_data=None,
            github_connected=False,
            logged_in_username=logged_in_username
        )

    # No GitHub to show
    if not target_username:
        flash("GitHub account not connected.", "warning")
        return redirect(url_for("dashboard", username=logged_in_username))

    # Fetch GitHub user & repos
    user_url = f"https://api.github.com/users/{target_username}"
    repos_url = f"https://api.github.com/users/{target_username}/repos?sort=updated"

    try:
        user_resp = requests.get(user_url, headers=HEADERS)
        repos_resp = requests.get(repos_url, headers=HEADERS)
    except Exception as e:
        print("GitHub API error:", e)
        flash("Failed to fetch GitHub data.", "error")
        return redirect(url_for("dashboard", username=logged_in_username))

    if user_resp.status_code != 200:
        flash(f"GitHub user '{target_username}' not found.", "error")
        return redirect(url_for("dashboard", username=logged_in_username))

    user_data = user_resp.json()
    repos_data = repos_resp.json() if repos_resp.status_code == 200 else []
    # Tag extraction for Tech Stack filtering
    for repo in repos_data:
        repo["tags"] = extract_tags(repo)

    # Collect all unique stack tags
    all_tags = sorted({tag for repo in repos_data for tag in repo["tags"]})


    # Optional: compute language usage chart
    language_totals = {}
    total_bytes = 0

    for repo in repos_data:
        lang_url = repo.get("languages_url")
        if not lang_url:
            continue
        try:
            lang_resp = requests.get(lang_url, headers=HEADERS)
            if lang_resp.ok:
                langs = lang_resp.json()
                for lang, bytes_count in langs.items():
                    language_totals[lang] = language_totals.get(lang, 0) + bytes_count
                    total_bytes += bytes_count
        except:
            continue

    language_data = None
    if total_bytes > 0:
        language_data = {
            "labels": list(language_totals.keys()),
            "values": [round((v / total_bytes) * 100, 2) for v in language_totals.values()]
        }
    insights = compute_insights(repos_data)
    return render_template(
        "dashboard.html",
        user=user_data,
        repos=repos_data,
        insights=insights,
        language_data=language_data,
        github_connected=is_github_connected,
        stack_tags=all_tags,
        logged_in_username=logged_in_username
    )

@app.route("/dashboard")
def dashboard_redirect():
    if "github_id" in session:
        return redirect(url_for("dashboard", username=session["github_id"]))
    elif "user" in session:
        user = users.find_one({"email": session["user"]})
        if user and "github_id" in user:
            return redirect(url_for("dashboard", username=user["github_id"]))
        else:
            return redirect(url_for("dashboard", username=session["user"]))  # email-only view
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

@app.route("/settings")
def settings():
    if "user" not in session and "github_id" not in session:
        flash("Please log in to view your settings.", "warning")
        return redirect(url_for("login"))
    return render_template("settings.html")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Login required to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_globals():
    return dict(users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        submitted = True  # Track form submission
        name = request.form.get('name')
        email = request.form.get('email').lower()
        password = request.form.get('password')

        # Basic validations
        if not name or not email or not password:
            flash("Please fill in all fields", "danger")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format", "danger")
        elif users.find_one({"email": email}):
            flash("Email already registered", "danger")
            return redirect(url_for("login"))
        else:
            users.insert_one({
                "name": name,
                "email": email,
                "password": generate_password_hash(password)
            })
            session["user"] = email  # Set session
            flash("Registered successfully", "success")
            return redirect(url_for("dashboard_redirect"))

    return render_template("register.html")


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
        return redirect(url_for("dashboard_redirect"))

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
    github_profile = github_data.get("html_url")
    github_email = github_data.get("email")
    avatar_url = github_data.get("avatar_url")
    name = github_data.get("name")

    # If the user already logged in with email before and wants to connect GitHub
    if "user" in session and "github_id" not in session:
        users.update_one(
            {"email": session["user"]},
            {
                "$set": {
                    "github_id": github_id,
                    "github_profile": github_profile,
                    "avatar_url": avatar_url,
                    "name": name,
                    "connected": True
                }
            }
        )
        session["github_id"] = github_id
        flash("GitHub account connected successfully!", "success")
        return redirect(url_for("dashboard", username=github_id))
    else:
        # Check if user exists by GitHub ID
        existing_user = users.find_one({"github_id": github_id})

        if not existing_user:
            # Insert new GitHub-only user
            users.insert_one({
                "github_id": github_id,
                "name": name,
                "email": github_email,  # May be None if GitHub email is private
                "avatar_url": avatar_url,
                "github_profile": github_profile,
                "connected": True
            })

    # Log in GitHub user
    session["github_id"] = github_id
    flash("Logged in with GitHub successfully!", "success")
    return redirect(url_for("dashboard", username=github_id))

@app.route("/logout")
def logout():
    # Clear all session data
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route('/healthz')
def health():
    return "ok", 200

#fuctions:

def compute_insights(repos):
    now = datetime.utcnow()

    # Prepare commit timestamps (already part of your fetch logic)
    for repo in repos:
        # You'll replace this with real commit timestamps per repo (last 100 is enough)
        repo["commits"] = repo.get("commits", [])  # A list of commit dates in ISO format
        repo["readme"] = repo.get("readme", "")     # Already fetched README content

    # Most Active Repo
    most_active = max(repos, key=lambda r: len(r["commits"]), default=None)

    # Least Active Repo — exclude the most active one
    def last_commit_time(repo):
        dates = [datetime.strptime(c, "%Y-%m-%dT%H:%M:%SZ") for c in repo["commits"]]
        return max(dates) if dates else datetime.min

    repos_excl_most_active = [r for r in repos if r != most_active]
    least_active = min(repos_excl_most_active, key=last_commit_time, default=None) if repos_excl_most_active else None


    # Most Loved = stars / commits
    most_loved = max(repos, key=lambda r: r["stargazers_count"] / max(len(r["commits"]), 1), default=None)

    # Tech Stack
    tech_keywords = ["react", "django", "flask", "node", "express", "vue", "tailwind", "next", "rest", "api", "typescript"]
    tech_counter = Counter()

    for repo in repos:
        readme = repo.get("readme", "").lower()
        for keyword in tech_keywords:
            if keyword in readme:
                tech_counter[keyword] += 1
        lang = repo.get("language")
        if lang:
            tech_counter[lang.lower()] += 1

    top_tech_stack = ", ".join([tech.title() for tech, _ in tech_counter.most_common(3)])

    # Growth Tip
    growth_tip = "Keep up the great work!"
    for repo in repos:
        if repo["stargazers_count"] > 50 and not repo.get("readme"):
            growth_tip = f"Add a README to {repo['name']} — it's your most starred project but lacks documentation."
            break

    return {
        "most_active_repo": most_active["name"] if most_active else "N/A",
        "most_loved_repo": most_loved["name"] if most_loved else "N/A",
        "least_active_repo": least_active["name"] if least_active else "N/A",
        "top_tech_stack": top_tech_stack or "N/A",
        "growth_tip": growth_tip
    }

def extract_tags(repo):
    tags = set()
    if repo.get("language"):
        tags.add(repo["language"])
    if repo.get("topics"):
        tags.update(repo["topics"])
    desc = (repo.get("description") or "") + " " + repo.get("name", "")
    keywords = ["react", "django", "flask", "next", "vue", "express", "node", "typescript", "python", "go", "rust"]
    for kw in keywords:
        if kw.lower() in desc.lower():
            tags.add(kw.title())
    return sorted(tags)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)