import click
from flask.cli import with_appcontext
from .db import Admin, db
from werkzeug.security import generate_password_hash
from .functions import generate_id
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
regex = re.compile(regex)

@click.command(name="createadminuser")
@with_appcontext
def create_admin_user():
    username = ""
    while not username.strip():
        username = input("Enter username : ")

    email = ""
    while not email.strip():
        email = input("Enter your email : ")
        if not regex.match(email):
            print("Invalid email address")
            email = ""

    password = ""
    while not password.strip() or len(password) < 8:
        password = input("Enter your password : ")
    
    account = Admin.query.filter(Admin.email == email).first()

    if account:
        print("Email already used with another account!")
        return
    
    hashed_password = generate_password_hash(password, "SHA256")
    session_id = generate_id(username, email, hashed_password)

    admin = Admin(
        username = username,
        email = email,
        password = hashed_password,
        session_id = session_id
    )

    db.session.add(admin)
    db.session.commit()

    print("Admin created successfully")