# GitHub Profile Analyzer:
A clean, interactive web tool to fetch and visualize key details from any GitHub profile—with an optional AI-powered insights panel.

---
## Demo Video:
>![Untitled video - Made with Clipchamp](https://github.com/user-attachments/assets/326f4a0e-1605-4e2f-9008-9ed60467ddc8)
> - A visual walkthrough of searching a GitHub username, exploring repo data, and viewing AI‑powered summaries.

---
## Features:
- **User Profile Data**: Avatar, bio, location, followers, following, and more.  
- **Repositories List**: Displays each repo’s name, description, and primary language with js chart-analysis. 
- **Responsive UI**: Clean, mobile‑friendly design written in HTML/CSS/JS.
- **MongoDB support**: for caching and user-session data.
-**Test suite included**: ensures data fetch reliability and response correctness.

---
## Live Demo:
- Deployed on [render](https://github-profile-analyzer-amax.onrender.com)

---
## Tech Stack:
| Layer     | Tools & Technologies                          |
| --------- | --------------------------------------------- |
| Frontend  | HTML, Tailwind CSS v3, SwiperJS, Font Awesome |
| Backend   | Python 3.12, Flask, Gunicorn                  |
| Database  | MongoDB                                       |
| Caching   | Optional MongoDB-backed cache                 |
| Container | Docker multi-stage build                      |
| Hosting   | Render                                        |
| Testing   | pytest + coverage suite                       |

---
## Installation & Local Setup
1. **Clone the repo**:
   ```
   git clone https://github.com/Kabya002/Github-profile-analyzer.git
   cd Github-profile-analyzer
2. **Without Docker (Manual Setup)**
   2.1 Build Tailwind & Frontend
   ```
   cd frontend
   npm install --legacy-peer-deps
   npx tailwindcss -i ./src/input.css -o ./tailwind.css --minify
   cd ..
   ```
   2.2 Backend Setup:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   2.3 Configure MongoDB:
   ```
   MONGODB_URI="mongodb://localhost:27017/github_analyzer"
   ```
   2.4 Run Flask App:
   ```
   export FLASK_APP=main.py
   flask run
   ```
3.**Docker (Recommended)**:
   ```
   docker build -t gh-profile-analyzer .
   docker run -it --rm -p 5000:5000 gh-profile-analyzer
   ```
## Testing:
Run the test suite:
```
pytest --cov=backend
```

---
## API Considerations:

1. Uses GitHub public APIs—no authentication required by default.
2. Rate limits apply: up to 60 unauthenticated requests per hour per IP.
3. For more requests, add an OAuth token:
     - Create a GitHub Personal Access Token.
     - Set it inside script.js where the API call is made.

---
## How to Use:
1. Open the app in your browser.
2. Type the GitHub username in the search field and hit Search.
3. View profile and repositories.
4. Click View on GitHub for the real profile page.

---
## Dockerfile Explained:
**Stage 1 – Frontend build**:
   - Based on Node 18, builds Tailwind CSS styling
   - Copies your templates and front-end assets
   - Outputs tailwind.css
**Stage 2 – Python backend**:
   - Uses slim Python 3.12
   - Adds a non-root user for security
   - Installs system packages (cURL, Git, build tools)
   - Copies backend + built CSS
   - Installs dependencies securely with pip
   - Runs Flask via Gunicorn with a healthcheck
   - Exposes port 5000 for Render

---
## Roadmap:
- MongoDB integration & caching
- pytest tests
- Add user session persistence
- Extend AI insights (trends, commit messages, PR histories)
- Docker‑Compose with Mongo sidecar
- CI pipeline (GitHub Actions)

---
## Folder Structure:
/project-root
├── backend/                # Flask + main app code
│   ├── templates/          # Jinja2 HTML templates
│   ├── static/             # CSS, JS, assets
├── frontend/               # Tailwind + JS chart logic
│   ├── src/                # input.css, custom JS
│   ├── package.json
│   └── tailwind.config.js
|── tests/                  # pytest test files
├── Dockerfile              # Multi-stage build (Tailwind → Python)
├── requirements.txt
├── README.md
└── docker-compose.yml  

---
## Contributing:
- Contributions welcome!
- Report issues or request features via GitHub Issues
- Fork, develop, and create PRs


