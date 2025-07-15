try:
    from flask import Flask, render_template, request, redirect, url_for, jsonify, session, g
    from flask_cors import CORS
    from pymongo import MongoClient
    from collections import Counter
    from datetime import datetime, timedelta
    from werkzeug.security import generate_password_hash, check_password_hash
    from flask_dance.contrib.github import make_github_blueprint, github
    from flask_dance.consumer import oauth_error
    from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity,verify_jwt_in_request
    import requests, os
    from functools import wraps
    from dotenv import load_dotenv
    import markdown
    import base64
    import re
except ImportError as e:
    print("Required libraries are not installed. Please run 'pip install -r requirements.txt'.")
    raise e

app = Flask(__name__)

# Load environment variables
load_dotenv()
  
#session for oauth
app.secret_key   = os.getenv("SESSION_SECRET_KEY")
app.config["SESSION_COOKIE_NAME"] = "github_analyzer_session"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# JWT configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY") 
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
app.config["JWT_COOKIE_SECURE"] = True 
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_COOKIE_CSRF_PROTECT"] = True 

jwt = JWTManager(app)
CORS(app)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["github_analyzer"]
searches = db["search_logs"]
users = db["users"]

# GitHub API setup
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else None,
    "User-Agent": "GitHub-Profile-Analyzer"}
HEADERS = {k: v for k, v in HEADERS.items() if v is not None}

# GitHub OAuth setup
github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_OAUTH_CLIENT_SECRET"),
    scope="user:email",
    redirect_to="github_callback_redirect"
)
app.register_blueprint(github_bp, url_prefix="/github_login")

def hybrid_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        identity = None
        jwt_error = None
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
        except Exception as e:
            jwt_error = str(e)

        session_user = session.get("user") or session.get("github_id")

        if identity or session_user:
            return f(*args, **kwargs)

        print(f"JWT error: {jwt_error}, Session user: {session_user}")
        return redirect(url_for("login", msg="Please log in to access this page.", category="warning"))
    return decorated_function

# Function to get the logged-in user from JWT or session
def get_logged_in_user():
    if hasattr(g, "logged_in_user"):
        return g.logged_in_user

    identity = get_jwt_identity()
    if not identity:
        return None
    user = users.find_one({
        "$or": [{"email": identity}, {"github_id": identity}]
    })
    g.logged_in_user = user
    return user

#Routes
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
            return redirect(url_for("home"), msg="GitHub user not found.", category="error")
        data = response.json()
        searches.insert_one({"username": username, "ip": request.remote_addr})
    except requests.exceptions.RequestException as e:
        print("GitHub API error:", e)
        return render_template("summary.html", user={}, error="GitHub API error")
    return redirect(url_for("summary", username=username, data=data))

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
@hybrid_login_required
def dashboard(username):
    identity = get_jwt_identity()
    # Validate access: identity must match username (email or GitHub ID)
    if identity != username:
        user =get_logged_in_user({"email": identity})
        if not user or user.get("github_id") != username:
            return redirect(url_for("dashboard_redirect", msg="Unauthorized access.", category="danger"))

    target_username = request.args.get("username") or username
    user_record = get_logged_in_user({"email": identity})
    if user_record and "github_id" not in user_record and not request.args.get("username"):
        return render_template(
            "dashboard.html",
            user=None,
            repos=[],
            language_data=None,
            github_connected=False,
            logged_in_username=identity
        )
    user_url = f"https://api.github.com/users/{target_username}"
    repos_url = f"https://api.github.com/users/{target_username}/repos?sort=updated"

    try:
        user_resp = requests.get(user_url, headers=HEADERS)
        repos_resp = requests.get(repos_url, headers=HEADERS)
    except Exception as e:
        print("GitHub API error:", e)
        return redirect(url_for("dashboard_redirect", msg="Failed to fetch GitHub data.", category="error"))

    if user_resp.status_code != 200:
        return redirect(url_for("dashboard_redirect", msg=f"GitHub user '{target_username}' not found.", category="error"))

    user_data = user_resp.json()
    repos_data = repos_resp.json() if repos_resp.status_code == 200 else []

    for repo in repos_data:
        repo["tags"] = extract_tags(repo)

    all_tags = sorted({tag for repo in repos_data for tag in repo["tags"]})

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
    msg = request.args.get("msg")
    category = request.args.get("category") or "info"
    insights = compute_insights(repos_data)
    user_record = get_logged_in_user({"email": identity}) or get_logged_in_user({"github_id": identity})
    return render_template(
    "dashboard.html",
    user=user_data,
    repos=repos_data,
    insights=insights,
    language_data=language_data,
    github_connected=True,
    stack_tags=all_tags,
    logged_in_username=identity,
    logged_in_user=user_record,
    msg=msg,
    category=category
)

@app.route("/dashboard")
@hybrid_login_required
def dashboard_redirect():
    identity = get_jwt_identity()
    msg = request.args.get("msg")
    category = request.args.get("category") or "info"
    
    #finding user by GitHub ID
    user = get_logged_in_user({"github_id": identity})
    if user:
        return redirect(url_for("dashboard",  username=identity, msg=msg, category=category))

    # else email login
    user = get_logged_in_user({"email": identity})
    if user and "github_id" in user:
        return redirect(url_for("dashboard", username=user["github_id"], msg=msg, category=category))
    elif user:
        return redirect(url_for("dashboard", username=identity, msg=msg, category=category))
    return redirect(url_for("login", msg="User not found.", category="danger"))

@hybrid_login_required
@app.route("/repo/<username>/<repo_name>")
def repo_detail(username, repo_name):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    # Repo metadata
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    repo_resp = requests.get(repo_url, headers=headers)
    if not repo_resp.ok:
        return redirect(url_for("dashboard_redirect", msg="Failed to fetch repository details", category="danger"))
    repo = repo_resp.json()

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
        repo=repo,
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
@hybrid_login_required
def settings():
    identity = get_jwt_identity()
    user = get_logged_in_user({"$or": [{"email": identity}, {"github_id": identity}]})
    if not user:
        return redirect(url_for("login", msg="User not found", category="danger"))

    return render_template("settings.html", logged_in_user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email', '').lower()
        password = request.form.get('password')
        
        
        if not name or not email or not password:
            return redirect(url_for("register", msg="Please fill in all fields", category="danger"))

        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return redirect(url_for("register", msg="Invalid email format", category="danger"))

        elif get_logged_in_user({"email": email}):
            return redirect(url_for("login", msg="Email already registered", category="danger"))

        else:
            users.insert_one({
                "name": name,
                "email": email,
                "password": generate_password_hash(password)
            })
            #session for github addon
            session["user"] = email
            #JWT cookie
            access_token = create_access_token(identity=email)
            response = redirect(url_for("dashboard_redirect", msg="Registered successfully", category="success"))
            response.set_cookie("access_token", access_token, httponly=True)
            return response
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").lower()
        password = request.form.get("password")

        user = get_logged_in_user({"email": email})
        if not user or not check_password_hash(user["password"], password):
            return redirect(url_for("login", msg="Invalid email or password.", category="error"))
        #session for github addon
        session["user"] = email
        #JWT cookie
        access_token = create_access_token(identity=email)
        response = redirect(url_for("dashboard_redirect", msg="Logged in successfully!", category="success"))
        response.set_cookie("access_token", access_token, httponly=True)
        return response

    return render_template("login.html")

@app.route("/login/github")
def github_login():
    print("/login/github called")
    session["oauth_start"] = True
    return redirect(url_for("github.login"))

@app.route("/github_login/github/authorized")
def github_callback_redirect():
    print(" GITHUB CALLBACK HIT")
    print("OAuth token in session:", dict(session))
    print("github.authorized =", github.authorized)


    if "oauth_start" in session:
        print("Logged in via GitHub button")
        session["oauth_start_logged"] = True 

    if not github.authorized:
        return redirect(url_for("dashboard_redirect", msg="GitHub login failed or was denied.", category="danger"))

    resp = github.get("/user")
    if not resp.ok:
        return redirect(url_for("login", msg="GitHub API request failed.", category="danger"))

    github_data = resp.json()
    github_id = github_data["login"]
    github_email = github_data.get("email")
    if not github_email:
    # If email not provided, fetch emails
        emails_resp = github.get("/user/emails")
        if emails_resp.ok:
            email_list = emails_resp.json()
            # primary + verified email
            primary_verified = next((e["email"] for e in email_list if e["primary"] and e["verified"]), None)
            if primary_verified:
                github_email = primary_verified

    github_profile = github_data.get("html_url")
    avatar_url = github_data.get("avatar_url")
    name = github_data.get("name")

    # Create or update user in database
    user = get_logged_in_user({"github_id": github_id})
    if not user:
        users.insert_one({
            "github_id": github_id,
            "name": name,
            "email": github_email,
            "avatar_url": avatar_url,
            "github_profile": github_profile,
            "connected": True
        })
    else:
        users.update_one(
            {"github_id": github_id},
            {"$set": {
                "name": name,
                "email": github_email,
                "avatar_url": avatar_url,
                "github_profile": github_profile,
                "connected": True
            }}
        )
    access_token = create_access_token(identity=github_id)
    session["github_id"] = github_id 
    response = redirect(url_for("dashboard", username=github_id, msg="Logged in successfully via GitHub!", category="success"))
    response.set_cookie("access_token", access_token, httponly=True)
    return response

@app.route("/logout")
def logout():
    session.clear()
    response = redirect(url_for("home", msg="You have been logged out.", category="info"))
    response.delete_cookie("access_token")
    return response

@oauth_error.connect_via(github_bp)
def github_oauth_error(blueprint, message, response):
    print("OAuth error from GitHub! Message:", message)
    print("Response:", response)

@app.context_processor
def inject_logged_in_user():
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()
        if not identity:
            return {"logged_in_user": None}

        # Try to find user by email or GitHub ID
        user = get_logged_in_user({
            "$or": [{"email": identity}, {"github_id": identity}]
        })
        return {
            "logged_in_user": user,
            "logged_in_username": identity 
        }
    except Exception:
        return {"logged_in_user": None}

@app.route('/healthz')
def health():
    return "ok", 200

#fuctions:

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
            tree.append({
                "name": item["name"],
                "type": "file",
                "url": item["html_url"]
            })
        elif item["type"] == "dir":
            tree.append({
                "name": item["name"],
                "type": "dir",
                "url": f"https://github.com/{username}/{repo_name}/tree/main/{item['path']}",
                "children": get_repo_tree(username, repo_name, item["path"])
            })
    return tree

def compute_insights(repos):
    now = datetime.utcnow()
    for repo in repos:
        repo["commits"] = repo.get("commits", [])
        repo["readme"] = repo.get("readme", "")
        
    most_active = max(repos, key=lambda r: len(r["commits"]), default=None)

    def last_commit_time(repo):
        dates = [datetime.strptime(c, "%Y-%m-%dT%H:%M:%SZ") for c in repo["commits"]]
        return max(dates) if dates else datetime.min

    repos_excl_most_active = [r for r in repos if r != most_active]
    least_active = min(repos_excl_most_active, key=last_commit_time, default=None) if repos_excl_most_active else None
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