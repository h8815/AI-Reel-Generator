# 🎬 AI Reel Generator

<div align="center">
  <em>Transform your photos into professional video reels with AI-powered automation.</em>

  **Features • Demo • Installation • Usage • Documentation • Contributing**
</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [Contributing](#-contributing)
- [Acknowledgments](#-acknowledgments)

---

## 🌟 Overview

**AI Reel Generator** is a powerful web app that allows users to create professional-quality video reels from photos and audio files — ideal for content creators, marketers, and social media enthusiasts.

### Why Choose AI Reel Generator?

✅ No Watermarks  
✅ Full HD Output  
✅ Easy Drag & Drop Interface  
✅ Fast Processing  
✅ Free Forever  
✅ Export for Instagram, TikTok, YouTube, and more  

---

## ✨ Features

### 🎨 Core Features

#### 🖼️ Drag & Drop Upload
- Upload multiple images at once  
- Reorder easily  
- Supports JPG, JPEG, PNG  

#### 🎵 Audio Integration
- Add MP3 background music  
- Perfect sync with visuals  
- Up to 50MB audio  

#### ⚙️ Customization
- Adjustable duration (0.5–10 sec)  
- Video filters: Grayscale, Sepia 
- Text overlay & multiple aspect ratios  

#### 📐 Aspect Ratios
- **9:16** – Reels/Shorts  
- **16:9** – YouTube/Facebook  
- **1:1** – Instagram posts  

#### 💾 Gallery Management
- View, download, or delete reels  
- Metadata tracking (date, file size, settings)

---

## 🎬 Video Specifications

| Feature | Specification |
|----------|----------------|
| Resolution | Full HD (1080p) |
| Frame Rate | 30 FPS |
| Video Codec | H.264 (MP4) |
| Audio Codec | AAC |
| Max Image Size | 10MB |
| Max Audio Size | 50MB |

---

## 📦 Prerequisites
- **Python 3.9+**
- **FFmpeg**
    - Windows: Download from **[ffmpeg.org](https://ffmpeg.org/download.html)**
   - macOS: `brew install ffmpeg`
    - Linux: `sudo apt-get install ffmpeg`

---

## 🚀 Installation

```bash
# Clone repo
git clone https://github.com/h8815/AI-Reel-Generator.git
cd AI-Reel-Generator

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# OR
source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Verify FFmpeg
ffmpeg -version

# Run the app
python main.py
```

App runs at: **http://localhost:5000**

---


## 📡 API Documentation

| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | `/` | Home page |
| GET | `/create` | Create reel page |
| POST | `/create` | Create a new reel |
| GET | `/gallery` | View created reels |
| POST | `/delete/<reel_name>` | Delete specific reel |
| GET | `/about` | About page |
| GET | `/help` | Help & FAQ page |

---

## 📁 Project Structure

```
ai-reel-generator/
├── main.py                   # Main Flask application
├── generate_process.py       # Background processing script
├── requirements.txt          # Python dependencies
├── templates/                # HTML templates
├── static/                   # Static files
│   ├── css/
│   ├── reels/                # Generated reels (auto-created)
│   └── metadata/             # Reel metadata (auto-created)    
├── user_uploads/             # Uploaded files (auto-created)
└── venv/                     # Virtual environment (not in repo)
```

---

## 🛠️ Technologies Used

### Backend
- Flask 3.0+  
- FFmpeg  
- Python 3.9+  

### Frontend
- HTML5, CSS3, JS (ES6+)  
- Jinja2 Templates  

### Libraries
- `subprocess`, `uuid`, `json`, `datetime`

---

## 🤝 Contributing

### Steps
1. Fork the repo  
2. Create a branch  
3. Make & test changes  
4. Push branch  
5. Open a Pull Request  

### Guidelines
- Follow **PEP 8**  
- Use clear commit messages  
- Update docs for new features  
- Test thoroughly  

**Areas for Contribution:**  
🐛 Bug Fixes | ✨ Features | 📝 Docs | 🎨 UI/UX | 🌍 Translations | ⚡ Optimization  

---

## 🙏 Acknowledgments

- **FFmpeg** – Video processing  
- **Flask** – Web framework  
- **Google Fonts** – Typography  
- **Community** – Contributors & testers   

---

<div align="center">

Made with ❤️  
If this project helped you, please ⭐ star the repository!  

[Report Bug](#) • [Request Feature](#) • [Contribute](#)

</div>
