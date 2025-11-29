from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class VisitForm(FlaskForm):
    clinician = StringField("Clinician", validators=[Optional(), Length(max=120)])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Save")


class DiagnosisForm(FlaskForm):
    code = StringField("Code", validators=[Optional(), Length(max=20)])
    description = StringField(
        "Description", validators=[DataRequired(), Length(max=255)]
    )
    submit = SubmitField("Add")
