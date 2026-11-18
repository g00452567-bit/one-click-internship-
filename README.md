## Live Website
https://one-click-internship.onrender.com
# One Click Internship

A Skill-Based Internship Matching Platform built using Python, FastAPI, SQLite, HTML, CSS and JavaScript.

## About the Project

One Click Internship helps students discover internship opportunities based on their skills.

Students can register, provide their skills, log in and receive notifications about matching internships.

## Key Features

- Student Registration
- Secure Password Hashing
- Student Login
- Student Dashboard
- Skill-Based Internship Matching
- Personalized Internship Notifications
- Notification Sound
- Apply Now with Original Portal Links
- Mark Notifications as Read

## How It Works

1. Students create an account.
2. Students enter their skills.
3. The backend matches student skills with internship requirements.
4. Matching internship notifications are generated.
5. Students can view matching opportunities and apply through the provided links.

## Technologies Used

| Technology | Purpose |
|---|---|
| HTML | Website Structure |
| CSS | Website Design |
| JavaScript | Frontend Functionality |
| Python | Backend |
| FastAPI | REST API |
| SQLite | Database |

## Project Structure

```text
one-click-internship/
│
├── backend/
│   ├── main.py
│   ├── db.py
│   └── internship.db
│
├── frontend/
│   ├── index.html
│   ├── register.html
│   ├── register.js
│   ├── login.html
│   ├── login.js
│   ├── dashboard.html
│   ├── notification.html
│   ├── script.js
│   └── style.css
│
└── README.md
```

## Run Locally

### 1. Install Dependencies

```bash
py -m pip install fastapi uvicorn
```

### 2. Start Backend

```bash
cd backend
py -m uvicorn main:app --reload
```

### 3. Open API Documentation

http://127.0.0.1:8000/docs

### 4. Open Frontend

Open the frontend `index.html` file in your browser.

## Current Project Status

The local demo supports student registration, login, skill matching, internship notifications and application links.

Internship opportunities are currently added through the backend API. Automatic collection from external internship portals and production deployment are future enhancements.

## Future Enhancements

- Authorized internship source integrations
- Admin dashboard
- Email notifications
- Advanced skill matching
- Online database integration
- Public website deployment

## Project Demo

Screenshots and demo video will be added here.

## Developed As

Full Stack Development Portfolio Project.
