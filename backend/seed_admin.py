"""
One-off script to create an admin user, since public /register always
creates 'farmer' accounts by design (see routes/auth.py).

Usage:
    cd backend
    python seed_admin.py
"""
import getpass
from app import create_app
from extensions import db, hash_password
from models import new_user_doc

app = create_app()

with app.app_context():
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass.getpass("Admin password: ")

    if db.users.find_one({"email": email}):
        print(f"A user with email {email} already exists.")
    else:
        doc = new_user_doc(name, email, hash_password(password), role="admin")
        db.users.insert_one(doc)
        print(f"Admin account created for {email}.")
