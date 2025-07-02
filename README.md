# GitHub Profile Analyzer:

A clean, interactive web tool to fetch and visualize key details from any GitHub profile—with an optional AI-powered insights panel.

---

## Demo Video
>
---
## Features

- **User Profile Data**: Avatar, bio, location, followers, following, and more.  
- **Repositories List**: Displays each repo’s name, description, and primary language with js chart-analysis. 
- **Responsive UI**: Clean, mobile‑friendly design written in HTML/CSS/JS.

---
## Live Demo
- Deployed on render.

## Tech Stack
| Layer         | Tools Used                        |
|---------------|------------------------------------|
| Frontend      | Tailwind CSS, SwiperJS, Font Awesome |
| Backend       | Flask (Python)                     |
| Template Engine | Jinja2                          |
| Hosting       | Render                      |
---

## Installation & Local Setup
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

API Considerations
---
1. Uses GitHub public APIs—no authentication required by default.
2. Rate limits apply: up to 60 unauthenticated requests per hour per IP.
3. For more requests, add an OAuth token:
     -Create a GitHub Personal Access Token.
     -Set it inside script.js where the API call is made.
   
How to Use:
---
1. Open the app in your browser.
2. Type the GitHub username in the search field and hit Search.
3. View profile and repositories.
4. Click View on GitHub for the real profile page.

## Folder Structure
---
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

## Getting Started
---
    1. Clone the Repository
     git clone https://github.com/yourusername/github-profile-analyzer.git
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
