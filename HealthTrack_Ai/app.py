from flask_mail import Mail, Message
from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
from flask_bcrypt import Bcrypt
from functools import wraps
import pickle
import numpy as np
from datetime import datetime, timedelta
import os
import traceback
import json
import secrets
import re

from config import Config
from database import Database
from auth import Auth
from doctor_routes import DoctorRoutes
from appointment_routes import AppointmentRoutes
from prediction_routes import PredictionRoutes
from doctor_auth import DoctorAuth
from doctor_appointment_routes import DoctorAppointmentRoutes

app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)

# Initialize mail
mail = Mail(app)

# Initialize database
db = Database()
doctor_auth = DoctorAuth(db)
doctor_appointment_routes = DoctorAppointmentRoutes(db)

# Load ML models
model = None
symptom_names = None
label_encoder = None

def load_models():
    global model, symptom_names, label_encoder
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'models', 'disease_prediction_model.pkl')
        symptoms_path = os.path.join(os.path.dirname(__file__), 'models', 'symptom_names.pkl')
        encoder_path = os.path.join(os.path.dirname(__file__), 'models', 'disease_label_encoder.pkl')
        
        if os.path.exists(model_path) and os.path.exists(symptoms_path) and os.path.exists(encoder_path):
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            with open(symptoms_path, 'rb') as f:
                symptom_names = pickle.load(f)
            with open(encoder_path, 'rb') as f:
                label_encoder = pickle.load(f)
            print("✓ Models loaded successfully")
        else:
            print("! Model files not found, using rule-based prediction")
            model = None
            symptom_names = []
            label_encoder = None
            
    except Exception as e:
        print(f"! Error loading models: {e}")
        model = None
        symptom_names = []
        label_encoder = None

# Login required decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'doctor_id' not in session:
            flash('Please login as doctor to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Template context processor
@app.context_processor
def utility_processor():
    def get_current_endpoint():
        return request.endpoint
    return dict(get_current_endpoint=get_current_endpoint, now=datetime.now)

@app.template_filter('format_time')
def format_time_filter(value):
    if value is None:
        return "Time not specified"
    if isinstance(value, timedelta):
        total_seconds = value.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        ampm = 'AM' if hours < 12 else 'PM'
        hour12 = hours if hours <= 12 else hours - 12
        if hour12 == 0:
            hour12 = 12
        return f"{hour12:02d}:{minutes:02d} {ampm}".lstrip('0')
    if hasattr(value, 'strftime'):
        try:
            return value.strftime('%I:%M %p').lstrip('0')
        except:
            return str(value)
    return str(value)

def send_email(to, subject, template, **kwargs):
    if not app.config['MAIL_PASSWORD']:
        print(f"⚠️ Email not sent: MAIL_PASSWORD not configured. Would send to {to}")
        return False
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        msg.body = render_template(f'email/{template}.txt', **kwargs)
        msg.html = render_template(f'email/{template}.html', **kwargs)
        mail.send(msg)
        print(f"✅ Email sent to {to}")
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

# ============================================
# MAIN ROUTES
# ============================================

@app.route('/')
def index():
    total_appointments = 0
    recent_appointments = []
    available_doctors = 0
    total_patients = 0
    
    try:
        cursor = db.get_connection().cursor(dictionary=True)
        
        # Get total patients – safely handle missing columns
        try:
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = TRUE")
            result = cursor.fetchone()
            total_patients = result['count'] if result else 0
        except:
            cursor.execute("SELECT COUNT(*) as count FROM users")
            result = cursor.fetchone()
            total_patients = result['count'] if result else 0
        
        # Get available doctors
        try:
            cursor.execute("SELECT COUNT(*) as count FROM doctors WHERE is_available = TRUE")
            result = cursor.fetchone()
            available_doctors = result['count'] if result else 0
        except:
            cursor.execute("SELECT COUNT(*) as count FROM doctors")
            result = cursor.fetchone()
            available_doctors = result['count'] if result else 0
        
        if 'user_id' in session:
            cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE user_id = %s", (session['user_id'],))
            result = cursor.fetchone()
            total_appointments = result['count'] if result else 0
            
            cursor.execute("""
                SELECT a.*, d.name as doctor_name, d.specialization, d.hospital 
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.id
                WHERE a.user_id = %s 
                ORDER BY a.appointment_date DESC, a.appointment_time DESC 
                LIMIT 5
            """, (session['user_id'],))
            recent_appointments = cursor.fetchall()
        
        cursor.close()
    except Exception as e:
        print(f"Dashboard error: {e}")
        flash("Unable to load dashboard data. Please check database connection.", "danger")
    
    return render_template('index.html', 
                         total_appointments=total_appointments,
                         available_doctors=available_doctors,
                         ai_accuracy=94,
                         total_patients=total_patients,
                         recent_appointments=recent_appointments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        auth = Auth(db)
        user, error = auth.authenticate(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            session.permanent = True
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash(error or 'Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        doctor = doctor_auth.authenticate_doctor(email, password)
        if doctor:
            session['doctor_id'] = doctor['id']
            session['doctor_name'] = doctor['name']
            session['doctor_email'] = doctor['email']
            session['doctor_specialization'] = doctor['specialization']
            session['doctor_hospital'] = doctor['hospital']
            session.permanent = True
            flash('Doctor login successful!', 'success')
            return redirect(url_for('doctor_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login') + '#doctor-tab')
    # GET request – redirect to main login page with doctor tab active
    return redirect(url_for('login') + '#doctor-tab')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        auth = Auth(db)
        success, message, user_id, verification_token = auth.register(full_name, email, password, phone)
        
        if success:
            verification_link = url_for('verify_email', token=verification_token, _external=True)
            send_email(
                to=email,
                subject="Verify Your HealthTrack AI Email",
                template="verify_email",
                name=full_name,
                verification_link=verification_link
            )
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'danger')
    return render_template('register.html')

@app.route('/doctor/register', methods=['GET', 'POST'])
def doctor_register():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'confirm_password': request.form.get('confirm_password'),
            'specialization': request.form.get('specialization'),
            'hospital': request.form.get('hospital'),
            'qualification': request.form.get('qualification'),
            'timings': request.form.get('timings'),
            'experience_years': request.form.get('experience_years', 0),
            'consultation_fee': request.form.get('consultation_fee', 1000)
        }
        if data['password'] != data['confirm_password']:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register') + '#doctor-reg-tab')
        success, message, doctor_id = doctor_auth.register_doctor(data)
        if success:
            flash('Doctor registration successful! Please login.', 'success')
            return redirect(url_for('login') + '#doctor-tab')
        else:
            flash(message, 'danger')
            return redirect(url_for('register') + '#doctor-reg-tab')
    # GET request – redirect to main registration page with doctor tab active
    return redirect(url_for('register') + '#doctor-reg-tab')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/verify-email/<token>')
def verify_email(token):
    cursor = db.get_connection().cursor()
    cursor.execute("""
        UPDATE users 
        SET email_verified = TRUE, verification_token = NULL 
        WHERE verification_token = %s
    """, (token,))
    if cursor.rowcount > 0:
        db.connection.commit()
        flash('Email verified successfully! You can now login.', 'success')
    else:
        flash('Invalid or expired verification token', 'danger')
    cursor.close()
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        cursor = db.get_connection().cursor(dictionary=True)
        cursor.execute("SELECT id, full_name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            auth = Auth(db)
            reset_token = auth.generate_reset_token(email)
            if reset_token:
                reset_link = url_for('reset_password', token=reset_token, _external=True)
                send_email(
                    to=email,
                    subject="Reset Your HealthTrack AI Password",
                    template="reset_password",
                    name=user['full_name'],
                    reset_link=reset_link
                )
                flash('Password reset link has been sent to your email.', 'info')
            else:
                flash('Unable to process request. Please try again.', 'danger')
        else:
            flash('If an account exists with this email, you will receive a password reset link.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    cursor = db.get_connection().cursor(dictionary=True)
    cursor.execute("""
        SELECT id, full_name, email FROM users 
        WHERE reset_token = %s AND reset_token_expiry > NOW()
    """, (token,))
    user = cursor.fetchone()
    cursor.close()
    if not user:
        flash('Invalid or expired reset token. Please request a new password reset.', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('reset_password.html', token=token)
        
        auth = Auth(db)
        valid_password, message, _ = auth.validate_password(new_password)
        if not valid_password:
            flash(message, 'danger')
            return render_template('reset_password.html', token=token)
        
        password_hash = auth.hash_password(new_password)
        cursor = db.get_connection().cursor()
        cursor.execute("""
            UPDATE users 
            SET password_hash = %s, reset_token = NULL, reset_token_expiry = NULL
            WHERE id = %s
        """, (password_hash, user['id']))
        db.connection.commit()
        cursor.close()
        flash('Password reset successful! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)

# ========== Patient Profile & Change Password ==========
@app.route('/profile')
@login_required
def profile():
    auth = Auth(db)
    user = auth.get_user_by_id(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('profile'))
    
    auth = Auth(db)
    success, message = auth.change_password(session['user_id'], current_password, new_password)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('profile'))

# ============================================
# SYMPTOM CHECKER & PREDICTION
# ============================================
@app.route('/symptom-checker')
@login_required
def symptom_checker():
    return render_template('symptom_checker.html')

@app.route('/predict-disease', methods=['POST'])
@login_required
def predict_disease():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
        selected_symptoms = data.get('symptoms', [])
        prediction_routes = PredictionRoutes(model, symptom_names, label_encoder, db)
        result = prediction_routes.predict(selected_symptoms)
        return jsonify(result)
    except Exception as e:
        print(f"Error in predict_disease: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============================================
# DOCTOR SEARCH & APPOINTMENT ROUTES
# ============================================
@app.route('/find-doctors')
def find_doctors():
    search = request.args.get('search', '')
    specialization = request.args.get('specialization', '')
    availability = request.args.get('availability', '')
    doctor_routes = DoctorRoutes(db)
    doctors = doctor_routes.search_doctors(search, specialization, availability)
    specializations = doctor_routes.get_all_specializations()
    return render_template('find_doctors.html', doctors=doctors, 
                         search=search, specialization=specialization, 
                         availability=availability, specializations=specializations)

@app.route('/doctor/<int:doctor_id>')
def doctor_profile(doctor_id):
    doctor_routes = DoctorRoutes(db)
    doctor = doctor_routes.get_doctor(doctor_id)
    if not doctor:
        flash('Doctor not found', 'danger')
        return redirect(url_for('find_doctors'))
    available_dates = []
    for i in range(1, 8):
        date = datetime.now().date() + timedelta(days=i)
        available_dates.append(date)
    return render_template('doctor_profile.html', doctor=doctor, available_dates=available_dates)

@app.route('/book-appointment/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_appointment(doctor_id):
    doctor_routes = DoctorRoutes(db)
    doctor = doctor_routes.get_doctor(doctor_id)
    if not doctor:
        flash('Doctor not found', 'danger')
        return redirect(url_for('find_doctors'))
    
    if request.method == 'POST':
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        symptoms = request.form.get('symptoms')
        predicted_disease = request.form.get('predicted_disease')
        confidence = request.form.get('confidence')
        
        if not appointment_date or not appointment_time:
            flash('Please select both date and time', 'danger')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
        if not symptoms or len(symptoms.strip()) < 10:
            flash('Please describe your symptoms in detail (at least 10 characters)', 'danger')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
        
        appointment_routes = AppointmentRoutes(db)
        success, message, appointment_id = appointment_routes.book_appointment(
            user_id=session['user_id'],
            doctor_id=doctor_id,
            date=appointment_date,
            time=appointment_time,
            symptoms=symptoms,
            predicted_disease=predicted_disease,
            confidence=confidence
        )
        if success:
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('appointments'))
        else:
            flash(f'Error: {message}', 'danger')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
    
    available_dates = []
    for i in range(1, 8):
        date = datetime.now().date() + timedelta(days=i)
        available_dates.append(date)
    return render_template('book_appointment.html', doctor=doctor, available_dates=available_dates)

@app.route('/appointments')
@login_required
def appointments():
    appointment_routes = AppointmentRoutes(db)
    appointments = appointment_routes.get_user_appointments(session['user_id'])
    today = datetime.now().date()
    grouped = {'today': [], 'upcoming': [], 'cancelled': [], 'past': []}
    for apt in appointments:
        apt_date = apt['appointment_date']
        if apt['status'] == 'cancelled':
            grouped['cancelled'].append(apt)
        elif apt_date == today:
            grouped['today'].append(apt)
        elif apt_date > today:
            grouped['upcoming'].append(apt)
        else:
            grouped['past'].append(apt)
    return render_template('appointments.html', **grouped)

@app.route('/cancel-appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    reason = request.form.get('reason', '')
    appointment_routes = AppointmentRoutes(db)
    success, message = appointment_routes.cancel_appointment(appointment_id, session['user_id'], reason)
    return jsonify({'success': success, 'message': message})

@app.route('/reschedule-appointment/<int:appointment_id>', methods=['POST'])
@login_required
def reschedule_appointment(appointment_id):
    new_date = request.form.get('new_date')
    new_time = request.form.get('new_time')
    appointment_routes = AppointmentRoutes(db)
    success, message = appointment_routes.reschedule_appointment(appointment_id, session['user_id'], new_date, new_time)
    return jsonify({'success': success, 'message': message})

@app.route('/get-available-slots', methods=['POST'])
@login_required
def get_available_slots():
    try:
        doctor_id = request.form.get('doctor_id')
        date = request.form.get('date')
        if not doctor_id or not date:
            return jsonify({'error': 'Missing doctor_id or date'}), 400
        appointment_routes = AppointmentRoutes(db)
        slots = appointment_routes.get_available_slots(int(doctor_id), date)
        return jsonify({'slots': slots})
    except Exception as e:
        print(f"Error in get-available-slots: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/get-doctors-by-specialization', methods=['POST'])
@login_required
def get_doctors_by_specialization():
    specialization = request.form.get('specialization', '')
    doctor_routes = DoctorRoutes(db)
    doctors = doctor_routes.get_doctors_by_specialization(specialization)
    return jsonify({'doctors': doctors})

# ============================================
# DOCTOR PORTAL ROUTES
# ============================================
@app.route('/doctor')
def doctor_home():
    if 'doctor_id' in session:
        return redirect(url_for('doctor_dashboard'))
    return redirect(url_for('login'))

@app.route('/doctor/dashboard')
@doctor_login_required
def doctor_dashboard():
    doctor_id = session['doctor_id']
    stats = doctor_appointment_routes.get_appointment_stats(doctor_id)
    today_appointments = doctor_appointment_routes.get_doctor_appointments(doctor_id, 'today')
    upcoming_appointments = doctor_appointment_routes.get_doctor_appointments(doctor_id, 'upcoming')
    return render_template('doctor/dashboard.html', 
                         stats=stats,
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments)

@app.route('/doctor/appointments')
@doctor_login_required
def doctor_appointments():
    doctor_id = session['doctor_id']
    filter_type = request.args.get('filter', 'all')
    appointments = doctor_appointment_routes.get_doctor_appointments(doctor_id, filter_type)
    return render_template('doctor/appointments.html', 
                         appointments=appointments,
                         current_filter=filter_type)

@app.route('/doctor/appointment/<int:appointment_id>')
@doctor_login_required
def doctor_appointment_detail(appointment_id):
    doctor_id = session['doctor_id']
    cursor = db.get_connection().cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, u.full_name as patient_name, u.email as patient_email, u.phone as patient_phone,
               u.date_of_birth, u.gender
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        WHERE a.id = %s AND a.doctor_id = %s
    """, (appointment_id, doctor_id))
    appointment = cursor.fetchone()
    cursor.close()
    if not appointment:
        flash('Appointment not found', 'danger')
        return redirect(url_for('doctor_appointments'))
    return render_template('doctor/appointment_detail.html', appointment=appointment)

@app.route('/doctor/update-appointment/<int:appointment_id>', methods=['POST'])
@doctor_login_required
def doctor_update_appointment(appointment_id):
    doctor_id = session['doctor_id']
    status = request.form.get('status')
    notes = request.form.get('notes')
    success, message = doctor_appointment_routes.update_appointment_status(appointment_id, doctor_id, status, notes)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('doctor_appointment_detail', appointment_id=appointment_id))

@app.route('/doctor/profile')
@doctor_login_required
def doctor_profile_page():
    doctor_id = session['doctor_id']
    doctor = doctor_auth.get_doctor_by_id(doctor_id)
    if not doctor:
        flash('Doctor profile not found', 'danger')
        return redirect(url_for('doctor_dashboard'))
    return render_template('doctor/profile.html', doctor=doctor)

@app.route('/doctor/profile/update', methods=['POST'])
@doctor_login_required
def doctor_update_profile():
    doctor_id = session['doctor_id']
    data = {
        'name': request.form.get('name'),
        'specialization': request.form.get('specialization'),
        'hospital': request.form.get('hospital'),
        'qualification': request.form.get('qualification'),
        'timings': request.form.get('timings'),
        'experience_years': request.form.get('experience_years'),
        'consultation_fee': request.form.get('consultation_fee'),
        'about': request.form.get('about')
    }
    cursor = db.get_connection().cursor()
    try:
        cursor.execute("""
            UPDATE doctors 
            SET name = %s, specialization = %s, hospital = %s, qualification = %s,
                timings = %s, experience_years = %s, consultation_fee = %s, about = %s
            WHERE id = %s
        """, (data['name'], data['specialization'], data['hospital'], 
              data['qualification'], data['timings'], data['experience_years'],
              data['consultation_fee'], data['about'], doctor_id))
        # Update start_time and end_time from timings
        timings = data['timings']
        if timings:
            time_pattern = r'(\d{1,2}):(\d{2})\s*(AM|PM)'
            matches = re.findall(time_pattern, timings)
            if len(matches) >= 2:
                start_hour, start_min, start_ampm = matches[0]
                end_hour, end_min, end_ampm = matches[1]
                start_hour = int(start_hour)
                end_hour = int(end_hour)
                if start_ampm == 'PM' and start_hour != 12:
                    start_hour += 12
                if end_ampm == 'PM' and end_hour != 12:
                    end_hour += 12
                if start_ampm == 'AM' and start_hour == 12:
                    start_hour = 0
                if end_ampm == 'AM' and end_hour == 12:
                    end_hour = 0
                start_time = f"{start_hour:02d}:{start_min}:00"
                end_time = f"{end_hour:02d}:{end_min}:00"
                cursor.execute("UPDATE doctors SET start_time = %s, end_time = %s WHERE id = %s",
                               (start_time, end_time, doctor_id))
        db.connection.commit()
        cursor.close()
        session['doctor_name'] = data['name']
        session['doctor_specialization'] = data['specialization']
        session['doctor_hospital'] = data['hospital']
        flash('Profile updated successfully', 'success')
    except Exception as e:
        db.connection.rollback()
        cursor.close()
        flash(f'Error updating profile: {str(e)}', 'danger')
    return redirect(url_for('doctor_profile_page'))

@app.route('/doctor/change-password', methods=['POST'])
@doctor_login_required
def doctor_change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('doctor_profile_page'))
    success, message = doctor_auth.change_password(session['doctor_id'], current_password, new_password)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('doctor_profile_page'))

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    full_name = request.form.get('full_name')
    phone = request.form.get('phone')
    date_of_birth = request.form.get('date_of_birth') or None
    gender = request.form.get('gender') or None
    
    auth = Auth(db)
    success, message = auth.update_profile(session['user_id'], full_name, phone, date_of_birth, gender)
    if success:
        flash(message, 'success')
        # Update session name if changed
        session['user_name'] = full_name
    else:
        flash(message, 'danger')
    return redirect(url_for('profile'))

@app.route('/doctor/availability', methods=['GET', 'POST'])
@doctor_login_required
def doctor_availability():
    doctor_id = session['doctor_id']
    if request.method == 'POST':
        is_available = request.form.get('is_available') == 'on'
        cursor = db.get_connection().cursor()
        cursor.execute("UPDATE doctors SET is_available = %s WHERE id = %s", (is_available, doctor_id))
        db.connection.commit()
        cursor.close()
        flash('Availability updated successfully', 'success')
        return redirect(url_for('doctor_availability'))
    cursor = db.get_connection().cursor(dictionary=True)
    cursor.execute("SELECT is_available, timings FROM doctors WHERE id = %s", (doctor_id,))
    doctor = cursor.fetchone()
    cursor.close()
    return render_template('doctor/availability.html', doctor=doctor)

@app.route('/doctor/logout')
def doctor_logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# ============================================
# ERROR HANDLERS
# ============================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message='Page not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500

# ============================================
# RUN APP
# ============================================
if __name__ == '__main__':
    load_models()
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)