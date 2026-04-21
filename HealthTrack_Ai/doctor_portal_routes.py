from flask import render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from datetime import datetime, timedelta
import traceback

def doctor_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'doctor_id' not in session:
            flash('Please login as doctor to access this page', 'warning')
            return redirect(url_for('doctor_login'))
        return f(*args, **kwargs)
    return decorated_function

def setup_doctor_routes(app, db, doctor_auth, doctor_appointment_routes):
    
    @app.route('/doctor')
    def doctor_home():
        return render_template('doctor/index.html')
    
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
            
            # Check password confirmation
            if data['password'] != request.form.get('confirm_password'):
                flash('Passwords do not match', 'danger')
                return render_template('doctor/register.html')
            
            success, message, doctor_id = doctor_auth.register_doctor(data)
            
            if success:
                flash('Doctor registration successful! Please login.', 'success')
                return redirect(url_for('doctor_login'))
            else:
                flash(message, 'danger')
        
        return render_template('doctor/register.html')
    
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
        
        return render_template('doctor/login.html')
    
    @app.route('/doctor/dashboard')
    @doctor_login_required
    def doctor_dashboard():
        doctor_id = session['doctor_id']
        
        # Get stats
        stats = doctor_appointment_routes.get_appointment_stats(doctor_id)
        
        # Get today's appointments
        today_appointments = doctor_appointment_routes.get_doctor_appointments(doctor_id, 'today')
        
        # Get upcoming appointments
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
        
        # Format time
        if hasattr(appointment['appointment_time'], 'seconds'):
            total_seconds = appointment['appointment_time'].seconds
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            ampm = 'AM' if hours < 12 else 'PM'
            hour12 = hours if hours <= 12 else hours - 12
            if hour12 == 0:
                hour12 = 12
            appointment['appointment_time_str'] = f"{hour12:02d}:{minutes:02d} {ampm}"
        
        return render_template('doctor/appointment_detail.html', appointment=appointment)
    
    @app.route('/doctor/update-appointment/<int:appointment_id>', methods=['POST'])
    @doctor_login_required
    def doctor_update_appointment(appointment_id):
        doctor_id = session['doctor_id']
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        success, message = doctor_appointment_routes.update_appointment_status(
            appointment_id, doctor_id, status, notes
        )
        
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
            
            db.connection.commit()
            cursor.close()
            
            # Update session
            session['doctor_name'] = data['name']
            session['doctor_specialization'] = data['specialization']
            session['doctor_hospital'] = data['hospital']
            
            flash('Profile updated successfully', 'success')
            
        except Exception as e:
            db.connection.rollback()
            cursor.close()
            flash(f'Error updating profile: {str(e)}', 'danger')
        
        return redirect(url_for('doctor_profile_page'))
    
    @app.route('/doctor/availability', methods=['GET', 'POST'])
    @doctor_login_required
    def doctor_availability():
        doctor_id = session['doctor_id']
        
        if request.method == 'POST':
            is_available = request.form.get('is_available') == 'on'
            
            cursor = db.get_connection().cursor()
            cursor.execute("""
                UPDATE doctors SET is_available = %s WHERE id = %s
            """, (is_available, doctor_id))
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
        return redirect(url_for('doctor_login'))