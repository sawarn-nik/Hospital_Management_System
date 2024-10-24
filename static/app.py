from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os

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
    room_no = db.Column(db.Integer, unique=True)
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
class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.String(100),nullable = False,primary_key = True)
    admin_password = db.Column(db.String(500),nullable = False)
class PatientDoctor(db.Model):
    __tablename__ = 'patient_doctor'
    room_id = db.Column(db.Integer, primary_key=True)
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


class DoctorRequest(db.Model):
    __tablename__ = 'doctor_requests'
    request_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(50), default="Pending")  # Default to 'Pending'
    password = db.Column(db.String(200), nullable=False)
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
        Doctor(name="Jame Smith", specialization="Surgeon", phone="0987654322",
               email="jamesmith@example.com", password=generate_password_hash("doc4",method='pbkdf2:sha256'),
               room_no=104, profile_picture_path="uploads/jamesmith.jpg",
               resume_path="uploads/jamesmith_resume.pdf", status="approved")
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
        if not patient:
            flash('Invalid email or password', 'danger')
            return render_template('Patients/login_patient.html')
        patient_id = patient.patient_id
        User = LogginedPatient.query.filter_by(patient_id=patient_id).first()

        # Check if patient exists and verify password
        if User and check_password_hash(patient.password, password):
            # Use session for patient login
            User.status = "Loggined"
            db.session.commit()        
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

@app.route('/view_doctor_requests', methods=['GET'])
def view_doctor_requests():
    # Logic to retrieve doctor requests from the database
    # Assuming there is a status field in the Doctor model to indicate if the request is pending
    doctor_requests = DoctorRequest.query.filter_by(status='pending').all()  # Adjust this query as needed
    
    return render_template('Admin/view_doctor_requests.html', doctor_requests=doctor_requests)

@app.route('/approve_doctor_request/<int:request_id>', methods=['GET'])
def approve_doctor_request(request_id):
    doctor_request = DoctorRequest.query.get(request_id)

    if doctor_request:
        # Create a new Doctor instance with profile picture and resume
        new_doctor = Doctor(
            name=doctor_request.name,
            specialization=doctor_request.specialization,
            phone=doctor_request.phone,
            email=doctor_request.email,
            password=doctor_request.password,  # Already hashed
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

        flash('Doctor request approved successfully!', 'success')
    else:
        flash('Doctor request not found.', 'danger')

    return redirect(url_for('admin_dashboard'))
@app.route('/reject_doctor_request/<int:request_id>', methods=['POST'])
def reject_doctor_request(request_id):
    doctor_request = DoctorRequest.query.get(request_id)
    doctor_request.status = "Rejected"  # Update status to approved

    if doctor_request:
        db.session.delete(doctor_request)  # Remove the request
        db.session.commit()
        flash('Doctor request rejected successfully!', 'success')
    else:
        flash('Doctor request not found.', 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('Admin/admin_dashboard.html')

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
        password = request.form['password']

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

        # Hash the password before saving
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create a new DoctorRequest instance with the form data and file paths
        new_request = DoctorRequest(
            name=name,
            specialization=specialization,
            phone=phone,
            email=email,
            password=hashed_password,  # Store the hashed password
            profile_picture=f'uploads/{profile_picture_filename}',  # Save the relative path
            resume=f'uploads/{resume_filename}'  # Save the relative path
        )

        # Add the new request to the database
        db.session.add(new_request)
        db.session.commit()

        # Flash a success message
        flash('Your registration request has been submitted and is pending approval.', 'success')

        # Redirect to home or another page
        return redirect(url_for('home'))

    # Render the registration form
    return render_template('Doctors/register_doctor.html')

@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch the doctor by email
        doctor = Doctor.query.filter_by(email=email).first()
        if not doctor:
            flash('Invalid email or password', 'danger')
            return render_template('Doctors/doctor_login.html')

        doctor_id = doctor.doctor_id
        User = LogginedDoctor.query.filter_by(doctor_id=doctor_id).first()

        # Check if doctor exists and verify password
        if User and check_password_hash(doctor.password, password):
            User.status = "Loggined"
            db.session.commit()  # Commit the changes to the database
            flash('Login successful!', 'success')
            return redirect(url_for('doctor_dashboard', doctor_id=doctor_id))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('Doctors/doctor_login.html')

@app.route('/doctor_dashboard')
def doctor_dashboard():
    doctor_id = request.args.get('doctor_id')
    if not doctor_id:
        flash('Doctor ID is missing', 'danger')
        return redirect(url_for('doctor_login'))

    User = LogginedDoctor.query.filter_by(doctor_id=doctor_id).first()
    if not User or User.status != "Loggined":
        flash('Please log in to access the dashboard', 'danger')
        return redirect(url_for('doctor_login'))

    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
    if not doctor:
        flash('Doctor not found', 'danger')
        return redirect(url_for('doctor_login'))

    return render_template('Doctors/doctor_dashboard.html', doctor=doctor)

# =======================
# logout
# =======================

@app.route('/logout')
def logout():
    
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))  # Redirect to home page

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates the tables in the database
        if not (Doctor.query.first() or Patient.query.first() or Admin.query.first()):
            populate_db()
    app.run(debug=True)



