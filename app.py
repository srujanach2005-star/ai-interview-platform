from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager
from auth import register_user, login_user
from database import init_db
import sqlite3

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "supersecretkey"
jwt = JWTManager(app)

init_db()


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/register_page")
def register_page():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    return register_user(data)


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    return login_user(data)


# DASHBOARD PAGE
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# interview
@app.route("/coding_editor")
def coding_editor():
    return render_template("coding_editor.html")


@app.route("/video_interview")
def video_interview():
    return render_template("video_interview.html")


@app.route("/results")
def results():
    return "Interview Results Page"


# ===============================
# ADMIN PANEL ROUTES (ADDED)
# ===============================

# Admin Dashboard
@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")


# View Candidates
@app.route("/admin_candidates")
def admin_candidates():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE role='user'")
    users = cur.fetchall()

    conn.close()

    return render_template("admin_candidates.html", users=users)


# Delete User
@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "User deleted"})


# Coding Judge Admin Page
@app.route("/admin_coding_judge")
def admin_coding_judge():
    return render_template("admin_coding_judge.html")


# Add Problem
@app.route("/add_problem", methods=["POST"])
def add_problem():

    data = request.json

    title = data.get("title")
    description = data.get("description")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO problems (title, description) VALUES (?, ?)",
        (title, description)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Problem added successfully"})


# Delete Problem
@app.route("/delete_problem/<int:problem_id>")
def delete_problem(problem_id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM problems WHERE id=?", (problem_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Problem deleted"})


# Admin AI Interviews Page
@app.route("/admin_ai_interviews")
def admin_ai_interviews():
    return render_template("admin_ai_interviews.html")


# Admin Results Page
@app.route("/admin_results")
def admin_results():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM interviews")
    results = cur.fetchall()

    conn.close()

    return render_template("admin_results.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)