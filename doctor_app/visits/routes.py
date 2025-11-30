from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from doctor_app import db
from doctor_app.models import Patient, Visit, Diagnosis
from doctor_app.visits.forms import VisitForm, EditNotesForm

bp = Blueprint("visits", __name__)


# Add new visit
@bp.route("/new/<int:patient_id>", methods=["GET", "POST"])
@login_required
def new_visit(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = VisitForm()

    # Pre-fill clinician with current user's name
    if request.method == "GET" and current_user.full_name:
        form.clinician.data = current_user.full_name

    if form.validate_on_submit():
        # Validate diagnoses - if any field is filled, description is required
        validation_errors = []
        for i in range(1, 6):
            code_field = f"diagnosis_code_{i}"
            desc_field = f"diagnosis_desc_{i}"

            code = getattr(form, code_field).data
            desc = getattr(form, desc_field).data

            # If EITHER code OR description is provided, description must be filled
            if (code and code.strip()) or (desc and desc.strip()):
                if not desc or not desc.strip():
                    validation_errors.append(
                        f"Diagnosis {i}: Description is required. Please fill in the diagnosis description."
                    )
                elif len(desc.strip()) < 3:
                    validation_errors.append(
                        f"Diagnosis {i}: Description must be at least 3 characters long."
                    )

        if validation_errors:
            for error in validation_errors:
                flash(error, "danger")
            return render_template("visits/new.html", form=form, patient=patient)

        v = Visit(
            patient_id=patient.id,
            clinician=form.clinician.data,
            notes=form.notes.data,
            created_by=current_user.id,
        )
        db.session.add(v)
        db.session.flush()  # Get visit.id for diagnoses

        # Add diagnoses (up to 5)
        diagnoses_added = 0
        for i in range(1, 6):
            code = getattr(form, f"diagnosis_code_{i}").data
            desc = getattr(form, f"diagnosis_desc_{i}").data

            # Only add diagnosis if description is provided
            if desc and desc.strip():
                diagnosis = Diagnosis(
                    visit_id=v.id,
                    code=code.strip() if code else None,
                    description=desc.strip(),
                )
                db.session.add(diagnosis)
                diagnoses_added += 1

        db.session.commit()

        if diagnoses_added > 0:
            flash(
                f"Visit added successfully with {diagnoses_added} diagnosis(es)",
                "success",
            )
        else:
            flash("Visit added successfully", "success")

        return redirect(url_for("patients.patient_detail", patient_id=patient.id))
    return render_template("visits/new.html", form=form, patient=patient)


# Visit detail page (with editable notes)
@bp.route("/<int:visit_id>", methods=["GET", "POST"])
@login_required
def visit_detail(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    diagnoses = visit.diagnoses
    form = EditNotesForm(obj=visit)

    if form.validate_on_submit():
        visit.notes = form.notes.data
        db.session.commit()
        flash("Clinical notes updated successfully", "success")
        return redirect(url_for("visits.visit_detail", visit_id=visit.id))

    return render_template(
        "visits/detail.html", visit=visit, diagnoses=diagnoses, form=form
    )


# Edit visit
@bp.route("/<int:visit_id>/edit", methods=["GET", "POST"])
@login_required
def edit_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    form = VisitForm()

    # Pre-populate form with existing data on GET
    if request.method == "GET":
        form.clinician.data = visit.clinician
        form.notes.data = visit.notes

        # Pre-populate existing diagnoses
        for i, diagnosis in enumerate(visit.diagnoses[:5], start=1):
            getattr(form, f"diagnosis_code_{i}").data = diagnosis.code
            getattr(form, f"diagnosis_desc_{i}").data = diagnosis.description

    if form.validate_on_submit():
        # Validate diagnoses
        validation_errors = []
        for i in range(1, 6):
            code = getattr(form, f"diagnosis_code_{i}").data
            desc = getattr(form, f"diagnosis_desc_{i}").data

            if (code and code.strip()) or (desc and desc.strip()):
                if not desc or not desc.strip():
                    validation_errors.append(f"Diagnosis {i}: Description is required.")
                elif len(desc.strip()) < 3:
                    validation_errors.append(
                        f"Diagnosis {i}: Description must be at least 3 characters long."
                    )

        if validation_errors:
            for error in validation_errors:
                flash(error, "danger")
            return render_template("visits/edit.html", form=form, visit=visit)

        # Update visit info
        visit.clinician = form.clinician.data
        visit.notes = form.notes.data

        # Delete old diagnoses
        for diagnosis in visit.diagnoses:
            db.session.delete(diagnosis)

        # Add new diagnoses
        diagnoses_added = 0
        for i in range(1, 6):
            code = getattr(form, f"diagnosis_code_{i}").data
            desc = getattr(form, f"diagnosis_desc_{i}").data

            if desc and desc.strip():
                diagnosis = Diagnosis(
                    visit_id=visit.id,
                    code=code.strip() if code else None,
                    description=desc.strip(),
                )
                db.session.add(diagnosis)
                diagnoses_added += 1

        db.session.commit()
        flash(
            f"Visit updated successfully with {diagnoses_added} diagnosis(es)",
            "success",
        )
        return redirect(url_for("patients.patient_detail", patient_id=visit.patient_id))

    return render_template("visits/edit.html", form=form, visit=visit)


# Delete visit
@bp.route("/<int:visit_id>/delete", methods=["POST"])
@login_required
def delete_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    patient_id = visit.patient_id
    visit_date = visit.visit_date.strftime("%B %d, %Y")

    db.session.delete(visit)
    db.session.commit()
    flash(f"Visit from {visit_date} deleted successfully", "success")
    return redirect(url_for("patients.patient_detail", patient_id=patient_id))
