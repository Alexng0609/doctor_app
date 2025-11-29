from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from doctor_app import db
from doctor_app.models import Patient, Visit, Diagnosis
from doctor_app.visits.forms import VisitForm, DiagnosisForm

bp = Blueprint("visits", __name__)


# Add new visit
@bp.route("/new/<int:patient_id>", methods=["GET", "POST"])
@login_required
def new_visit(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = VisitForm()
    if form.validate_on_submit():
        v = Visit(
            patient_id=patient.id, clinician=form.clinician.data, notes=form.notes.data
        )
        db.session.add(v)
        db.session.commit()
        flash("Visit added", "success")
        return redirect(url_for("visits.visit_detail", visit_id=v.id))
    return render_template("visits/new.html", form=form, patient=patient)


# Visit detail page
@bp.route("/<int:visit_id>", methods=["GET", "POST"])
@login_required
def visit_detail(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    form = DiagnosisForm()
    if form.validate_on_submit():
        d = Diagnosis(
            visit_id=visit.id, code=form.code.data, description=form.description.data
        )
        db.session.add(d)
        db.session.commit()
        flash("Diagnosis added", "success")
        return redirect(url_for("visits.visit_detail", visit_id=visit.id))
    diagnoses = visit.diagnoses
    return render_template(
        "visits/detail.html", visit=visit, diagnoses=diagnoses, form=form
    )
