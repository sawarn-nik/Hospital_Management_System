# Hospital Management System
## Project Description
The Hospital Management System is a web-based application developed using Flask, HTML, CSS, and Bootstrap. The system incorporates Role-Based Access Control (RBAC) to ensure secure and efficient hospital operations. It provides distinct interfaces and functionalities for admins, doctors, and patients, showcasing creativity, problem-solving, and technical skills in designing secure user interfaces.

## Key Features
RBAC Implementation
### Admins:
Manage and control hospital operations, including doctor approvals, patient records, and resource allocation.
Access exclusive analytics dashboards for resource utilization.
### Doctors:
View and manage assigned patient data.
Update personal profiles with admin verification.
### Patients:
View personal medical records and treatment schedules securely.
Secure and Functional UI
### Distinct access levels based on user roles.
Secure login and registration systems for admins and doctors.
Alerts and notifications for important actions (e.g., doctor approval, login failures).

## Learning Objectives
This project evaluates the following skills:

## Creativity:

Designing a functional and visually appealing user interface.
Implementing a clear distinction between user roles through tailored dashboards and forms.
Understanding of RBAC:

Structuring the application to grant access based on roles.
Ensuring sensitive data and operations are only accessible to authorized users.
Technical Proficiency:

Building secure backend functionality with Flask.
Integrating RBAC principles into frontend pages using dynamic elements (e.g., role-specific menus).
Using Bootstrap for responsive and interactive designs.

## Technologies Used
### Flask: Backend framework for routing, session management, and database interactions.
### HTML & CSS: For crafting a responsive and accessible UI.
### Bootstrap: For modern styling and layout enhancements.
### SQLite: Lightweight database for storing user and role-based data.

## RBAC in Action
### Admin Role:
Can approve/reject doctor requests.
Access sensitive hospital data like patient records and facility usage.
### Doctor Role:
Restricted to viewing assigned patient details.
Requires admin approval for profile updates.
### Patient Role:
Limited to personal data access, ensuring data privacy.

## Usage
### Admin Login:
Admins can log in using their credentials to access dashboards for managing hospital operations.

### Doctor Registration:
Doctors can submit a registration request, requiring admin approval.

### Role-Specific Dashboards:
Each role sees a tailored dashboard based on their permissions.

## Future Enhancements
### Add multi-factor authentication for enhanced security.
### Implement a logging system to track user actions by role.
### Enhance analytics with interactive charts and graphs.
## File Structure

File Structure
```hospital-management-system/
├── instance
│ ├── hospital.db
├── myenv 
├── static/ # Static files (CSS, JavaScript, images) 
│ ├── js/ # Custom JavaScript files 
│ └── uploads/ │ └── all_charts.png 
├── templates/ # HTML templates 
│ ├── Admin/ 
│ │ ├── admin_dashboard.html 
│ │ ├── admin_login.html 
│ │ ├── admin_selection.html 
│ │ ├── register_admin.html 
│ │ ├── view_doctor_requests.html 
│ │ └── view_feedback.html 
│ ├── Doctors/ 
│ │ ├── doctor_appointments.html 
│ │ ├── doctor_dashboard.html 
│ │ ├── doctor_login.html 
│ │ ├── doctor_selection.html 
│ │ ├── doctor_update.html 
│ │ ├── DoctorAbout.html 
│ │ ├── register_doctor.html 
│ │ └── view_doctor_profile.html 
│ ├── Patients/ 
│ │ ├── about.html 
│ │ ├── book_appointment.html 
│ │ ├── contact.html 
│ │ ├── departments.html 
│ │ ├── facilities.html 
│ │ ├── login_patient.html 
│ │ ├── patient_dashboard.html 
│ │ ├── patient_selection.html 
│ │ ├── register_patient.html 
│ │ ├── view_appointments.html 
│ │ └── view_profile.html 
│ ├── change_password.html 
│ └── index.html 
├── .gitignore 
├── app.py 
├── requirements.txt # Python dependencies 
└── README.md # Documentation


