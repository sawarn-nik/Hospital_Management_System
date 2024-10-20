from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:1234@localhost/Hospital"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = os.urandom(24)  # Generate a secure random secret key

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

class DoctorRequest(db.Model):
    __tablename__ = 'doctor_requests'
    request_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(50), default="Pending")  # Default to 'Pending'
    password = db.Column(db.String(200),nullable=False)

    
class Doctor(UserMixin, db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    room_no = db.Column(db.String(10), unique=True)
    phone = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200), nullable=False)  # For hashed passwords
    password_update_requested = db.Column(db.Boolean, default=False)
    new_password = db.Column(db.String(100))
    password_verified = db.Column(db.Boolean, default=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))
    update_verified = db.Column(db.String(15))
    
    def get_id(self):
        return str(self.doctor_id)

class PatientDoctor(db.Model):
    __tablename__ = 'patient_doctor'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))

class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), nullable=False)


class Department(db.Model):
    __tablename__ = 'departments'
    department_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    doctors = db.relationship('Doctor', backref='department', lazy=True)

class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.String(100),nullable = False,primary_key = True)
    admin_password = db.Column(db.String(500),nullable = False)

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

@app.route('/login_patient_page', methods=['GET'])
def login_patient_page():
    return render_template('Patients/login_patient.html')  # Login page

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
            problem=problem  # Store the selected problem
        )

        # Add the new patient to the database
        db.session.add(new_patient)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('patient_selection'))  # Redirect back to the selection page

    health_problems = HEALTH_PROBLEMS  # Pass health problems to the template
    return render_template('Patients/register_patient.html', health_problems=health_problems)

@app.route('/login_patient', methods=['GET', 'POST'])
def login_patient():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch the patient by email
        patient = Patient.query.filter_by(email=email).first()

        # Check if patient exists and verify password
        if patient and check_password_hash(patient.password, password):
            # Use session for patient login
            session['patient_id'] = patient.patient_id  # Store patient ID in session
            flash('Login successful!', 'success')
            return redirect(url_for('patient_dashboard'))  # Redirect to patient dashboard
        else:
            flash('Invalid email or password', 'danger')

    return render_template('Patients/login_patient.html')  # Render login page for GET requests

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'patient_id' not in session:
        flash('Please log in to access the dashboard', 'danger')
        return redirect(url_for('login_patient'))

    # Fetch patient details using patient_id stored in session
    patient = Patient.query.get(session['patient_id'])
    return render_template('Patients/patient_dashboard.html', patient=patient)

@app.route('/view_profile')
def view_profile():
    if 'patient_id' not in session:  # Check if the patient is logged in
        flash('You need to be logged in to view your profile.', 'danger')
        return redirect(url_for('login_patient'))  # Redirect if not logged in

    patient = Patient.query.get(session['patient_id'])  # Fetch patient details
    if patient is None:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patient_dashboard'))  # Redirect if patient not found

    return render_template('Patients/view_profile.html', patient=patient)  # Pass patient to the template

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'patient_id' not in session:  # Check if the patient is logged in
        flash('Please log in to book an appointment.', 'danger')
        return redirect(url_for('login_patient'))

    if request.method == 'POST':
        # Logic for booking an appointment
        # You can add your logic here to create a new appointment in the database
        pass

    return render_template('Patients/book_appointment.html')  # Render the booking form

@app.route('/view_appointments')
def view_appointments():
    if 'patient_id' not in session:  # Check if the patient is logged in
        flash('Please log in to view your appointments.', 'danger')
        return redirect(url_for('login_patient'))

    # Fetch the appointments for the logged-in patient
    appointments = Appointment.query.filter_by(patient_id=session['patient_id']).all()  # Fetch appointments
    return render_template('Patients/view_appointments.html', appointments=appointments)

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
        db.session.add(new_admin)
        db.session.commit()
        flash('Admin registered successfully!', 'success')
        return redirect(url_for('admin_login'))  # Correct redirection

    return render_template('Admin/register_admin.html')  # Ensure this template exists

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        admin = Admin.query.filter_by(admin_id=id).first()  # Fetch the admin record
        if admin and check_password_hash(admin.admin_password, password):  # Verify password
            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
            
        flash('Invalid admin ID or password', 'danger')  # Flash message for invalid login
        return redirect(url_for('admin_login'))  # Redirect back to the login page

    return render_template('Admin/admin_login.html') 

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('Admin/admin_dashboard.html')

# =======================
# Doctor Routes
# =======================
@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch the doctor by email
        doctor = Doctor.query.filter_by(email=email).first()

        # Check if doctor exists and verify password
        if doctor and check_password_hash(doctor.password, password):
            # Use session for doctor login
            session['doctor_id'] = doctor.doctor_id  # Store doctor ID in session
            flash('Login successful!', 'success')
            return redirect(url_for('doctor_dashboard'))  # Redirect to doctor dashboard
        else:
            flash('Invalid email or password', 'danger')

    return render_template('Doctors/doctor_login.html')  # Render login page for GET requests

@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'doctor_id' not in session:
        flash('Please log in to access the dashboard', 'danger')
        return redirect(url_for('login_doctor'))

    # Fetch doctor details using doctor_id stored in session
    doctor = Doctor.query.get(session['doctor_id'])
    return render_template('Doctors/doctor_dashboard.html', doctor=doctor)

# =======================
# logout
# =======================

@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))  # Redirect to home page

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates the tables in the database
    app.run(debug=True)
