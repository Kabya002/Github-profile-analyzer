from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests, os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")
CORS(app)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["github_analyzer"]
searches = db["search_logs"]

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search")
def search_user():
    username = request.args.get("username")
    if not username:
        return redirect(url_for("home"))
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        flash(f"User '{username}' not found on GitHub.", "error")
        return redirect(url_for("home"))

    data = response.json()
    searches.insert_one({"username": username, "ip": request.remote_addr})

    return redirect(url_for("summary", username=username))

@app.route("/summary/<username>")
def summary(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return render_template("summary.html", user={})

    data = response.json()
    return render_template("summary.html", user=data)

@app.route("/api/user/<username>")
def api_user_summary(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return jsonify({"error": "User not found"}), 404

    data = response.json()
    return jsonify({
        "login": data.get("login"),
        "name": data.get("name"),
        "bio": data.get("bio"),
        "public_repos": data.get("public_repos"),
        "followers": data.get("followers"),
        "following": data.get("following")
    })

if __name__ == '__main__':
    app.run(debug=True)