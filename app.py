from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Attendance, LeaveRequest
from flask_mail import Mail, Message

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

with app.app_context():
    db.create_all()


# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    return render_template("login.html")


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):

        session["user_id"] = user.id
        session["role"] = user.role

        if user.role == "Admin":
            return redirect(url_for("admin_dashboard"))

        return redirect(url_for("employee_dashboard"))

    flash("Invalid Email or Password")
    return redirect(url_for("home"))


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():

    if "admin_id" in session:

        session["user_id"] = session["admin_id"]

        session["role"] = "Admin"

        session.pop("admin_id")

        flash("Returned to Admin Account")

        return redirect(url_for("admin_dashboard"))

    session.clear()

    return redirect(url_for("home"))
# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@app.route("/admin-dashboard")
def admin_dashboard():

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    total_employees = User.query.filter_by(role="Employee").count()

    present_today = Attendance.query.filter_by(status="Present").count()

    pending_leaves = LeaveRequest.query.filter_by(status="Pending").count()

    approved_leaves = LeaveRequest.query.filter_by(status="Approved").count()

    return render_template(
        "admin_dashboard.html",
        total_employees=total_employees,
        present_today=present_today,
        pending_leaves=pending_leaves,
        approved_leaves=approved_leaves
    )


# -----------------------------
# EMPLOYEE DASHBOARD
# -----------------------------
@app.route("/employee-dashboard")
def employee_dashboard():

    if session.get("role") != "Employee":
        return redirect(url_for("home"))

    user = User.query.get(session["user_id"])

    attendance_count = Attendance.query.filter_by(
        employee_id=user.employee_id
    ).count()

    pending_count = LeaveRequest.query.filter_by(
        employee_id=user.employee_id,
        status="Pending"
    ).count()

    approved_count = LeaveRequest.query.filter_by(
        employee_id=user.employee_id,
        status="Approved"
    ).count()

    return render_template(
        "employee_dashboard.html",
        attendance_count=attendance_count,
        pending_count=pending_count,
        approved_count=approved_count
    )

# -----------------------------
# CREATE EMPLOYEE
# -----------------------------
@app.route("/create-employee", methods=["GET", "POST"])
def create_employee():

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        password = generate_password_hash(request.form["password"])

        employee_count = User.query.filter_by(role="Employee").count() + 1
        employee_id = f"EMP{employee_count:04d}"

        employee = User(
            employee_id=employee_id,
            name=name,
            email=email,
            department=department,
            password=password,
            role="Employee"
        )

        db.session.add(employee)
        db.session.commit()

        flash("Employee Created Successfully")

        return redirect(url_for("admin_dashboard"))

    return render_template("create_employee.html")
# -----------------------------
# PROFILE
# -----------------------------
@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("home"))

    user = User.query.get(session["user_id"])

    return render_template(
        "profile.html",
        user=user
    )


# -----------------------------
# ATTENDANCE
# -----------------------------
@app.route("/attendance")
def attendance():

    if "user_id" not in session:
        return redirect(url_for("home"))

    user = User.query.get(session["user_id"])

    attendances = Attendance.query.filter_by(
        employee_id=user.employee_id
    ).all()

    return render_template(
        "attendance.html",
        attendances=attendances
    )


# -----------------------------
# APPLY LEAVE
# -----------------------------
@app.route("/apply-leave", methods=["GET", "POST"])
def apply_leave():

    if "user_id" not in session:
        return redirect(url_for("home"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        leave = LeaveRequest(
            employee_id=user.employee_id,
            from_date=request.form["from_date"],
            to_date=request.form["to_date"],
            reason=request.form["reason"],
            status="Pending"
        )

        db.session.add(leave)
        db.session.commit()

        flash("Leave Request Submitted Successfully")

        return redirect(url_for("leave_history"))

    return render_template("apply_leave.html")
# -----------------------------
# LEAVE HISTORY
# -----------------------------
@app.route("/leave-history")
def leave_history():

    if "user_id" not in session:
        return redirect(url_for("home"))

    user = User.query.get(session["user_id"])

    leaves = LeaveRequest.query.filter_by(
        employee_id=user.employee_id
    ).all()

    return render_template(
        "leave_history.html",
        leaves=leaves
    )


# -----------------------------
# ADMIN LEAVE REQUESTS
# -----------------------------
@app.route("/leave-requests")
def leave_requests():

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    leaves = LeaveRequest.query.all()

    return render_template(
        "admin_leave_requests.html",
        leaves=leaves
    )

# -----------------------------
# APPROVE LEAVE
# -----------------------------
@app.route("/approve-leave/<int:leave_id>")
def approve_leave(leave_id):

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    leave = LeaveRequest.query.get_or_404(leave_id)

    leave.status = "Approved"

    db.session.commit()

    employee = User.query.filter_by(
        employee_id=leave.employee_id
    ).first()

    msg = Message(
    subject="Leave Request Approved",
    sender=app.config["MAIL_DEFAULT_SENDER"],
    recipients=[employee.email]
)
    

    msg.body = f"""
Hello {employee.name},

Your leave request has been APPROVED.

From Date : {leave.from_date}
To Date   : {leave.to_date}

Status : Approved

Regards,
HR Department
"""

    print(employee.email)

    mail.send(msg)

    flash("Leave Approved Successfully")

    return redirect(url_for("leave_requests"))
# -----------------------------
# REJECT LEAVE
# -----------------------------
@app.route("/reject-leave/<int:leave_id>")
def reject_leave(leave_id):

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    leave = LeaveRequest.query.get_or_404(leave_id)

    leave.status = "Rejected"

    db.session.commit()

    flash("Leave Rejected Successfully")

    return redirect(url_for("leave_requests"))
# -----------------------------
# CHANGE PASSWORD
# -----------------------------
@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        return redirect(url_for("home"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if not check_password_hash(user.password, current_password):
            flash("Current Password is Incorrect")
            return redirect(url_for("change_password"))

        if new_password != confirm_password:
            flash("New Password and Confirm Password do not match")
            return redirect(url_for("change_password"))

        user.password = generate_password_hash(new_password)

        db.session.commit()

        flash("Password Changed Successfully")

        return redirect(url_for("employee_dashboard"))

    return render_template("change_password.html")


# -----------------------------
# CREATE DEFAULT ADMIN
# -----------------------------
@app.route("/create-admin")
def create_admin():

    admin = User.query.filter_by(role="Admin").first()

    if admin:
        return "Admin Already Exists"

    admin = User(
        employee_id="ADMIN001",
        name="Administrator",
        email="admin@company.com",
        department="Administration",
        password=generate_password_hash("admin123"),
        role="Admin"
    )

    db.session.add(admin)
    db.session.commit()

    return "Admin Created Successfully"
# -----------------------------
# ERROR HANDLERS
# -----------------------------
@app.errorhandler(404)
def page_not_found(error):
    return "<h2>404 - Page Not Found</h2>", 404


@app.errorhandler(500)
def internal_server_error(error):
    return "<h2>500 - Internal Server Error</h2>", 500

# -----------------------------
# ADMIN ATTENDANCE
# -----------------------------
@app.route("/admin-attendance", methods=["GET", "POST"])
def admin_attendance():

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    employees = User.query.filter_by(role="Employee").all()

    if request.method == "POST":

        from datetime import datetime

        today = datetime.now().strftime("%d-%m-%Y")

        for employee in employees:

            status = request.form.get(f"status_{employee.employee_id}")

            existing = Attendance.query.filter_by(
                employee_id=employee.employee_id,
                date=today
            ).first()

            if existing:
                existing.status = status
            else:
                attendance = Attendance(
                    employee_id=employee.employee_id,
                    date=today,
                    status=status
                )
                db.session.add(attendance)

        db.session.commit()

        flash("Attendance Saved Successfully")

        return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin_attendance.html",
        employees=employees
    )

# -----------------------------
# EMPLOYEE LIST
# -----------------------------
@app.route("/employee-list")
def employee_list():

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    employees = User.query.filter_by(role="Employee").all()

    return render_template(
        "employee_list.html",
        employees=employees
    )

# -----------------------------
# VIEW EMPLOYEE
# -----------------------------
@app.route("/view-employee/<int:user_id>")
def view_employee(user_id):

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    employee = User.query.get_or_404(user_id)

    attendance = Attendance.query.filter_by(
        employee_id=employee.employee_id
    ).all()

    leaves = LeaveRequest.query.filter_by(
        employee_id=employee.employee_id
    ).all()

    return render_template(
        "view_employee.html",
        employee=employee,
        attendance=attendance,
        leaves=leaves
    )

# -----------------------------
# RESET EMPLOYEE PASSWORD
# -----------------------------
@app.route("/reset-password/<int:user_id>", methods=["GET", "POST"])
def reset_password(user_id):

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    employee = User.query.get_or_404(user_id)

    if request.method == "POST":

        new_password = request.form["new_password"]

        employee.password = generate_password_hash(new_password)

        db.session.commit()

        flash("Employee Password Reset Successfully")

        return redirect(url_for("employee_list"))

    return render_template(
        "reset_password.html",
        employee=employee
    )

# -----------------------------
# LOGIN AS EMPLOYEE
# -----------------------------
@app.route("/login-as-employee/<int:user_id>")
def login_as_employee(user_id):

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    employee = User.query.get_or_404(user_id)

    session["admin_id"] = session["user_id"]

    session["user_id"] = employee.id

    session["role"] = "Employee"

    flash("Logged in as Employee")

    return redirect(url_for("employee_dashboard"))


# -----------------------------
# RUN APPLICATION
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)