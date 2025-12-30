# 🎓 Real-Time Attendance Marking Using Facial Recognition

<div align="center">

![Face Recognition](https://img.shields.io/badge/Face%20Recognition-CNN%20%2B%20FaceNet-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-green?style=for-the-badge&logo=python)
![Next.js](https://img.shields.io/badge/Next.js-15.5-black?style=for-the-badge&logo=next.js)
![Flask](https://img.shields.io/badge/Flask-3.0-orange?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A cutting-edge, real-time attendance management system powered by advanced deep learning facial recognition technology.**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Tech Stack](#-tech-stack) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Demo](#-demo)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🌟 Overview

The **Real-Time Attendance Marking System** revolutionizes traditional attendance tracking by leveraging state-of-the-art facial recognition technology. Built with a modern tech stack, this system provides:

- ⚡ **Real-time face detection and recognition** using CNN and FaceNet models
- 🎯 **High accuracy** with advanced deep learning algorithms
- 📊 **Comprehensive dashboard** for attendance management
- 🔐 **Secure authentication** for teachers and administrators
- 📱 **Responsive UI** that works seamlessly across devices
- 📈 **Analytics and reporting** with Excel export functionality

Perfect for educational institutions, corporate offices, and any organization requiring efficient attendance management!

---

## ✨ Features

### 🎯 Core Features

- **Real-Time Face Recognition**
  - Live camera feed with instant face detection
  - Multi-face detection and recognition
  - Automatic attendance marking upon recognition
  - High-precision CNN-based facial recognition

- **Student Management**
  - Easy student registration with photo capture
  - Bulk student data import/export
  - Student profile management
  - Face embedding storage and training

- **Attendance Tracking**
  - Real-time attendance sessions
  - Historical attendance records
  - Date-wise attendance filtering
  - Excel report generation

- **Teacher Dashboard**
  - Session management (start/stop attendance sessions)
  - Live attendance monitoring
  - Student attendance statistics
  - Export attendance reports

- **Admin Panel**
  - User management (teachers and students)
  - System configuration
  - Database management
  - Analytics and insights

### 🔒 Security Features

- Secure password hashing with bcrypt
- JWT-based authentication
- Role-based access control (Teacher/Admin)
- Protected API endpoints

### 📊 Analytics & Reporting

- Attendance percentage calculations
- Date-range based reports
- Excel export functionality
- Visual attendance statistics

---

## 🎬 Demo

### Screenshots

> *Add your screenshots here showing:*
> - Login page
> - Student registration
> - Live attendance marking
> - Dashboard
> - Reports

### Live Demo

> *Add your deployed application link here if available*

---

## 🛠 Tech Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| **Next.js 15.5** | React framework for production |
| **React 19** | UI library |
| **TypeScript** | Type-safe JavaScript |
| **Tailwind CSS 4** | Utility-first CSS framework |
| **Framer Motion** | Animation library |
| **Socket.IO Client** | Real-time communication |
| **Lucide React** | Beautiful icon library |
| **XLSX** | Excel file handling |

### Backend

| Technology | Purpose |
|------------|---------|
| **Flask 3.0** | Python web framework |
| **PyTorch 2.5** | Deep learning framework |
| **FaceNet-PyTorch** | Face recognition model |
| **OpenCV** | Computer vision library |
| **NumPy** | Numerical computing |
| **scikit-learn** | Machine learning utilities |
| **Flask-CORS** | Cross-origin resource sharing |
| **Flask-Bcrypt** | Password hashing |
| **Pillow** | Image processing |

### Database

- **JSON-based storage** (Local development)
- **MongoDB support** (Production-ready)

---

## 🏗 System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Dashboard  │  │   Students   │  │  Attendance  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬───────────────────────────────────┘
                         │ REST API / WebSocket
┌────────────────────────┴──────────────────────────────────┐
│                      Backend (Flask)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     Auth     │  │    Routes    │  │   Models     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌─────────────────────────────────────────────────┐      │
│  │         Face Recognition Engine                 │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │      │
│  │  │  MTCNN   │  │ FaceNet  │  │   CNN    │       │      │
│  │  │ Detector │  │ Embedder │  │Recognizer│       │      │
│  │  └──────────┘  └──────────┘  └──────────┘       │      │
│  └─────────────────────────────────────────────────┘      │
└────────────────────────┬──────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    Database Layer                           │
│              (JSON Storage / MongoDB)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **npm or yarn** (comes with Node.js)
- **Git** ([Download](https://git-scm.com/))
- **Webcam** (for face recognition)

### Step 1: Clone the Repository

```bash
git clone https://github.com/indoreshivam2006/REAL-TIME-ATTENDANCE-MARKING-USING-FACIAL-RECOGNITION-.git
cd REAL-TIME-ATTENDANCE-MARKING-USING-FACIAL-RECOGNITION-
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, for MongoDB)
# Copy .env.example to .env and configure if needed
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
# or
yarn install
```

### Step 4: Initialize Database

The system will automatically create necessary directories and files on first run. The database structure includes:

- `backend/data/storage/` - JSON database files
- `backend/models/` - Trained face recognition models
- `backend/uploads/` - Student photos

---

## 🎮 Usage

### Starting the Application

#### 1. Start the Backend Server

```bash
# From the backend directory
cd backend
python app.py
```

The backend server will start on `http://localhost:5000`

#### 2. Start the Frontend Development Server

```bash
# From the frontend directory (in a new terminal)
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

### First-Time Setup

1. **Access the Application**
   - Open your browser and navigate to `http://localhost:3000`

2. **Login as Admin/Teacher**
   - Use default credentials (if configured) or create a new teacher account

3. **Register Students**
   - Navigate to the Students section
   - Click "Add Student"
   - Fill in student details and capture face photo
   - The system will automatically train the recognition model

4. **Start Attendance Session**
   - Go to the Attendance section
   - Click "Start Session"
   - Allow camera access
   - Students will be automatically recognized and marked present

5. **View Reports**
   - Navigate to Reports section
   - Filter by date range
   - Export to Excel if needed

---

## 📚 API Documentation

### Base URL

```
http://localhost:5000/api
```

### Authentication Endpoints

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "teacher@example.com",
  "password": "password123"
}
```

### Student Endpoints

#### Get All Students
```http
GET /api/students
Authorization: Bearer <token>
```

#### Register Student
```http
POST /api/students/register
Content-Type: multipart/form-data

{
  "name": "Shivam Indore",
  "rollNumber": "JLU07986",
  "email": "shivamindore@gmail.com",
  "photo": <file>
}
```

### Attendance Endpoints

#### Start Session
```http
POST /api/attendance/session/start
Authorization: Bearer <token>
```

#### Mark Attendance
```http
POST /api/attendance/mark
Content-Type: application/json

{
  "sessionId": "session_123",
  "studentId": "student_456"
}
```

#### Get Attendance Report
```http
GET /api/attendance/report?startDate=2024-01-01&endDate=2024-12-31
Authorization: Bearer <token>
```

---

## 📁 Project Structure

```
REAL-TIME-ATTENDANCE-MARKING-USING-FACIAL-RECOGNITION/
├── backend/
│   ├── app.py                      # Flask application entry point
│   ├── config.py                   # Configuration settings
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (not in repo)
│   ├── data/
│   │   └── storage/               # JSON database files (gitignored)
│   ├── face_recognition/
│   │   ├── cnn_recognizer.py      # CNN-based face recognition
│   │   ├── detector.py            # Face detection logic
│   │   ├── facenet_model.py       # FaceNet implementation
│   │   ├── mtcnn_detector.py      # MTCNN face detector
│   │   └── recognizer.py          # Recognition coordinator
│   ├── models/
│   │   ├── attendance.py          # Attendance model
│   │   ├── database.py            # Database operations
│   │   ├── student.py             # Student model
│   │   ├── teacher.py             # Teacher model
│   │   └── weights/               # Model weights (gitignored)
│   └── routes/
│       ├── auth.py                # Authentication routes
│       ├── students.py            # Student management routes
│       ├── attendance.py          # Attendance routes
│       └── admin.py               # Admin routes
├── frontend/
│   ├── app/
│   │   ├── page.tsx               # Home page
│   │   ├── layout.tsx             # Root layout
│   │   ├── dashboard/             # Dashboard pages
│   │   ├── students/              # Student management pages
│   │   └── attendance/            # Attendance pages
│   ├── public/                    # Static assets
│   ├── types/                     # TypeScript type definitions
│   ├── package.json               # Node dependencies
│   ├── tsconfig.json              # TypeScript configuration
│   ├── tailwind.config.js         # Tailwind CSS configuration
│   └── next.config.ts             # Next.js configuration
├── .gitignore                     # Git ignore rules
├── LICENSE                        # MIT License
└── README.md                      # This file
```

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**!

### How to Contribute

1. **Fork the Project**
   ```bash
   # Click the 'Fork' button at the top right of this page
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/your-username/REAL-TIME-ATTENDANCE-MARKING-USING-FACIAL-RECOGNITION-.git
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```

4. **Make Your Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests if applicable

5. **Commit Your Changes**
   ```bash
   git commit -m "Add some AmazingFeature"
   ```

6. **Push to Your Branch**
   ```bash
   git push origin feature/AmazingFeature
   ```

7. **Open a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Describe your changes in detail

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Use ESLint and Prettier for JavaScript/TypeScript
- Write meaningful commit messages
- Update documentation for new features
- Add comments for complex logic

---

## 🐛 Known Issues & Roadmap

### Known Issues

- [ ] Camera access may require HTTPS in production
- [ ] Large batch student registration may take time for model training

### Roadmap

- [ ] Mobile application (React Native)
- [ ] Multi-camera support
- [ ] Cloud deployment guide
- [ ] Docker containerization
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] SMS integration
- [ ] Biometric integration (fingerprint backup)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Shivam Indore, Abhay Dwivedi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 👨‍💻 Contact

**Shivam Indore**
- GitHub: [@indoreshivam2006](https://github.com/indoreshivam2006)
- Project Link: [https://github.com/indoreshivam2006/REAL-TIME-ATTENDANCE-MARKING-USING-FACIAL-RECOGNITION-](https://github.com/indoreshivam2006/REAL-TIME-ATTENDANCE-MARKING-USING-FACIAL-RECOGNITION-)

---

## 🙏 Acknowledgments

- [FaceNet-PyTorch](https://github.com/timesler/facenet-pytorch) for the face recognition model
- [Next.js](https://nextjs.org/) for the amazing React framework
- [Flask](https://flask.palletsprojects.com/) for the lightweight backend framework
- [OpenCV](https://opencv.org/) for computer vision capabilities
- All contributors who help improve this project

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by [Shivam Indore](https://github.com/indoreshivam2006).

</div>
