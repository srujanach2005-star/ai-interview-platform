from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager
from auth import register_user, login_user
from database import init_db
import sqlite3
import random
import subprocess
import tempfile
from flask import redirect




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



# get_random_promblem
@app.route("/get_random_problem")
def get_random_problem():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT id, title, description FROM problems")
    problems = cur.fetchall()

    conn.close()

    if not problems:
        return jsonify({"error": "No problems found"})

    problem = random.choice(problems)

    return jsonify({
        "id": problem[0],
        "title": problem[1],
        "description": problem[2]
    })


# Coding Assessment Page
@app.route("/coding_assessment")
def coding_assessment():
    return render_template("coding_editor.html")


@app.route("/video_interview")
def video_interview():
    return render_template("video_interview.html")


@app.route("/results")
def results():
    return "Interview Results Page"


# ===============================
# ADMIN PANEL ROUTES
# ===============================

@app.route("/admin_dashboard")
def admin_dashboard():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # total candidates
    cur.execute("SELECT COUNT(*) FROM users WHERE role='candidate'")
    total_candidates = cur.fetchone()[0]

    # coding tests attempted
    cur.execute("SELECT COUNT(*) FROM submissions")
    coding_tests = cur.fetchone()[0]

    # ai interviews attended
    cur.execute("SELECT COUNT(*) FROM interviews")
    ai_interviews = cur.fetchone()[0]

    # selected candidates
    cur.execute("SELECT COUNT(*) FROM interviews WHERE status='Selected'")
    selected_candidates = cur.fetchone()[0]

    # recent candidates
    cur.execute("""
    SELECT 
        users.name,
        users.email,
        COALESCE(submissions.score,0),
        COALESCE(interviews.score,0),
        COALESCE(interviews.status,'Pending')
    FROM users
    LEFT JOIN submissions ON users.id=submissions.user_id
    LEFT JOIN interviews ON users.id=interviews.candidate_id
    WHERE users.role='candidate'
    ORDER BY users.id DESC LIMIT 5
    """)

    candidates = cur.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_candidates=total_candidates,
        coding_tests=coding_tests,
        ai_interviews=ai_interviews,
        selected_candidates=selected_candidates,
        candidates=candidates
    )


# View Candidates
@app.route("/admin_candidates")
def admin_candidates():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # show all users with roles
    cur.execute("SELECT id,name,email,role FROM users")
    candidates = cur.fetchall()

    conn.close()

    return render_template("admin_candidates.html", candidates=candidates)


# Delete User
@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return redirect("/admin_candidates")

# role updated
@app.route("/update_role/<int:user_id>", methods=["POST"])
def update_role(user_id):

    data = request.json
    role = data["role"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Role Updated Successfully"})

# Coding Judge Admin Page
@app.route("/admin_coding_judge")
def admin_coding_judge():
    return render_template("admin_coding_judge.html")

@app.route("/add_problem", methods=["POST"])
def add_problem():

    data = request.json

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # insert problem
    cur.execute(
        "INSERT INTO problems (title, description) VALUES (?, ?)",
        (data["title"], data["description"])
    )

    problem_id = cur.lastrowid

    # insert 5 hidden testcases
    testcases = [
        (problem_id, data["input1"], data["output1"]),
        (problem_id, data["input2"], data["output2"]),
        (problem_id, data["input3"], data["output3"]),
        (problem_id, data["input4"], data["output4"]),
        (problem_id, data["input5"], data["output5"])
    ]

    cur.executemany(
        "INSERT INTO testcases (problem_id, input, output) VALUES (?, ?, ?)",
        testcases
    )

    conn.commit()
    conn.close()

    return jsonify({"msg": "Problem added successfully"})





# add problemstosee

@app.route("/admin_problems")
def admin_problems():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT id, title, description FROM problems")
    problems = cur.fetchall()

    conn.close()

    return render_template("admin_problems.html", problems=problems)
# Delete Problem
  # add this at the top if not already

@app.route("/delete_problem/<int:problem_id>")
def delete_problem(problem_id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # delete testcases first (important)
    cur.execute("DELETE FROM testcases WHERE problem_id=?", (problem_id,))
    
    # delete problem
    cur.execute("DELETE FROM problems WHERE id=?", (problem_id,))

    conn.commit()
    conn.close()

    return redirect("/admin_problems")

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




# run_code
@app.route("/run_code", methods=["POST"])
def run_code():

    data = request.json
    code = data["code"]
    problem_id = data["problem_id"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # take only first testcase for RUN
    cur.execute(
        "SELECT input, output FROM testcases WHERE problem_id=? LIMIT 1",
        (problem_id,)
    )
    testcase = cur.fetchone()

    conn.close()

    inp, expected = testcase

    try:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(code.encode())
            filename = f.name

        process = subprocess.run(
            ["python", filename],
            input=inp,
            text=True,
            capture_output=True,
            timeout=5
        )

        # 🔴 SHOW ERRORS IF EXIST
        if process.stderr:
            return jsonify({"console": process.stderr})

        # ✅ NORMAL OUTPUT
        output = process.stdout.strip()

        console = f"""Input: {inp}
Expected: {expected}
Your Output: {output}
"""

        return jsonify({"console": console})

    except Exception as e:
        return jsonify({"console": str(e)})
    





    # sumbit_code
@app.route("/submit_code", methods=["POST"])
def submit_code():

    data = request.json
    code = data["code"]
    problem_id = data["problem_id"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT input, output FROM testcases WHERE problem_id=?", (problem_id,))
    testcases = cur.fetchall()

    conn.close()

    score = 0
    results = []   # ⭐ THIS WAS MISSING

    for inp, expected in testcases:

        try:

            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                f.write(code.encode())
                filename = f.name

            process = subprocess.run(
                ["python", filename],
                input=inp,
                text=True,
                capture_output=True,
                timeout=3
            )

            output = process.stdout.strip()

            if output == expected:
                score += 1
                results.append("PASS")
            else:
                results.append("FAIL")

        except:
            results.append("FAIL")

    return jsonify({
        "score": score,
        "results": results
    })

if __name__ == "__main__":
    app.run(debug=True)