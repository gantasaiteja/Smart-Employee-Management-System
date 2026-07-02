from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(db.String(20), unique=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    department = db.Column(db.String(100), nullable=False)

    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default="Employee")


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(db.String(20), nullable=False)

    date = db.Column(db.String(20), nullable=False)

    status = db.Column(db.String(20), default="Present")


class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(db.String(20), nullable=False)

    from_date = db.Column(db.String(20), nullable=False)

    to_date = db.Column(db.String(20), nullable=False)

    reason = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), default="Pending")