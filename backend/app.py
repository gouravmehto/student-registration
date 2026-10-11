from flask import Flask, request, redirect, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def create_table():
    conn = sqlite3.connect("students.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            course TEXT,
            gender TEXT,
            skills TEXT,
            file_name TEXT
        )
    """)
    conn.commit()
    conn.close()

create_table()

@app.route("/")
def home():
    return open("../frontend/form.html").read()

@app.route("/save", methods=["POST"])
def save():
    name = request.form.get("name", "").strip()
    course = request.form.get("course", "")
    gender = request.form.get("gender", "")
    skills = ", ".join(request.form.getlist("skills"))

    uploaded_file = request.files.get("file")
    file_name = ""
    if uploaded_file and uploaded_file.filename:
        file_name = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(UPLOAD_FOLDER, file_name))

    conn = sqlite3.connect("students.db")
    conn.execute("INSERT INTO students (name, course, gender, skills, file_name) VALUES (?, ?, ?, ?, ?)",
                 (name, course, gender, skills, file_name))
    conn.commit()
    conn.close()

    return redirect("/students")

@app.route("/students")
def students():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    records = conn.execute("select * from students order by id desc").fetchall()
    conn.close()


    html = open("../frontend/students.html").read()
    rows = ""
    for student in records:
        file_display = student['file_name'] if student['file_name'] else "No file"
        rows += f"<tr><td>{student['name']}</td><td>{student['course']}</td><td>{student['gender']}</td><td>{student['skills']}</td><td>{file_display}</td></tr>"
    return html.replace("{{rows}}", rows)


@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True)
