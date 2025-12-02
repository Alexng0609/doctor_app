from datetime import datetime
from doctor_app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="doctor")  # 'admin' or 'doctor'
    full_name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    location = db.Column(
        db.String(255), nullable=True
    )  # UPDATED: Increased to 255 for full addresses
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationship to visits created by this user
    visits = db.relationship(
        "Visit", backref="creator", lazy=True, foreign_keys="Visit.created_by"
    )

    # Relationship to patients assigned to this doctor
    patients = db.relationship("Patient", backref="primary_doctor", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "admin"


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=True, index=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    doctor_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True
    )  # NEW: Primary doctor
    visits = db.relationship(
        "Visit", backref="patient", lazy=True, cascade="all, delete-orphan"
    )


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True
    )
    visit_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    clinician = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    diagnoses = db.relationship(
        "Diagnosis", backref="visit", lazy=True, cascade="all, delete-orphan"
    )


class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(
        db.Integer, db.ForeignKey("visit.id"), nullable=False, index=True
    )
    code = db.Column(db.String(20), nullable=True)
    description = db.Column(db.String(255), nullable=False)
