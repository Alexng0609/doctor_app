import os
import sys

# Ensure the folder containing doctor_app is in Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from doctor_app import create_app, db
from doctor_app.models import User

app = create_app()

# Create a default admin user if none exists
with app.app_context():
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("✓ Default admin user created (username: admin, password: admin123)")
    else:
        print("✓ Admin user already exists")

if __name__ == "__main__":
    # Show all routes
    print("\n=== AVAILABLE ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule} -> {rule.endpoint}")
    print("======================\n")

    print("Starting server...")
    print("Access the app at: http://127.0.0.1:5000/")
    print("Login with username: admin, password: admin123\n")

    app.run(debug=True)
