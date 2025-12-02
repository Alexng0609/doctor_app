from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    Optional,
    Length,
    EqualTo,
    ValidationError,
)
from doctor_app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")


class RegisterForm(FlaskForm):
    """Admin uses this to create doctors"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=80)]
    )
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    location = TextAreaField(
        "Location/Address", validators=[Optional(), Length(max=255)]
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    role = SelectField("Role", choices=[("doctor", "Doctor"), ("admin", "Admin")])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username already exists. Please choose a different one."
            )


class CreateAssistantForm(FlaskForm):
    """Doctors use this to create assistants"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=80)]
    )
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username already exists. Please choose a different one."
            )


class EditAssistantForm(FlaskForm):
    """Doctors use this to edit their assistants"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=80)]
    )
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    is_active = BooleanField("Active Account")


class EditUserForm(FlaskForm):
    """Admin uses this to edit any user"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=80)]
    )
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    location = TextAreaField(
        "Location/Address", validators=[Optional(), Length(max=255)]
    )
    role = SelectField(
        "Role",
        choices=[("admin", "Admin"), ("doctor", "Doctor"), ("assistant", "Assistant")],
    )
    is_active = BooleanField("Active Account")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        "Confirm New Password", validators=[DataRequired(), EqualTo("new_password")]
    )
