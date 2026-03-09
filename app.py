from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager
from auth import register_user, login_user
from database import init_db

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


if __name__ == "__main__":
    app.run(debug=True)