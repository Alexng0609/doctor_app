from datetime import datetime
from doctor_app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.String(20), default="doctor"
    )  # 'admin', 'doctor', or 'assistant'
    full_name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    # Relationships
    visits = db.relationship(
        "Visit", backref="creator", lazy=True, foreign_keys="Visit.created_by"
    )
    patients = db.relationship(
        "Patient", backref="primary_doctor", lazy=True, foreign_keys="Patient.doctor_id"
    )
    assistants = db.relationship(
        "User",
        backref=db.backref("doctor", remote_side=[id]),
        foreign_keys=[doctor_id],
        lazy="dynamic",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "admin"

    def is_doctor(self):
        return self.role == "doctor"

    def is_assistant(self):
        return self.role == "assistant"

    def can_delete_patient(self):
        """Assistants cannot delete patients"""
        return self.role in ["admin", "doctor"]

    def can_import_export(self):
        """Assistants cannot import/export"""
        return self.role in ["admin", "doctor"]

    def get_accessible_patients(self):
        """
        Get all patients this user can access:
        1. Patients directly assigned to this doctor (doctor_id = self.id)
        2. Patients this doctor has added visits to (via created_by in Visit)

        This enables shared patients without database migration.
        """
        from sqlalchemy import or_

        # Determine target doctor ID
        if self.is_assistant():
            # Assistants see their doctor's patients + patients they've visited
            target_doctor_id = self.doctor_id
        else:
            # Doctors/admins see their own patients + patients they've visited
            target_doctor_id = self.id

        # Get patient IDs from visits this user created
        visit_patient_ids = (
            db.session.query(Patient.id)
            .join(Visit)
            .filter(Visit.created_by == self.id)
            .distinct()
            .subquery()
        )

        # Return patients that are either:
        # - Assigned to this doctor (or their doctor if assistant), OR
        # - Have visits created by this user
        return Patient.query.filter(
            or_(
                Patient.doctor_id == target_doctor_id, Patient.id.in_(visit_patient_ids)
            )
        )


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=True, index=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
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
