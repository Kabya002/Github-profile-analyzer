# 🔍 GitHub Profile Analyzer

A visually engaging web app built with **Flask**, **Tailwind CSS**, and **SwiperJS** that analyzes any public GitHub profile and presents the data with modern UI sections including a hero section, feature carousel, creator info, and contact form.

---

## 🌐 Live Demo

🚀 Deployed soon! Stay tuned.

---

## 📸 Features

- 🎯 **Hero Section**: Clean call-to-action with search bar to fetch GitHub user data.
- 🎠 **Carousel Slider**: Swiper-powered full-screen slider showcasing app features with image overlays.
- 🧑‍💻 **Meet the Creator**: Zoom-on-hover profile card with creator details.
- 📬 **Contact Form**: Dark semi-transparent form UI with custom "Send Message" button.
- 🌙 **Dark Mode Toggle**: Switch between light and dark themes.
- 📱 **Responsive Layout**: Works smoothly across all devices.
- 📌 **Sticky Navbar**: Hides on scroll down, shows on scroll up.
- ⬆️ **Back to Top Button**: Fixed-position floating circle button for scrolling to top.

---

## 🛠️ Tech Stack

| Layer         | Tools Used                        |
|---------------|------------------------------------|
| Frontend      | Tailwind CSS, SwiperJS, Font Awesome |
| Backend       | Flask (Python)                     |
| Template Engine | Jinja2                          |
| Hosting       | Coming soon…                       |

---

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

```bash
git clone https://github.com/yourusername/github-profile-analyzer.git
cd github-profile-analyzer
2. Set Up Virtual Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
3. Install Requirements
bash
Copy
Edit
pip install -r requirements.txt
4. Run the App
flask run

The app will be available at http://127.0.0.1:5000/.
You can extend with @keyframes in Tailwind config for more custom effects.

🧠 Credits
Developed with ❤️ by Kabyashree Gogoi

Inspired by UI principles from Boomerang, SwiperJS, and modern Tailwind UI kits

📜 License
This project is licensed under the MIT License.

🤝 Contributions
PRs are welcome! For major changes, please open an issue first to discuss what you would like to change.