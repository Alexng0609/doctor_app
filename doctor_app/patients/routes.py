from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from doctor_app import db
from doctor_app.models import Patient, Visit, Diagnosis
from doctor_app.patients.forms import PatientForm, ImportPatientsForm
import openpyxl
from datetime import datetime

bp = Blueprint("patients", __name__)


# List all patients
@bp.route("/", methods=["GET"])
@login_required
def list_patients():
    q = request.args.get("q", "")
    patients = Patient.query
    if q:
        patients = patients.filter(
            (Patient.full_name.ilike(f"%{q}%")) | (Patient.phone.ilike(f"%{q}%"))
        )
    patients = patients.order_by(Patient.full_name.asc()).all()
    return render_template("patients/list.html", patients=patients, q=q)


# Add new patient
@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_patient():
    form = PatientForm()
    if form.validate_on_submit():
        p = Patient(
            full_name=form.full_name.data,
            phone=form.phone.data,
            date_of_birth=form.date_of_birth.data,
        )
        db.session.add(p)
        db.session.commit()
        flash("Patient created successfully", "success")
        return redirect(url_for("patients.list_patients"))
    return render_template("patients/new.html", form=form)


# Patient detail page
@bp.route("/<int:patient_id>", methods=["GET"])
@login_required
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    visits = patient.visits
    return render_template("patients/detail.html", patient=patient, visits=visits)


# Import patients from Excel
@bp.route("/import", methods=["GET", "POST"])
@login_required
def import_patients():
    form = ImportPatientsForm()
    if form.validate_on_submit():
        file = form.file.data

        try:
            # Load the Excel file
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            imported_count = 0
            skipped_count = 0
            errors = []

            # Skip header row (assumes first row is header)
            for row_idx, row in enumerate(
                sheet.iter_rows(min_row=2, values_only=True), start=2
            ):
                try:
                    # Expected columns: Full Name, Phone, Date of Birth, Visit Date, Clinician, Notes, Diagnosis Code, Diagnosis Description
                    full_name = row[0] if len(row) > 0 else None
                    phone = row[1] if len(row) > 1 else None
                    dob_value = row[2] if len(row) > 2 else None
                    visit_date_value = row[3] if len(row) > 3 else None
                    clinician = row[4] if len(row) > 4 else None
                    notes = row[5] if len(row) > 5 else None
                    diagnosis_code = row[6] if len(row) > 6 else None
                    diagnosis_description = row[7] if len(row) > 7 else None

                    # Validate required fields
                    if not full_name or str(full_name).strip() == "":
                        skipped_count += 1
                        errors.append(f"Row {row_idx}: Missing full name")
                        continue

                    # Parse date of birth
                    date_of_birth = None
                    if dob_value:
                        if isinstance(dob_value, datetime):
                            date_of_birth = dob_value.date()
                        elif isinstance(dob_value, str):
                            try:
                                for fmt in [
                                    "%Y-%m-%d",
                                    "%m/%d/%Y",
                                    "%d/%m/%Y",
                                    "%Y/%m/%d",
                                ]:
                                    try:
                                        date_of_birth = datetime.strptime(
                                            dob_value, fmt
                                        ).date()
                                        break
                                    except ValueError:
                                        continue
                            except:
                                pass

                    # Check if patient already exists (by name and phone)
                    existing_patient = None
                    if phone and str(phone).strip():
                        existing_patient = Patient.query.filter_by(
                            full_name=str(full_name).strip(), phone=str(phone).strip()
                        ).first()

                    if not existing_patient:
                        existing_patient = Patient.query.filter_by(
                            full_name=str(full_name).strip()
                        ).first()

                    # Create or use existing patient
                    if existing_patient:
                        patient = existing_patient
                    else:
                        patient = Patient(
                            full_name=str(full_name).strip(),
                            phone=str(phone).strip() if phone else None,
                            date_of_birth=date_of_birth,
                        )
                        db.session.add(patient)
                        db.session.flush()  # Get patient.id for visit

                    # Create visit if visit date or diagnosis is provided
                    if visit_date_value or diagnosis_description:
                        # Parse visit date
                        visit_date = None
                        if visit_date_value:
                            if isinstance(visit_date_value, datetime):
                                visit_date = visit_date_value
                            elif isinstance(visit_date_value, str):
                                try:
                                    for fmt in [
                                        "%Y-%m-%d",
                                        "%m/%d/%Y",
                                        "%d/%m/%Y",
                                        "%Y/%m/%d",
                                        "%Y-%m-%d %H:%M:%S",
                                        "%m/%d/%Y %H:%M:%S",
                                    ]:
                                        try:
                                            visit_date = datetime.strptime(
                                                visit_date_value, fmt
                                            )
                                            break
                                        except ValueError:
                                            continue
                                except:
                                    pass

                        # If no visit date provided, use current datetime
                        if not visit_date:
                            visit_date = datetime.utcnow()

                        # Create visit
                        visit = Visit(
                            patient_id=patient.id,
                            visit_date=visit_date,
                            clinician=str(clinician).strip() if clinician else None,
                            notes=str(notes).strip() if notes else None,
                        )
                        db.session.add(visit)
                        db.session.flush()  # Get visit.id for diagnosis

                        # Create diagnosis if description is provided
                        if diagnosis_description and str(diagnosis_description).strip():
                            diagnosis = Diagnosis(
                                visit_id=visit.id,
                                code=str(diagnosis_code).strip()
                                if diagnosis_code
                                else None,
                                description=str(diagnosis_description).strip(),
                            )
                            db.session.add(diagnosis)

                    imported_count += 1

                except Exception as e:
                    skipped_count += 1
                    errors.append(f"Row {row_idx}: {str(e)}")

            # Commit all changes at once
            db.session.commit()

            # Show results
            flash(f"Successfully imported {imported_count} patient records", "success")
            if skipped_count > 0:
                flash(f"Skipped {skipped_count} rows due to errors", "warning")

            # Show first few errors if any
            for error in errors[:5]:
                flash(error, "warning")
            if len(errors) > 5:
                flash(f"... and {len(errors) - 5} more errors", "warning")

            return redirect(url_for("patients.list_patients"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error importing file: {str(e)}", "danger")

    return render_template("patients/import.html", form=form)
