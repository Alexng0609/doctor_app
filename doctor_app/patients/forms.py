from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class PatientForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    date_of_birth = DateField("Date of Birth", validators=[Optional()])
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
