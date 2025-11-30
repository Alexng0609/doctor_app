from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=80)]
    )
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    role = SelectField(
        "Role", choices=[("doctor", "Doctor"), ("admin", "Admin")], default="doctor"
    )
    submit = SubmitField("Register")


class EditUserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    role = SelectField("Role", choices=[("doctor", "Doctor"), ("admin", "Admin")])
    is_active = SelectField(
        "Status",
        choices=[(True, "Active"), (False, "Inactive")],
        coerce=lambda x: x == "True",
    )
    submit = SubmitField("Update")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Change Password")
