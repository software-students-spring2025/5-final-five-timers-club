from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
    UserMixin,
)
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()

auth_bp = Blueprint("auth", __name__)

# mongo setup to store user's info
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["emotion_playlist"]
users_coll = db["users"]


# Flask-Login user class
class User(UserMixin):
    def __init__(self, user_dict):
        self.id = str(user_dict["_id"])
        self.username = user_dict["username"]

    @staticmethod
    def get(user_id):
        u = users_coll.find_one({"_id": ObjectId(user_id)})
        return User(u) if u else None

    @staticmethod
    def find_by_username(username):
        u = users_coll.find_one({"username": username})
        return User(u) if u else None


# routes
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if users_coll.find_one({"username": username}):
            flash("Username already taken", "warning")
            return redirect(url_for("auth.register"))
        users_coll.insert_one(
            {"username": username, "password_hash": generate_password_hash(password)}
        )
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        u = users_coll.find_one({"username": username})
        if u and check_password_hash(u["password_hash"], password):
            user = User(u)
            login_user(user)
            return redirect(url_for("home"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
