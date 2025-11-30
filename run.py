import os
import sys

# Ensure the folder containing doctor_app is in Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from doctor_app import create_app, db
from doctor_app.models import User

app = create_app()

# Create default users if none exist
with app.app_context():
    if User.query.count() == 0:
        # Create admin user
        admin = User(
            username="admin",
            full_name="Administrator",
            email="admin@clinic.com",
            role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)

        # Create sample doctor user
        doctor = User(
            username="doctor1",
            full_name="Dr. John Smith",
            email="doctor1@clinic.com",
            role="doctor",
        )
        doctor.set_password("doctor123")
        db.session.add(doctor)

        db.session.commit()
        print("✓ Default users created:")
        print("  Admin - username: admin, password: admin123")
        print("  Doctor - username: doctor1, password: doctor123")
    else:
        print(f"✓ Database has {User.query.count()} user(s)")

if __name__ == "__main__":
    # Show all routes
    print("\n=== AVAILABLE ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule} -> {rule.endpoint}")
    print("======================\n")

    print("Starting server...")
    print("Access the app at: http://127.0.0.1:5000/")
    print("\nDefault Login Credentials:")
    print("  Admin: username=admin, password=admin123")
    print("  Doctor: username=doctor1, password=doctor123\n")

    app.run(debug=True)
