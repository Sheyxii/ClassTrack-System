# ClassTrack System

A desktop application for managing class sections, students, attendance, grades, and schedules — built with **PyQt5** and a **MySQL** database backend.

## ✨ Features

- **Login** — secure entry point into the system
- **Section Management** — create, view, and archive class sections (e.g. subject, section code, room)
- **Student Management** — add and manage student records (name, age, contact info, birthday, address) per section
- **Attendance Tracking** — record daily attendance (present/absent) per section
- **Grades** — record midterm and final grades, with automatic semestral grade computation
- **Schedules** — set up weekly class schedules with day, time, room, and color-coding
- **Archiving** — archive old/past sections without deleting historical data
- **Demo Data Setup** — a script to quickly populate the database with sample sections, students, grades, attendance, and schedules for testing

## 🛠️ Tech Stack

- **Language:** Python
- **GUI Framework:** PyQt5
- **Database:** MySQL

## 📁 Project Structure

```
ClassTrack-System/
├── app.py                   # Application entry point
├── setup_default_data.py    # Script to populate sample/demo data
├── ui/                       # PyQt5 UI windows and components
├── utils/                    # Helper modules (database connection, JSON data, etc.)
├── image/                    # App images/icons/assets
├── uploaded_resources/       # Runtime-uploaded files/resources
└── requirements.txt
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- MySQL Server (running locally or accessible remotely)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sheyxii/ClassTrack-System.git
   cd ClassTrack-System
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the MySQL database**
   - Make sure your MySQL server is running.
   - Create a database for the app.
   - Update the database connection settings (host, user, password, database name) in `utils/database.py` to match your local setup.

5. **(Optional) Populate sample data**
   ```bash
   python setup_default_data.py
   ```
   This creates sample sections (e.g. ITEC 104, CMSC 203), adds default students, generates random grades, simulates attendance records, and sets up weekly schedules — useful for testing/demo purposes.

6. **Run the application**
   ```bash
   python app.py
   ```

## 📝 Notes

- This project was built as part of a school requirement/portfolio project.
- Database credentials are **not** included in this repo — configure your own local MySQL connection before running.

## 📄 License

This project currently has no license specified. Add one (e.g. MIT) if you plan to make this publicly reusable.
