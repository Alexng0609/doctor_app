from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from doctor_app import db, login_manager
from doctor_app.models import User
from doctor_app.auth.forms import (
    LoginForm,
    RegisterForm,
    EditUserForm,
    ChangePasswordForm,
    CreateAssistantForm,
    EditAssistantForm,
)
from functools import wraps

bp = Blueprint("auth", __name__)


# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("You need admin privileges to access this page", "danger")
            return redirect(url_for("patients.list_patients"))
        return f(*args, **kwargs)

    return decorated_function


# Doctor required decorator (for assistant management)
def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_doctor():
            flash("Only doctors can access this page", "danger")
            return redirect(url_for("patients.list_patients"))
        return f(*args, **kwargs)

    return decorated_function


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
            if not user.is_active:
                flash(
                    "Your account has been deactivated. Please contact an administrator.",
                    "danger",
                )
                return render_template("auth/login.html", form=form)
            login_user(user)

            # Show different messages based on role
            if user.is_assistant():
                flash(f"✅ Welcome back, {user.full_name}!", "success")
                flash(f"ℹ️ You're working under {user.doctor.full_name}", "info")
            elif user.is_doctor():
                flash(f"✅ Welcome back, Dr. {user.full_name}!", "success")
            else:
                flash(f"✅ Welcome back, {user.full_name}!", "success")

            next_page = request.args.get("next")
            return (
                redirect(next_page)
                if next_page
                else redirect(url_for("patients.list_patients"))
            )
        flash("Invalid username or password", "danger")
    return render_template("auth/login.html", form=form)


# Logout
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully", "success")
    return redirect(url_for("auth.login"))


# Register new user (admin only - creates doctors)
@bp.route("/register", methods=["GET", "POST"])
@login_required
@admin_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if username already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists", "danger")
            return render_template("auth/register.html", form=form)

        user = User(
            username=form.username.data,
            full_name=form.full_name.data,
            email=form.email.data,
            location=form.location.data,
            role=form.role.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"User {user.username} created successfully", "success")
        return redirect(url_for("auth.list_users"))
    return render_template("auth/register.html", form=form)


# Create assistant (doctor only)
@bp.route("/assistants/create", methods=["GET", "POST"])
@login_required
@doctor_required
def create_assistant():
    form = CreateAssistantForm()
    if form.validate_on_submit():
        # Create assistant account
        assistant = User(
            username=form.username.data,
            full_name=form.full_name.data,
            email=form.email.data,
            role="assistant",
            doctor_id=current_user.id,  # Link to current doctor
            location=current_user.location,  # Inherit doctor's location
            is_active=True,
        )
        assistant.set_password(form.password.data)
        db.session.add(assistant)
        db.session.commit()
        flash(f"✅ Assistant '{assistant.username}' created successfully", "success")
        return redirect(url_for("auth.my_assistants"))

    return render_template("auth/create_assistant.html", form=form)


# List my assistants (doctor only)
@bp.route("/assistants")
@login_required
@doctor_required
def my_assistants():
    assistants = current_user.assistants.order_by(User.created_at.desc()).all()

    # Get patient counts for each assistant
    assistant_data = []
    for assistant in assistants:
        patient_count = len(assistant.patients)  # ← USE len() INSTEAD
        assistant_data.append({"assistant": assistant, "patient_count": patient_count})

    return render_template("auth/my_assistants.html", assistant_data=assistant_data)


# Edit assistant (doctor only - can only edit their own assistants)
@bp.route("/assistants/<int:assistant_id>/edit", methods=["GET", "POST"])
@login_required
@doctor_required
def edit_assistant(assistant_id):
    assistant = User.query.get_or_404(assistant_id)

    # Make sure this assistant belongs to current doctor
    if assistant.doctor_id != current_user.id:
        flash("You can only edit your own assistants", "danger")
        return redirect(url_for("auth.my_assistants"))

    form = EditAssistantForm(obj=assistant)

    if form.validate_on_submit():
        # Check if username is taken by another user
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != assistant.id:
            flash("Username already exists", "danger")
            return render_template(
                "auth/edit_assistant.html", form=form, assistant=assistant
            )

        assistant.username = form.username.data
        assistant.full_name = form.full_name.data
        assistant.email = form.email.data
        assistant.is_active = form.is_active.data

        db.session.commit()
        flash(f"✅ Assistant '{assistant.username}' updated successfully", "success")
        return redirect(url_for("auth.my_assistants"))

    return render_template("auth/edit_assistant.html", form=form, assistant=assistant)


# Delete assistant (doctor only)
@bp.route("/assistants/<int:assistant_id>/delete", methods=["POST"])
@login_required
@doctor_required
def delete_assistant(assistant_id):
    assistant = User.query.get_or_404(assistant_id)

    # Make sure this assistant belongs to current doctor
    if assistant.doctor_id != current_user.id:
        flash("You can only delete your own assistants", "danger")
        return redirect(url_for("auth.my_assistants"))

    # Check if assistant has patients
    patient_count = assistant.patients.count()
    if patient_count > 0:
        flash(
            f"❌ Cannot delete assistant '{assistant.username}': "
            f"They have {patient_count} patient(s) assigned. "
            f"Please reassign patients first.",
            "danger",
        )
        return redirect(url_for("auth.my_assistants"))

    username = assistant.username
    db.session.delete(assistant)
    db.session.commit()
    flash(f"✅ Assistant '{username}' deleted successfully", "success")
    return redirect(url_for("auth.my_assistants"))


# List all users (admin only)
@bp.route("/users")
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("auth/users.html", users=users)


# Edit user (admin only)
@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        # Check if username is taken by another user
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != user.id:
            flash("Username already exists", "danger")
            return render_template("auth/edit_user.html", form=form, user=user)

        user.username = form.username.data
        user.full_name = form.full_name.data
        user.email = form.email.data
        user.location = form.location.data
        user.role = form.role.data
        user.is_active = form.is_active.data

        db.session.commit()
        flash(f"User {user.username} updated successfully", "success")
        return redirect(url_for("auth.list_users"))

    return render_template("auth/edit_user.html", form=form, user=user)


# Quick update location (admin only)
@bp.route("/users/<int:user_id>/update-location", methods=["POST"])
@login_required
@admin_required
def update_location(user_id):
    user = User.query.get_or_404(user_id)
    location = request.form.get("location", "").strip()

    user.location = location if location else None
    db.session.commit()

    flash(f"Location updated for {user.username}", "success")
    return redirect(url_for("auth.list_users"))


# Change own password
@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect", "danger")
            return render_template("auth/change_password.html", form=form)

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Password changed successfully", "success")
        return redirect(url_for("patients.list_patients"))

    return render_template("auth/change_password.html", form=form)


# Delete user (admin only)
@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent deleting yourself
    if user.id == current_user.id:
        flash("You cannot delete your own account", "danger")
        return redirect(url_for("auth.list_users"))

    # Prevent deleting the last admin
    if user.is_admin():
        admin_count = User.query.filter_by(role="admin").count()
        if admin_count <= 1:
            flash("Cannot delete the last admin user", "danger")
            return redirect(url_for("auth.list_users"))

    # Check if doctor has assistants
    if user.is_doctor():
        assistant_count = user.assistants.count()
        if assistant_count > 0:
            flash(
                f"❌ Cannot delete doctor '{user.username}': "
                f"They have {assistant_count} assistant(s). "
                f"Please delete or reassign assistants first.",
                "danger",
            )
            return redirect(url_for("auth.list_users"))

    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f"User {username} deleted successfully", "success")
    return redirect(url_for("auth.list_users"))
