from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from doctor_app import db, login_manager
from doctor_app.models import User
from doctor_app.auth.forms import LoginForm

bp = Blueprint("auth", __name__)


# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Root route - redirect to login or patients list
@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("patients.list_patients"))
    return redirect(url_for("auth.login"))


# Login page
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("patients.list_patients"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("patients.list_patients"))
        flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)


# Logout
@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
