from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, DateField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Optional, Length
from datetime import date, timedelta


def validate_date_of_birth(form, field):
    if field.data:
        today = date.today()
        max_age = 150  # Maximum reasonable age
        min_date = today - timedelta(days=max_age * 365)

        # Check if date is in the future
        if field.data > today:
            raise ValidationError(
                "Date of birth cannot be in the future. Please check the year."
            )

        # Check if date is too far in the past (older than 150 years)
        if field.data < min_date:
            raise ValidationError(
                f"Date of birth seems too old (over {max_age} years). Please verify the year."
            )


class PatientForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    date_of_birth = DateField(
        "Date of Birth", validators=[Optional(), validate_date_of_birth]
    )
    submit = SubmitField("Save")


class ImportPatientsForm(FlaskForm):
    file = FileField(
        "Excel File",
        validators=[
            FileRequired(),
            FileAllowed(["xlsx", "xls"], "Only Excel files (.xlsx, .xls) are allowed!"),
        ],
    )
    submit = SubmitField("Import Patients")
