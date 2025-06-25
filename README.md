# GitHub Profile Analyzer 🚀

A clean, interactive web tool to fetch and visualize key details from any GitHub profile—with an optional AI-powered insights panel.

---

## 📺 Demo Video

> *(Please upload a short demo walkthrough here — e.g., using Loom, YouTube, or an embedded video. Ideally 1–2 minutes showing profile search, repo view, and AI insights.)*

---
## ⚙️ Features

- **User Profile Data**: Avatar, bio, location, followers, following, and more.  
- **Repositories List**: Displays each repo’s name, description, and primary language with js chart-analysis. 
- **Responsive UI**: Clean, mobile‑friendly design written in HTML/CSS/JS. :contentReference[oaicite:1]{index=1}

---
## 🌐 Live Demo

🚀 Deployed soon! Stay tuned.

## 🛠️ Tech Stack
| Layer         | Tools Used                        |
|---------------|------------------------------------|
| Frontend      | Tailwind CSS, SwiperJS, Font Awesome |
| Backend       | Flask (Python)                     |
| Template Engine | Jinja2                          |
| Hosting       | Coming soon…                       |
---

## ⚙️ Installation & Local Setup
1. Clone the repo:
   ```bash
   git clone https://github.com/Kabya002/Github-profile-analyzer.git
   cd Github-profile-analyzer
2. Serve locally (any static server works):
   ```bash
    # Python 3
    python3 -m http.server 8000
    # OR using Node.js (install serve: npm install -g serve)
    serve .
3. Open http://localhost:8000 in your browser.
---
🚀 Deployment
You can host this as a static site using:
| Platform           | Steps                                                                |
| ------------------ | -------------------------------------------------------------------- |
| **GitHub Pages**   | Push to a repo named username.github.io <br> 2. Enable Pages in Settings|
| **Netlify/Vercel** | Connect your Git repo <br> 2. Set build command to npm run build or none <br> 3. Deploy|
| **Static Hosting** | Upload content to any static web server or storage bucket (e.g., S3) |
---
🔐 API Considerations
1. Uses GitHub public APIs—no authentication required by default.
2. Rate limits apply: up to 60 unauthenticated requests per hour per IP.
3. For more requests, add an OAuth token:
     -Create a GitHub Personal Access Token.
     -Set it inside script.js where the API call is made.
---
📝 How to Use
1. Open the app in your browser.
2. Type the GitHub username in the search field and hit Search.
3. View profile and repositories.
4. Click View on GitHub for the real profile page.
## 📁 Folder Structure

/project-root
├── backend/
│ ├── app.py
│ ├── templates/
│ │ ├── base.html
│ │ └── home.html
│ └── static/
│ ├── css/
│ │ └── tailwind.css
│ └── images/
│ ├── hero-bg.jpeg
│ ├── features-bg.jpeg
│ ├── contact-bg.jpeg
│ ├── creator-bg.jpeg
│ └── shot1.png ... shot5.png
├── README.md
├── requirements.txt

---

## 🚀 Getting Started

### 1. Clone the Repository
    1. git clone https://github.com/yourusername/github-profile-analyzer.git
       cd github-profile-analyzer
    2. Set Up Virtual Environment
        python -m venv venv
        source venv/bin/activate  # on Windows: venv\Scripts\activate
    3. Install Requirements
        pip install -r requirements.txt
    4. Run the App
        flask run
        ###The app will be available at http://127.0.0.1:5000/.
        You can extend with @keyframes in Tailwind config for more custom effects.
---
✨ Contributing
>Contributions welcome!
---
🧾 License
>This project is released under the MIT License. See LICENSE for details.
---
🔗 References
>Adapted from the original GitHub Profile Analyzer by <a href="https://github.com/Amaan-Mujawar/GitHub-Profile-Analyzer?utm_source=chatgpt.com">Amaan Mujawar: sleek UI, repo insights, and AI query pop-up.</a>
