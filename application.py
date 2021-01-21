import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, createGoogleEvent

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'todo.db')

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////" + DATABASE
db = SQLAlchemy(app)

app.config["AUTO_RELOAD_TEMPLATES"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    todo_time = db.column(db.String(80))
    complete = db.Column(db.Boolean)

@app.route("/")
@login_required
def index():

    db = SQL("sqlite:///users.db")

    rows = db.execute("""
    SELECT username FROM users WHERE id = :ide""", ide = session["user_id"])

    username = rows[0]["username"]

    return render_template("index.html", username = username)

@app.route("/login", methods = ['GET', 'POST'])
def login():
    db = SQL("sqlite:///users.db")
    session.clear()

    if request.method == "POST":

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                              username=request.form.get("username"))

        if not check_password_hash(rows[0]["password"], request.form.get("pass")):
            return "Wrong username and/or password", 403

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods = ['GET', 'POST'])
def register():
    db = SQL("sqlite:///users.db")
    if request.method == "POST":

        if request.form.get("pass") != request.form.get("confirmation pass"):
            return "Both Passwords must be same!", 403

        rows = db.execute("SELECT * FROM users")

        for row in rows:
            if request.form.get('username') == row['username'] or request.form.get('email') == row['email']:
                return "Username/Email already exists", 403

        try:
            values = db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :hash)",
                    username = request.form.get("username"), email = request.form.get("email"),hash = generate_password_hash((request.form.get("pass"))))
        except:
            return "Registration Error", 403

        session["user_id"] = values
        return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/profile")
@login_required
def profile():
    db = SQL("sqlite:///users.db")

    rows = db.execute("""
    SELECT username FROM users WHERE id = :ide""", ide = session["user_id"])

    username = rows[0]["username"]
    return render_template("profile.html", username=username)

@app.route("/home")
@login_required
def home():
    db = SQL("sqlite:///users.db")

    rows = db.execute("""
    SELECT username FROM users WHERE id = :ide""", ide = session["user_id"])

    username = rows[0]["username"]
    return render_template("home.html", username=username)

@app.route("/guides")
@login_required
def guides():
    db = SQL("sqlite:///users.db")

    rows = db.execute("""
    SELECT username FROM users WHERE id = :ide""", ide = session["user_id"])

    username = rows[0]["username"]
    return render_template("guides.html", username = username)

@app.route("/plans")
@login_required
def plans():
    db = SQL("sqlite:///users.db")

    rows = db.execute("""
    SELECT username FROM users WHERE id = :ide""", ide = session["user_id"])

    username = rows[0]["username"]
    return render_template("plans.html", username=username)





@app.route("/todo")
@login_required
def todoApp():
    db = SQL("sqlite:///todo.db")
    todo_list = db.execute("""SELECT * FROM todo""")
    return render_template("todo.html", todo_list=todo_list)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")

    db = SQL("sqlite:///todo.db")

    db.execute("""
                INSERT INTO todo (title, todo_time, complete)
                VALUES (:title, :todo_time, :complete)""",
                title=title, todo_time=str(request.form.get("time")), complete=False)
    return redirect("/todo")


@app.route("/complete/<string:todo_id>")
def complete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect("/todo")


@app.route("/delete/<string:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/todo")
