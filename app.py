from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import string
import matplotlib.pyplot as plt
import numpy as np
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:1234@localhost/Hospital"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = os.urandom(24)  # Generate a secure random secret key
app.config['UPLOAD_FOLDER'] = 'static/uploads'  
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

HEALTH_PROBLEMS = [
    "Fever",
    "Cough",
    "Headache",
    "Nausea",
    "Abdominal Pain",
    "Fatigue",
    "Skin Rash",
    "Muscle Pain",
    "Joint Pain",
    "Others (please specify)"
]

def send_email(emailID,emailsubject,emailbody,password):
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    sender_email = "apollohospital069@gmail.com"
    sender_password = "xqho lrkx ekej nxrx"

    recipient_email = emailID
    subject = emailsubject
    body = emailbody+password

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def generate_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.Integer, nullable=True)
    bloodgroup = db.Column(db.String(5), nullable=True)
    phone = db.Column(db.String(15), unique=True)
    address = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200), nullable=False)  # New password field
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))  # Ensure this is defined
    problem = db.Column(db.String(200), nullable=True)  # New field for health problem
    bloodpressure = db.Column(db.String(6), nullable=True)

    
class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200), nullable=False)  # For hashed passwords
    room_no = db.Column(db.Integer, unique=True, autoincrement = True)
    status = db.Column(db.String(20), default='pending')  # Default to 'pending'
    
    # New fields for storing the uploaded files
    profile_picture_path = db.Column(db.String(200), nullable=False)  # Path to profile picture
    resume_path = db.Column(db.String(200), nullable=False)  # Path to resume
    
    def get_id(self):
        return str(self.doctor_id)

class LogginedDoctor(db.Model):
    __tablename__ = 'LogginedDoctor'
    doctor_id = db.Column(db.Integer,nullable = False,primary_key = True)
    status = db.Column(db.String(20),default = "Logged-out",nullable = False)
    
class LogginedPatient(db.Model):
    __tablename__ = 'LogginedPatient'
    patient_id = db.Column(db.Integer,nullable = False,primary_key = True)
    status = db.Column(db.String(20),default = "Logged-out",nullable = False)
class LogginedAdmin(db.Model):
    __tablename__ = 'LogginedAdmin'
    admin_id = db.Column(db.String(20),nullable = False,primary_key = True)
    status = db.Column(db.String(20),default = "Logged-out",nullable = False)
    
class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.String(100),nullable = False,primary_key = True)
    admin_password = db.Column(db.String(500),nullable = False)
class PatientDoctor(db.Model):
    __tablename__ = 'patient_doctor'
    room_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    feedbackId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    feedback = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(10), default="Pending")
class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    date = db.Column(db.Date, nullable=False)
    room_no = db.Column(db.Integer,db.ForeignKey('doctors.room_no'))
    doctor_name = db.Column(db.String(100), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    patient_problem = db.Column(db.String(100), nullable=False)
    prescription = db.Column(db.String(500), nullable=True)

class DoctorRequest(db.Model):
    __tablename__ = 'doctor_requests'
    request_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(50), default="Pending")  # Default to 'Pending'
    profile_picture = db.Column(db.String(500), nullable=False)  # New field for profile picture path
    resume = db.Column(db.String(500), nullable=False)  # New field for resume path


# # =======================
# # Dummy Data
# # =======================
def populate_db():
# Dummy data for doctors
    doctors = [
        Doctor(name="John Doe", specialization="Cardiologist", phone="1234567890",
               email="johndoe@example.com", password=generate_password_hash("doc1",method='pbkdf2:sha256'),
               room_no=101, profile_picture_path="uploads/johndoe.jpg",
               resume_path="uploads/johndoe_resume.pdf", status="approved"),
        Doctor(name="Jane Smith", specialization="Neurologist", phone="0987654321",
               email="janesmith@example.com", password=generate_password_hash("doc2",method='pbkdf2:sha256'),
               room_no=102, profile_picture_path="uploads/janesmith.jpg",
               resume_path="uploads/janesmith_resume.pdf", status="approved"),
        Doctor(name="John Paul", specialization="General Physician", phone="1234567891",
               email="johnpaul@example.com", password=generate_password_hash("doc3",method='pbkdf2:sha256'),
               room_no=103, profile_picture_path="uploads/johnpaul.jpg",
               resume_path="uploads/johnpaul_resume.pdf", status="approved"),
        Doctor(name="Jaime Smith", specialization="Surgeon", phone="0987654322",
               email="jaimesmith@example.com", password=generate_password_hash("doc4",method='pbkdf2:sha256'),
               room_no=104, profile_picture_path="uploads/jaimesmith.jpg",
               resume_path="uploads/jaimesmith_resume.pdf", status="approved")
    ]

# Dummy data for patients
    patients = [
        Patient(name="Alice Johnson", age=30, gender="Female", weight=65, bloodgroup="O+",
                phone="1234567890", address="123 Main St", email="alice@example.com",
                password=generate_password_hash("patient1",method='pbkdf2:sha256'), doctor_id=1, problem="Heart issues",
                bloodpressure="120/80"),
        Patient(name="Bob Williams", age=40, gender="Male", weight=85, bloodgroup="B+",
                phone="0987654321", address="456 Elm St", email="bob@example.com",
                password=generate_password_hash("patient2",method='pbkdf2:sha256'), doctor_id=2, problem="Migraine",
                bloodpressure="130/83"),
        Patient(name="Alice Paulson", age=32, gender="Female", weight=65, bloodgroup="O+",
                phone="1234567891", address="123 LA Street", email="paulson@example.com",
                password=generate_password_hash("patient3",method='pbkdf2:sha256'), doctor_id=3, problem="General",
                bloodpressure="125/80"),
        Patient(name="Bob Williams", age=41, gender="Male", weight=85, bloodgroup="B+",
                phone="0987654322", address="456 River St", email="willi@example.com",
                password=generate_password_hash("patient4",method='pbkdf2:sha256'), doctor_id=4, problem="Surgery",
                bloodpressure="127/84")
    ]

# Dummy data for admins
    admins = [
        Admin(admin_id="admin001", admin_password=generate_password_hash("admin1",method='pbkdf2:sha256')),
        Admin(admin_id="admin002", admin_password=generate_password_hash("admin2",method='pbkdf2:sha256')),
        Admin(admin_id="admin003", admin_password=generate_password_hash("admin3",method='pbkdf2:sha256'))
    ]
# Dummy data for DocUser and PatUser
    Docusers = [
        LogginedDoctor(doctor_id=1,status="Logged-out"),
        LogginedDoctor(doctor_id=2,status="Logged-out"),
        LogginedDoctor(doctor_id=3,status="Logged-out"),
        LogginedDoctor(doctor_id=4,status="Logged-out"),
    ]
    Patusers = (
        LogginedPatient(patient_id=1,status="Logged-out"),
        LogginedPatient(patient_id=2,status="Logged-out"),
        LogginedPatient(patient_id=3,status="Logged-out"),
        LogginedPatient(patient_id=4,status="Logged-out"),
    )
    Adminusers = (
        LogginedAdmin(admin_id="admin001",status="Logged-out"),
        LogginedAdmin(admin_id="admin002",status="Logged-out"),
        LogginedAdmin(admin_id="admin003",status="Logged-out"),
    )

# Insert data into the database
    for doctor in doctors:
        db.session.add(doctor)
    for patient in patients:
        db.session.add(patient)
    for admin in admins:
        db.session.add(admin)    
    for user in Docusers:
        db.session.add(user)
    for user in Patusers:
        db.session.add(user)
    for user in Adminusers:
        db.session.add(user)
# Commit the changes to the database
    db.session.commit()
    
# =======================
# Home and Role Selection
# =======================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/role_selection', methods=['POST'])
def role_selection():
    role = request.form['role']
    
    if role == 'admin':
        return redirect(url_for('admin_selection'))  # Redirect to the admin login page
    elif role == 'patient':
        return redirect(url_for('patient_selection'))  # Redirect to the patient dashboard
    elif role == 'doctor':
        return redirect(url_for('doctor_selection'))  # Redirect to the doctor selection page

# =======================
# Patient Routes
# =======================
@app.route('/patient_selection', methods=['GET', 'POST'])
def patient_selection():
    if request.method == 'POST':
        action = request.form['patient_action']
        if action == 'login':
            return redirect(url_for('login_patient'))  # Redirect to the patient login page
        elif action == 'register':
            return redirect(url_for('register_patient'))  # Redirect to the patient registration page
    return render_template('Patients/patient_selection.html')

@app.route('/register_patient_page', methods=['GET'])
def register_patient_page():
    return render_template('Patients/register_patient.html')  # Registration page

@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        weight = request.form.get('weight')  # Optional field
        bloodgroup = request.form.get('bloodgroup')  # Optional field
        phone = request.form['phone']
        address = request.form['address']
        email = request.form['email']
        password = request.form['password']
        problem = request.form['problem']
        bp = request.form['BP']
        # If "Others" is selected, take the input from the other field
        if problem == "Others (please specify)":
            problem = request.form.get('other_problem', '')
        
        # Hash the password
        hashed_password = generate_password_hash(password,method='pbkdf2:sha256')

        # Create a new Patient instance
        new_patient = Patient(
            name=name,
            age=age,
            gender=gender,
            weight=weight,
            bloodgroup=bloodgroup,
            phone=phone,
            address=address,
            email=email,
            password=hashed_password,  # Store the hashed password
            problem=problem,
            bloodpressure = bp
        )
        new_user = LogginedPatient(
            status = "Logged-out"
        )
        # Add the new patient to the database
        db.session.add(new_user)
        db.session.add(new_patient)
        db.session.commit()

        return redirect(url_for('patient_selection'))  # Redirect back to the selection page

    health_problems = HEALTH_PROBLEMS  # Pass health problems to the template
    return render_template('Patients/register_patient.html', health_problems=health_problems)

@app.route('/login_patient_page', methods=['GET'])
def login_patient_page():
    return render_template('Patients/login_patient.html')  # Login page

@app.route('/login_patient', methods=['GET', 'POST'])
def login_patient():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch the patient by email
        patient = Patient.query.filter_by(email=email).first()
        patient_id = patient.patient_id
        User = LogginedPatient.query.filter_by(patient_id=patient_id).first()

        # Check if patient exists and verify password
        if User and check_password_hash(patient.password, password):
            User.status = "Loggined"
            db.session.commit()
            return redirect(url_for('patient_dashboard', patient_id = patient_id))  # Redirect to patient dashboard

    return render_template('Patients/login_patient.html')  # Render login page for GET requests

@app.route('/patient_dashboard')
def patient_dashboard():
    patient_id = request.args.get('patient_id')

    if not patient_id:
        return redirect(url_for('login_patient'))
    
    User = LogginedPatient.query.filter_by(patient_id=patient_id).first()
    if not User or User.status != "Loggined":
        return redirect(url_for('login_patient'))

    patient = Patient.query.get(patient_id)
    if not patient:
        return redirect(url_for('login_patient'))
    return render_template('Patients/patient_dashboard.html', patient=patient)

@app.route('/view_profile')
def view_profile():
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return redirect(url_for('login_patient'))
    
    User = LogginedPatient.query.filter_by(patient_id=patient_id).first()
    if not User or User.status != "Loggined":
        return redirect(url_for('login_patient'))

    patient = Patient.query.get(patient_id)  # Fetch patient details
    if not patient:
        return redirect(url_for('patient_dashboard'))  # Redirect if patient not found

    return render_template('Patients/view_profile.html', patient=patient)  # Pass patient to the template

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return redirect(url_for('login_patient'))

    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        date = request.form.get('date')

        # Validate the date (ensure it's in the future)
        if datetime.strptime(date, '%Y-%m-%d').date() < datetime.today().date():
            return redirect(url_for('book_appointment', patient_id=patient_id))

        doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
        patient = Patient.query.filter_by(patient_id=patient_id).first()

        if not doctor:
            return redirect(url_for('book_appointment', patient_id=patient_id))

        # Create a new appointment
        new_appointment = Appointment(patient_id=patient_id, doctor_id=doctor_id, date=date, room_no=doctor.room_no,doctor_name = doctor.name,patient_problem = patient.problem,patient_name = patient.name)
        db.session.add(new_appointment)
        
        db.session.commit()
        return redirect(url_for('patient_dashboard', patient_id=patient_id))

    # Fetch doctors to populate the select options
    doctors = Doctor.query.all()
    return render_template('Patients/book_appointment.html', patient_id=patient_id, doctors=doctors)

@app.route('/view_appointments')
def view_appointments():
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return redirect(url_for('login_patient'))

    # Fetch the appointments for the logged-in patient
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()

    return render_template('Patients/view_appointments.html', appointments=appointments,patient_id = patient_id)

@app.route('/AboutUs')
def AboutUs():
    patient_id = request.args.get('patient_id')
    return render_template('Patients/about.html',patient_id = patient_id)
@app.route('/ContactUs', methods=['GET', 'POST'])
def ContactUs():
    patient_id = request.args.get('patient_id')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact = request.form['phone']
        feedback = request.form['feedback']
        
        new_feedback = Feedback(
            name = name,
            email = email,
            phone = contact,
            feedback = feedback
        )
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(url_for('ContactUs'))
    return render_template('Patients/contact.html',patient_id = patient_id)
@app.route('/Facilities')
def Facilities():
    patient_id = request.args.get('patient_id')
    return render_template('Patients/facilities.html',patient_id = patient_id)
@app.route('/Departments')
def Departments():
    patient_id = request.args.get('patient_id')
    return render_template('Patients/departments.html',patient_id = patient_id)


# =======================
# Admin Routes
# =======================
@app.route('/admin_selection', methods=['GET', 'POST'])
def admin_selection():
    if request.method == 'POST':
        action = request.form['admin_action']
        if action == 'login':
            return redirect(url_for('admin_login')) 
        elif action == 'register':
            return redirect(url_for('register_admin'))  # Ensure this points to the correct route
    return render_template('Admin/admin_selection.html')

@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        admin_password = request.form['admin_password']
        hashed_password = generate_password_hash(admin_password,method='pbkdf2:sha256')
        new_admin = Admin(admin_id=admin_id, admin_password=hashed_password)
        new_user = LogginedAdmin(admin_id = admin_id,status="Logged-out")
        db.session.add(new_admin)
        db.session.add(new_user)

        db.session.commit()

        return redirect(url_for('admin_login'))  # Correct redirection

    return render_template('Admin/register_admin.html')  # Ensure this template exists

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        admin = Admin.query.filter_by(admin_id=id).first()
        User = LogginedAdmin.query.filter_by(admin_id=admin.admin_id).first()

        if admin and check_password_hash(admin.admin_password, password): 
            User.status = "Loggined"
            db.session.commit()
            return redirect(url_for('admin_dashboard',admin_id=admin.admin_id))  # Redirect to admin dashboard
            
        return redirect(url_for('admin_login'))  # Redirect back to the login page

    return render_template('Admin/admin_login.html') 

@app.route('/view_doctor_requests', methods=['GET'])
def view_doctor_requests():
    doctor_requests = DoctorRequest.query.filter_by(status='pending').all()  # Adjust this query as needed
    return render_template('Admin/view_doctor_requests.html', doctor_requests=doctor_requests)



@app.route('/approve_doctor_request/<int:request_id>', methods=['GET'])
def approve_doctor_request(request_id):
    doctor_request = DoctorRequest.query.get(request_id)
    Randompassword = generate_password()
    hashed_password = generate_password_hash(Randompassword, method='pbkdf2:sha256')

    if doctor_request:
        # Create a new Doctor instance with profile picture and resume
        new_doctor = Doctor(
            name=doctor_request.name,
            specialization=doctor_request.specialization,
            phone=doctor_request.phone,
            email=doctor_request.email,
            password= hashed_password,  # Already hashed
            profile_picture_path=doctor_request.profile_picture,  # Include profile picture
            resume_path=doctor_request.resume, # Include resume
            status="Approved"
        )
        new_user = LogginedDoctor(
            status="Logged-out"
        )
        db.session.add(new_user)
        db.session.add(new_doctor)
        doctor_request.status = "Approved"  # Update status to approved
        db.session.commit()
        body = "Email: "+doctor_request.email+"\nPassword: \""+Randompassword+"\"\nTeam Apollo Hospital\n"
        send_email(doctor_request.email,"Account Verification","Your Account is Verified now you can login using your credentials:- \n",body)
    return redirect(url_for('admin_dashboard'))
@app.route('/reject_doctor_request/<int:request_id>', methods=['POST'])
def reject_doctor_request(request_id):
    doctor_request = DoctorRequest.query.get(request_id)
    doctor_request.status = "Rejected"  # Update status to approved
    send_email(doctor_request.email,"Account Request Rejected","Your Account is not Approved.","You can try again after 15 days.")

    if doctor_request:
        db.session.delete(doctor_request)  # Remove the request
        db.session.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    admin_id = request.args.get('admin_id')  # Get the admin_id from the query parameters

    return render_template('Admin/admin_dashboard.html',admin_id = admin_id)

@app.route('/view_feedback')
def view_feedback():
    # Query the Feedback table to get all feedback records
    feedback_records = Feedback.query.all()
    
    # Render the feedback in the template
    return render_template('Admin/view_feedback.html', feedback=feedback_records)

@app.route('/mark_feedback_done/<int:feedback_id>', methods=['POST'])
def mark_feedback_done(feedback_id):
    # Query the feedback entry
    feedback_item = Feedback.query.get(feedback_id)

    if feedback_item and feedback_item.status == "Pending":
        # Send an email to the patient
        subject = "Thank You for Your Feedback"
        message = f"Dear {feedback_item.name},\n\nThank you for your feedback! We appreciate your input and will use it to improve our services.\n\nBest regards,\n"
        recipient = feedback_item.email
        last = "Team Apollo Hospital"
        # Assuming send_email is a function you've defined to handle email sending
        send_email(recipient, subject, message,last )
        feedback_item.status = "Done"
        db.session.commit()
    return redirect(url_for('view_feedback'))
# =======================
# Doctor Routes
# =======================

@app.route('/doctor_selection', methods=['GET', 'POST'])
def doctor_selection():
    if request.method == 'POST':
        action = request.form['doctor_action']
        if action == 'login':
            return redirect(url_for('doctor_login')) 
        elif action == 'register':
            return redirect(url_for('register_doctor'))  # Ensure this points to the correct route
    return render_template('Doctors/Doctor_selection.html')

@app.route('/register_doctor', methods=['GET', 'POST'])
def register_doctor():
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        phone = request.form['phone']
        email = request.form['email']

        # Handle profile picture and resume upload
        profile_picture = request.files['profile_picture']
        resume = request.files['resume']

        # Secure filenames
        profile_picture_filename = secure_filename(profile_picture.filename)
        resume_filename = secure_filename(resume.filename)

        # Define paths to save the uploaded files
        profile_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_picture_filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)

        # Save the uploaded files to the specified paths
        profile_picture.save(profile_picture_path)
        resume.save(resume_path)

        # Create a new DoctorRequest instance with the form data and file paths
        new_request = DoctorRequest(
            name=name,
            specialization=specialization,
            phone=phone,
            email=email,
            profile_picture=f'uploads/{profile_picture_filename}',  # Save the relative path
            resume=f'uploads/{resume_filename}'  # Save the relative path
        )

        # Add the new request to the database
        db.session.add(new_request)
        db.session.commit()
        
        send_email(
            email,
            "Registration Successful",
            f"Dr. {name}, you have successfully registered to work in our hospital.\nPlease wait for our approval.\n",
            "Team Apollo Hospital"
        )

        return redirect(url_for('home'))

    # Render the registration form
    return render_template('Doctors/register_doctor.html')
universalPassword = ""
@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch the doctor by email
        doctor = Doctor.query.filter_by(email=email).first()

        if not doctor:
            return render_template('Doctors/doctor_login.html')

        doctor_id = doctor.doctor_id

        User = LogginedDoctor.query.filter_by(doctor_id=doctor_id).first()

        # Check if doctor exists and verify password
        if User and check_password_hash(doctor.password, password):
            global universalPassword
            universalPassword = password
            User.status = "Loggined"
            db.session.commit()  # Commit the changes to the database
            return redirect(url_for('doctor_dashboard', doctor_id=doctor_id))  
    return render_template('Doctors/doctor_login.html')

@app.route('/doctor_dashboard')
def doctor_dashboard():
    doctor_id = request.args.get('doctor_id')
    if not doctor_id:
        return redirect(url_for('doctor_login'))

    User = LogginedDoctor.query.filter_by(doctor_id=doctor_id).first()
    if not User or User.status != "Loggined":
        return redirect(url_for('doctor_login'))

    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
    if not doctor:
        return redirect(url_for('doctor_login'))
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.date.asc()).all()

    return render_template('Doctors/doctor_dashboard.html', doctor = doctor, appointments=appointments)

@app.route('/view_doctor_profile')
def view_doctor_profile():
    doctor_id = request.args.get('doctor_id')
    if not doctor_id:
        return redirect(url_for('doctor_login'))

    # Fetch the logged-in doctor
    logged_doctor = LogginedDoctor.query.filter_by(doctor_id=doctor_id).first()
    if not logged_doctor or logged_doctor.status != "Loggined":
        return redirect(url_for('doctor_login'))

    # Fetch the doctor details
    doctor = Doctor.query.get(doctor_id)  # Replace 'Doctor' with your actual model name
    if not doctor:
        return redirect(url_for('doctor_dashboard'))  # Redirect if doctor not found

    return render_template('Doctors/view_doctor_profile.html', doctor=doctor)  # Pass doctor to the template
@app.route('/doctor_appointments')
def doctor_appointments():
    doctor_id = request.args.get('doctor_id')
    if not doctor_id:
        return redirect(url_for('doctor_login'))

    # Fetch upcoming appointments for the logged-in doctor
    upcoming_appointments = Appointment.query.filter_by(doctor_id=doctor_id).filter(Appointment.date >= date.today()).all()

    return render_template('Doctors/doctor_appointments.html', appointments=upcoming_appointments,doctor_id = doctor_id)

@app.route('/DoctorAboutUs')
def DoctorAboutUs():
    doctor_id = request.args.get('doctor_id')
    return render_template('Doctors/DoctorAbout.html',doctor_id = doctor_id)
@app.route('/change_password_page/<doctor_id>', methods=['GET', 'POST'])
def change_password_page(doctor_id):
    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
    if not doctor:
        return redirect(url_for('doctor_dashboard', doctor_id=doctor_id))

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        if not (check_password_hash(doctor.password, old_password)) or (new_password != confirm_new_password):
            return redirect(url_for('doctor_dashboard', doctor_id=doctor_id))  # Or show an error message

        # Update password in the database
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        global universalPassword
        universalPassword = new_password
        doctor.password = hashed_password
        db.session.commit()
        subject = "Password Changed"
        message = f"Hello Dr. {doctor.name},\n\nHere are your Updated Login Details:\n" \
                f"Email: {doctor.email}\nPassword: \"{universalPassword}\"\n\n" \
                "Please keep your credentials secure.\n\nBest Regards.\n"
        send_email(doctor.email, subject, message, "Team Apollo Hospital")

        return redirect(url_for('doctor_dashboard', doctor_id=doctor_id))

    return render_template('change_password.html', doctor=doctor)

@app.route('/forgot_password/<int:doctor_id>')
def forgot_password(doctor_id):
    # Query the doctor based on the ID
    doctor = Doctor.query.get(doctor_id)
    
    # Check if the doctor exists
    if not doctor:
        return redirect(url_for('doctor_dashboard', doctor_id=doctor_id))
    print(universalPassword)
    # Prepare the email content
    subject = "Password Recovery"
    message = f"Hello Dr. {doctor.name},\n\nHere are your login details:\n" \
              f"Email: {doctor.email}\nPassword: \"{universalPassword}\"\n\n" \
              "Please keep your credentials secure.\n\nBest Regards.\n"
    
    # Send the email
    send_email(doctor.email, subject, message, "Team Apollo Hospital")
    
    return redirect(url_for('doctor_dashboard', doctor_id=doctor_id))

@app.route('/upload_prescription/<int:doctor_id>/<int:appointment_id>', methods=['POST'])
def upload_prescription(doctor_id, appointment_id):
    appointments = Appointment.query.get(appointment_id)
    doctor = Doctor.query.get(doctor_id)
    patient = Patient.query.get(appointments.patient_id)
    if not appointments or not doctor:
        return redirect(url_for('doctor_dashboard', doctor=doctor,appointments=appointments))

    # Handle the uploaded file
    if 'prescription' in request.files:
        file = request.files['prescription']
        if file.filename != '':
            # Save the file securely
            filename = secure_filename(file.filename)
            filepath = os.path.join('static/uploads', filename)
            file.save(filepath)
            
            # Update the appointment's prescription path in the database
            appointments.prescription = filepath
            db.session.commit()
    send_email(patient.email,"Prescription Uploaded","Your Doctor has uploaded the prescription.\nPlease Login and check it.","Team Apollo Hospital")
    # Redirect back to the doctor's dashboard
    return redirect(url_for('doctor_dashboard', doctor_id=doctor_id,appointments=appointments))
@app.route('/update_prescription/<int:appointment_id>', methods=['POST'])
def update_prescription(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = Patient.query.get(appointment.patient_id) if appointment else None 

    if 'prescription' not in request.files:
        return redirect(url_for('doctor_appointments', doctor_id=appointment.doctor_id))

    file = request.files['prescription']
    
    if file.filename == '':
        return redirect(url_for('doctor_appointments', doctor_id=appointment.doctor_id))

    # Save the new prescription file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Update the appointment's prescription field
    appointment.prescription = file_path
    db.session.commit()
    upcoming_appointments = Appointment.query.filter_by(doctor_id=appointment.doctor_id).filter(Appointment.date >= date.today()).all()
    if patient:
        send_email(
            patient.email,
            "Prescription Updated",
            "Your Doctor has updated the prescription.\nPlease login and check it.",
            "Team Apollo Hospital"
        )
    return redirect(url_for('doctor_appointments', doctor_id=appointment.doctor_id,appointment = upcoming_appointments))

# =======================
# logout
# =======================

@app.route('/logout_patient')
def logout_patient():
    patient_id = request.args.get('patient_id')
    User = LogginedPatient.query.filter_by(patient_id=patient_id).first()
    User.status = "Logged-out"
    db.session.commit()
    return redirect(url_for('home'))  # Redirect to home page

@app.route('/logout_doctor')
def logout_doctor():
    doctor_id = request.args.get('doctor_id')
    User = LogginedDoctor.query.filter_by(doctor_id=doctor_id).first()
    # Check if the doctor exists
    if User:
        User.status = "Logged-out"  # Update the status to 'Logged-out'
        db.session.commit()  # Commit the changes
        return redirect(url_for('home'))
    else:
        return redirect(url_for('doctor_login'))

@app.route('/logout_admin')
def logout_admin():
    admin_id = request.args.get('admin_id')
    print(admin_id)
    User = LogginedAdmin.query.filter_by(admin_id=admin_id).first()
    if User:
        User.status = "Logged-out"  # Update the status to 'Logged-out'
        db.session.commit()  # Commit the changes
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

import matplotlib.pyplot as plt
import numpy as np

def generate_graphs():
    # Data for plotting
    x = np.arange(1, 11)
    y1 = np.random.randint(1, 100, size=10)  # Random patient visits for 10 days
    y2 = np.random.randint(1, 100, size=10)  # Random treatment outcomes

    # Creating the first graph (Patient Visits)
    plt.figure(figsize=(10, 15))
    plt.subplot(3, 1, 1)
    plt.bar(x, y1, color='#004d40')
    plt.title('Patient Visits Over 10 Days', fontsize=16, color='#004d40', pad=20)
    plt.xlabel('Days', fontsize=14)
    plt.ylabel('Number of Patients', fontsize=14)
    plt.xticks(x)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Creating the second graph (Treatment Outcomes)
    plt.subplot(3, 1, 2)
    plt.plot(x, y2, marker='o', color='#00796b', linestyle='-', linewidth=2)
    plt.title('Treatment Outcomes', fontsize=16, color='#004d40', pad=20)
    plt.xlabel('Days', fontsize=14)
    plt.ylabel('Outcome Score', fontsize=14)
    plt.xticks(x)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Data for the pie chart (Facilities Provided)
    facilities = ['Emergency Care', 'Inpatient Services', 'Outpatient Services', 'Surgical Services', 'Diagnostic Imaging']
    sizes = [25, 35, 20, 15, 5]

    # Define colors using a dark teal palette
    pie_colors = ['#004d40', '#00796b', '#009688', '#80cbc4', '#b2dfdb']

    # Creating the third graph (Facilities Pie Chart)
    plt.subplot(3, 1, 3)
    wedges, texts, autotexts = plt.pie(
        sizes, labels=None, colors=pie_colors, startangle=140, explode=(0.1, 0, 0, 0, 0), autopct='%1.1f%%'
    )
    for autotext in autotexts:
        autotext.set_color('red')
    # Positioning labels around the pie chart with adjusted spacing
    label_distance = 1.4  # Increased radial distance for clearer label spacing
    for i, wedge in enumerate(wedges):
        angle = (wedge.theta1 + wedge.theta2) / 2.0
        x = label_distance * np.cos(np.deg2rad(angle))
        y = label_distance * np.sin(np.deg2rad(angle))

        # Custom positioning for specific labels
        if facilities[i] == 'Diagnostic Imaging':
            x -= 0.2  # Move it further to the left
        elif facilities[i] == 'Surgical Services':
            y -= 0.2  # Move it slightly downwards

        # Adjust text alignment based on angle
        ha = 'left' if angle < 90 or angle > 270 else 'right'
        
        # Plot label with custom positioning
        plt.text(x, y, facilities[i], ha=ha, va='center', color='#004d40', fontsize=10, fontweight='bold')

    plt.axis('equal')
    plt.title('Facilities Provided', fontsize=16, color='#004d40', pad=35)  # Additional padding for the title

    # Save all graphs in a single row with a consistent style
    plt.tight_layout(rect=[0, 0.1, 1, 1])  # Adjust layout to ensure enough space for labels
    plt.savefig('static/all_charts.png', bbox_inches='tight', dpi=300)
    # plt.show()

generate_graphs()

if __name__ == '__main__':
    with app.app_context():
        generate_graphs()
        # db.drop_all()
        db.create_all()  # Creates the tables in the database
        if not (Doctor.query.first() or Patient.query.first() or Admin.query.first()):
            populate_db()
    app.run(debug=True)



