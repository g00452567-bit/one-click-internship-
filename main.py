
import re
import sqlite3
import hashlib
import secrets

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import get_connection, create_table


app = FastAPI(title="One Click Internship API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

create_table()


# ---------------- MODELS ----------------

class StudentRegistration(BaseModel):
    name: str
    email: str
    phone: str
    college: str
    course: str
    year: str
    skills: str
    password: str


class StudentLogin(BaseModel):
    email: str
    password: str


class InternshipCreate(BaseModel):
    title: str
    company: str
    description: str
    skills: str
    apply_url: str


# ---------------- PASSWORD SECURITY ----------------

def hash_password(password):
    salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        200000
    ).hex()

    return salt + ":" + hashed


def verify_password(password, stored_hash):
    salt, original_hash = stored_hash.split(":", 1)

    new_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        200000
    ).hex()

    return secrets.compare_digest(new_hash, original_hash)


# ---------------- SKILL MATCHING ----------------

def normalize_skill(skill):
    skill = skill.strip().lower()
    skill = re.sub(r"[_-]+", " ", skill)
    skill = re.sub(r"\s+", " ", skill)
    return skill


def get_skill_set(skills):
    if not skills:
        return set()

    parts = re.split(r"[,;\n|]+", skills)

    return {
        normalize_skill(skill)
        for skill in parts
        if normalize_skill(skill)
    }


def find_matching_skills(student_skills, internship_skills):
    student_set = get_skill_set(student_skills)
    internship_set = get_skill_set(internship_skills)

    return sorted(student_set.intersection(internship_set))


# ---------------- NOTIFICATION SYSTEM ----------------

def create_student_notifications(connection, email, student_skills):

    internships = connection.execute(
        "SELECT * FROM internships"
    ).fetchall()

    notification_count = 0

    for internship in internships:

        matched = find_matching_skills(
            student_skills,
            internship["skills"]
        )

        if matched:

            message = (
                f"New internship: {internship['title']} at "
                f"{internship['company']}. "
                f"Matching skills: {', '.join(matched)}"
            )

            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO notifications
                (student_email, internship_id, message)
                VALUES (?, ?, ?)
                """,
                (email, internship["id"], message)
            )

            notification_count += cursor.rowcount

    return notification_count


def create_internship_notifications(connection, internship):

    students = connection.execute(
        "SELECT email, skills FROM students"
    ).fetchall()

    notification_count = 0

    for student in students:

        matched = find_matching_skills(
            student["skills"],
            internship["skills"]
        )

        if matched:

            message = (
                f"New internship: {internship['title']} at "
                f"{internship['company']}. "
                f"Matching skills: {', '.join(matched)}"
            )

            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO notifications
                (student_email, internship_id, message)
                VALUES (?, ?, ?)
                """,
                (student["email"], internship["id"], message)
            )

            notification_count += cursor.rowcount

    return notification_count


# ---------------- HOME ----------------

@app.get("/")
def home():
    return {
        "message": "One Click Internship Backend is Running!"
    }


@app.get("/health")
def health():
    return {
        "status": "success",
        "message": "Backend is working"
    }


# ---------------- REGISTRATION ----------------

@app.post("/register", status_code=201)
def register_student(student: StudentRegistration):

    if not re.fullmatch(r"\d{10}", student.phone):
        raise HTTPException(
            status_code=400,
            detail="Enter a valid 10-digit phone number"
        )

    if len(student.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters"
        )

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO students
            (name, email, phone, college, course, year,
             skills, password_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student.name,
                student.email,
                student.phone,
                student.college,
                student.course,
                student.year,
                student.skills,
                hash_password(student.password)
            )
        )

        # Find existing internships matching the new student
        notification_count = create_student_notifications(
            connection,
            student.email,
            student.skills
        )

        connection.commit()

        return {
            "status": "success",
            "message": "Student registered successfully!",
            "matching_notifications": notification_count
        }

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="This email is already registered"
        )

    finally:
        connection.close()


# ---------------- LOGIN ----------------

@app.post("/login")
def login_student(student: StudentLogin):

    connection = get_connection()

    try:

        user = connection.execute(
            "SELECT * FROM students WHERE email = ?",
            (student.email,)
        ).fetchone()

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Account not found. Please register first."
            )

        if not verify_password(
            student.password,
            user["password_hash"]
        ):
            raise HTTPException(
                status_code=401,
                detail="Incorrect password!"
            )

        return {
            "status": "success",
            "message": "Login successful!",
            "name": user["name"],
            "email": user["email"],
            "skills": user["skills"]
        }

    finally:
        connection.close()


# ---------------- ADD INTERNSHIP ----------------

@app.post("/internships", status_code=201)
def add_internship(internship: InternshipCreate):

    if not internship.apply_url.startswith(("https://", "http://")):
        raise HTTPException(
            status_code=400,
            detail="Enter a valid HTTP or HTTPS application URL"
        )

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            INSERT INTO internships
            (title, company, description, skills, apply_url)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                internship.title,
                internship.company,
                internship.description,
                internship.skills,
                internship.apply_url
            )
        )

        internship_id = cursor.lastrowid

        saved_internship = connection.execute(
            "SELECT * FROM internships WHERE id = ?",
            (internship_id,)
        ).fetchone()

        # Automatically notify matching students
        notification_count = create_internship_notifications(
            connection,
            saved_internship
        )

        connection.commit()

        return {
            "status": "success",
            "message": "Internship added successfully!",
            "internship_id": internship_id,
            "students_notified": notification_count
        }

    finally:
        connection.close()


# ---------------- VIEW INTERNSHIPS ----------------

@app.get("/internships")
def get_internships(student_email: str = None):

    connection = get_connection()

    try:

        internships = connection.execute(
            "SELECT * FROM internships ORDER BY id DESC"
        ).fetchall()

        result = []

        student_skills = None

        if student_email:

            student = connection.execute(
                "SELECT skills FROM students WHERE email = ?",
                (student_email,)
            ).fetchone()

            if student is None:
                raise HTTPException(
                    status_code=404,
                    detail="Student not found"
                )

            student_skills = student["skills"]

        for internship in internships:

            matched = []

            if student_skills is not None:

                matched = find_matching_skills(
                    student_skills,
                    internship["skills"]
                )

                # Only show matching internships to the student
                if not matched:
                    continue

            result.append({
                "id": internship["id"],
                "title": internship["title"],
                "company": internship["company"],
                "description": internship["description"],
                "skills": internship["skills"],
                "matched_skills": matched,
                "apply_url": internship["apply_url"]
            })

        return {
            "status": "success",
            "count": len(result),
            "internships": result
        }

    finally:
        connection.close()


# ---------------- STUDENT NOTIFICATIONS ----------------

@app.get("/students/{email}/notifications")
def get_student_notifications(email: str):

    connection = get_connection()

    try:

        student = connection.execute(
            "SELECT email FROM students WHERE email = ?",
            (email,)
        ).fetchone()

        if student is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

        notifications = connection.execute(
            """
            SELECT
                n.id,
                n.message,
                n.is_read,
                n.created_at,
                i.title,
                i.company,
                i.apply_url,
                i.skills
            FROM notifications n
            JOIN internships i
            ON n.internship_id = i.id
            WHERE n.student_email = ?
            ORDER BY n.id DESC
            """,
            (email,)
        ).fetchall()

        return {
            "status": "success",
            "count": len(notifications),
            "notifications": [dict(item) for item in notifications]
        }

    finally:
        connection.close()


# ---------------- MARK NOTIFICATION AS READ ----------------

@app.patch("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, email: str):

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            UPDATE notifications
            SET is_read = 1
            WHERE id = ? AND student_email = ?
            """,
            (notification_id, email)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Notification not found"
            )

        connection.commit()

        return {
            "status": "success",
            "message": "Notification marked as read"
        }

    finally:
        connection.close()
