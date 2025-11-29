from doctor_app import create_app, db
from doctor_app.models import User

app = create_app()

with app.app_context():
    # Check if admin already exists
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")  # Change password as needed
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: username='admin', password='admin123'")
    else:
        print("Admin user already exists.")
