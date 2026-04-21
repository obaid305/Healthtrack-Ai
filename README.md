HealthTrack AI - Healthcare Management System

================================================================================

PROJECT OVERVIEW

HealthTrack AI is a comprehensive healthcare management system that integrates an AI-powered symptom checker with automated doctor appointment scheduling. It provides a dual-portal experience for patients and doctors.

================================================================================

FEATURES

Patient Portal:
- User Registration & Login with email verification
- Forgot Password with secure reset tokens
- AI Symptom Checker: 289+ symptoms across 11 disease categories
- Disease Prediction with confidence scores (40-95%) and specialist recommendations
- Find Doctors by name, hospital, or specialization
- View Doctor Profiles (timings, working days, fee, rating)
- Book Appointment with 30-minute slots, double-booking prevention
- View Appointments grouped as Today, Upcoming, Past, Cancelled
- Cancel Appointment (24-hour deadline policy)
- Reschedule Appointment (maximum 2 times)
- Dashboard with statistics

Doctor Portal:
- Doctor Login & Registration
- Dashboard with statistics (today's, upcoming, total patients, completed)
- Manage Appointments with filters (All, Today, Upcoming, Past, Completed, Cancelled)
- View Appointment Details (patient info, symptoms, predicted disease)
- Add Consultation Notes
- Update Appointment Status (Scheduled, Completed, Cancelled)
- Update Profile (specialization, hospital, timings, fee)
- Toggle Availability

System-Wide:
- Secure authentication (Bcrypt password hashing)
- Email verification (24-hour token)
- Password reset (1-hour token)
- SQL injection prevention (parameterized queries)
- Session management (1-hour timeout)
- Responsive medical-themed UI
- Back-to-top button, loading states, error handling

================================================================================

TECHNOLOGY STACK

Backend:    Python 3.13, Flask 3.0, Flask-Bcrypt, Flask-Mail
Database:   MySQL 8.0
Frontend:   HTML5, CSS3, JavaScript, jQuery 3.6, Bootstrap 5.3
Icons:      Font Awesome 6.4
AI/ML:      scikit-learn (Logistic Regression)
Deployment: Waitress, PythonAnywhere / AWS

================================================================================

DATABASE TABLES

- users          : Patient accounts (id, full_name, email, password_hash, phone, email_verified, etc.)
- doctors        : Doctor profiles (id, name, email, specialization, hospital, timings, working_days, fee, rating, etc.)
- appointments   : Appointment bookings (id, user_id, doctor_id, date, time, status, symptoms, predicted_disease, confidence, notes)
- patient_history: Historical records (id, user_id, appointment_id, symptoms, predicted_disease, doctor_notes)
- reviews        : Patient feedback (id, user_id, doctor_id, appointment_id, rating, review)
- notifications  : System notifications (id, user_id, doctor_id, type, title, message, is_read)

================================================================================

INSTALLATION & SETUP

Prerequisites:
- Python 3.13+
- MySQL 8.0+
- Git

Steps:

1. Clone the repository:
   git clone https://github.com/yourusername/HealthTrack_Ai.git
   cd HealthTrack_Ai

2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate      (Linux/Mac)
   venv\Scripts\activate          (Windows)

3. Install dependencies:
   pip install -r requirements.txt

4. Configure environment variables (create .env file):
   SECRET_KEY=your-secret-key
   MYSQL_PASSWORD=your_mysql_password
   MAIL_USERNAME=ai.healthtrack@gmail.com
   MAIL_PASSWORD=your_gmail_app_password
   MAIL_DEBUG=False
   APP_URL=http://localhost:5000

5. Set up the database:
   python database.py

6. Run the application:
   python app.py

Access at: http://127.0.0.1:5000

================================================================================

DEFAULT LOGIN CREDENTIALS

Patient:
Email: testuser@example.com
Password: Test@123

Doctor (all doctors have the same password):
Email examples: dr.shahzad.gul@healthtrack.com, dr.niaz.afridi@healthtrack.com
Password: doctor123

To list all doctor emails, run: python show_doctors.py

================================================================================

PROJECT STRUCTURE

HealthTrack_Ai/
├── app.py
├── config.py
├── database.py
├── auth.py
├── doctor_auth.py
├── appointment_routes.py
├── prediction_routes.py
├── doctor_routes.py
├── doctor_portal_routes.py
├── doctor_appointment_routes.py
├── requirements.txt
├── .env
├── models/
│   ├── disease_prediction_model.pkl
│   ├── symptom_names.pkl
│   └── disease_label_encoder.pkl
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── doctor.css
│   └── js/
│       └── main.js
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── forgot_password.html
    ├── reset_password.html
    ├── symptom_checker.html
    ├── find_doctors.html
    ├── doctor_profile.html
    ├── book_appointment.html
    ├── appointments.html
    ├── error.html
    └── doctor/
        ├── base.html
        ├── dashboard.html
        ├── appointments.html
        ├── appointment_detail.html
        ├── profile.html
        ├── availability.html
        ├── login.html
        └── register.html

================================================================================

TESTING

Run unit and integration tests:
python -m unittest discover tests/

Manual testing: Use browser and default credentials.

================================================================================

CONTRIBUTING

1. Fork the repository.
2. Create a feature branch (git checkout -b feature/amazing-feature).
3. Commit your changes (git commit -m 'Add amazing feature').
4. Push to the branch (git push origin feature/amazing-feature).
5. Open a Pull Request.

================================================================================

LICENSE

Distributed under the MIT License.

================================================================================

CONTACT

Obaid Ullah - obaidy586@gmail.com
Abdul Basit - basitayan25may2006@gmail.com



================================================================================

ACKNOWLEDGEMENTS

Supervisor: Dr. Adnan Iqbal (Associate Professor, School of Computing Sciences, Pak-Austria Fachhochschule)
Pak-Austria Fachhochschule: Institute of Applied Sciences and Technology Mang, Haripur, Pakistan.


================================================================================
