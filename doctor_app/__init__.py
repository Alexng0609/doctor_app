import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from doctor_app.config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # Fixed: should be "auth.login"

    # Import and register blueprints
    from doctor_app.auth.routes import bp as auth_bp

    app.register_blueprint(auth_bp)  # no prefix

    from doctor_app.patients.routes import bp as patients_bp

    app.register_blueprint(patients_bp, url_prefix="/patients")

    from doctor_app.visits.routes import bp as visits_bp

    app.register_blueprint(visits_bp, url_prefix="/visits")

    # Create database tables
    with app.app_context():
        from doctor_app.models import User, Patient, Visit, Diagnosis

        db.create_all()

    return app
