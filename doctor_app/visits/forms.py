from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Optional, Length


class DiagnosisEntryForm(FlaskForm):
    code = StringField("Code", validators=[Optional(), Length(max=20)])
    description = StringField("Description", validators=[Optional(), Length(max=255)])


class VisitForm(FlaskForm):
    clinician = StringField("Clinician", validators=[Optional(), Length(max=120)])
    notes = TextAreaField("Clinical Notes", validators=[Optional()])

    # Diagnosis fields (up to 5 diagnoses)
    diagnosis_code_1 = StringField(
        "Diagnosis Code 1", validators=[Optional(), Length(max=20)]
    )
    diagnosis_desc_1 = StringField(
        "Diagnosis Description 1", validators=[Optional(), Length(max=255)]
    )

    diagnosis_code_2 = StringField(
        "Diagnosis Code 2", validators=[Optional(), Length(max=20)]
    )
    diagnosis_desc_2 = StringField(
        "Diagnosis Description 2", validators=[Optional(), Length(max=255)]
    )

    diagnosis_code_3 = StringField(
        "Diagnosis Code 3", validators=[Optional(), Length(max=20)]
    )
    diagnosis_desc_3 = StringField(
        "Diagnosis Description 3", validators=[Optional(), Length(max=255)]
    )

    diagnosis_code_4 = StringField(
        "Diagnosis Code 4", validators=[Optional(), Length(max=20)]
    )
    diagnosis_desc_4 = StringField(
        "Diagnosis Description 4", validators=[Optional(), Length(max=255)]
    )

    diagnosis_code_5 = StringField(
        "Diagnosis Code 5", validators=[Optional(), Length(max=20)]
    )
    diagnosis_desc_5 = StringField(
        "Diagnosis Description 5", validators=[Optional(), Length(max=255)]
    )

    submit = SubmitField("Save Visit")


class EditNotesForm(FlaskForm):
    notes = TextAreaField("Clinical Notes", validators=[Optional()])
    submit = SubmitField("Update Notes")


class DiagnosisForm(FlaskForm):
    code = StringField("Code", validators=[Optional(), Length(max=20)])
    description = StringField(
        "Description", validators=[DataRequired(), Length(max=255)]
    )
    submit = SubmitField("Add")
