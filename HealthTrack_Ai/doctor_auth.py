# doctor_auth.py - Added change_password method
from flask_bcrypt import Bcrypt
import re
from datetime import datetime, timedelta
import secrets
import json

class DoctorAuth:
    def __init__(self, db):
        self.db = db
        self.bcrypt = Bcrypt()
    
    def hash_password(self, password):
        return self.bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password_hash, password):
        return self.bcrypt.check_password_hash(password_hash, password)
    
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        return True, "Password is valid"
    
    def generate_random_password(self):
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
        return ''.join(secrets.choice(alphabet) for _ in range(12))
    
    def register_doctor(self, data):
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        specialization = data.get('specialization')
        hospital = data.get('hospital')
        qualification = data.get('qualification')
        timings = data.get('timings')
        experience_years = data.get('experience_years', 0)
        consultation_fee = data.get('consultation_fee', 1000)
        
        if not self.validate_email(email):
            return False, "Invalid email format", None
        valid_password, message = self.validate_password(password)
        if not valid_password:
            return False, message, None
        if not name or len(name.strip()) < 2:
            return False, "Doctor name is required", None
        if not specialization:
            return False, "Specialization is required", None
        
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("SELECT id FROM doctors WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            return False, "Email already registered", None
        
        password_hash = self.hash_password(password)
        # Parse timings
        start_time = None
        end_time = None
        if timings:
            time_pattern = r'(\d{1,2}):(\d{2})\s*(AM|PM)'
            matches = re.findall(time_pattern, timings)
            if len(matches) >= 2:
                start_hour = int(matches[0][0])
                start_min = int(matches[0][1])
                start_ampm = matches[0][2]
                end_hour = int(matches[1][0])
                end_min = int(matches[1][1])
                end_ampm = matches[1][2]
                if start_ampm == 'PM' and start_hour != 12: start_hour += 12
                if end_ampm == 'PM' and end_hour != 12: end_hour += 12
                if start_ampm == 'AM' and start_hour == 12: start_hour = 0
                if end_ampm == 'AM' and end_hour == 12: end_hour = 0
                start_time = f"{start_hour:02d}:{start_min:02d}:00"
                end_time = f"{end_hour:02d}:{end_min:02d}:00"
        working_days = json.dumps(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        try:
            cursor.execute("""
                INSERT INTO doctors 
                (name, email, password_hash, specialization, hospital, qualification, 
                 timings, start_time, end_time, working_days, experience_years, consultation_fee, is_available)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            """, (name, email, password_hash, specialization, hospital, qualification,
                  timings, start_time, end_time, working_days, experience_years, consultation_fee))
            doctor_id = cursor.lastrowid
            self.db.connection.commit()
            cursor.close()
            return True, "Doctor registration successful", doctor_id
        except Exception as e:
            self.db.connection.rollback()
            cursor.close()
            return False, f"Registration failed: {str(e)}", None
    
    def authenticate_doctor(self, email, password):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, password_hash, specialization, hospital, is_available FROM doctors WHERE email = %s AND is_active = TRUE", (email,))
        doctor = cursor.fetchone()
        cursor.close()
        if doctor and self.check_password(doctor['password_hash'], password):
            cursor = self.db.get_connection().cursor()
            cursor.execute("UPDATE doctors SET last_login = NOW() WHERE id = %s", (doctor['id'],))
            self.db.connection.commit()
            cursor.close()
            return {'id': doctor['id'], 'name': doctor['name'], 'email': doctor['email'],
                    'specialization': doctor['specialization'], 'hospital': doctor['hospital']}
        return None
    
    def get_doctor_by_id(self, doctor_id):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, email, specialization, hospital, qualification, 
                   timings, start_time, end_time, working_days, experience_years, 
                   consultation_fee, rating, total_reviews, is_available, about
            FROM doctors WHERE id = %s AND is_active = TRUE
        """, (doctor_id,))
        doctor = cursor.fetchone()
        cursor.close()
        if doctor and doctor.get('working_days'):
            try:
                working_days_list = json.loads(doctor['working_days'])
                doctor['working_days_display'] = ', '.join(working_days_list)
            except:
                doctor['working_days_display'] = 'Not specified'
        return doctor
    
    def update_doctor_timings(self, doctor_id, timings):
        cursor = self.db.get_connection().cursor()
        start_time = None
        end_time = None
        if timings:
            time_pattern = r'(\d{1,2}):(\d{2})\s*(AM|PM)'
            matches = re.findall(time_pattern, timings)
            if len(matches) >= 2:
                start_hour = int(matches[0][0])
                start_min = int(matches[0][1])
                start_ampm = matches[0][2]
                end_hour = int(matches[1][0])
                end_min = int(matches[1][1])
                end_ampm = matches[1][2]
                if start_ampm == 'PM' and start_hour != 12: start_hour += 12
                if end_ampm == 'PM' and end_hour != 12: end_hour += 12
                if start_ampm == 'AM' and start_hour == 12: start_hour = 0
                if end_ampm == 'AM' and end_hour == 12: end_hour = 0
                start_time = f"{start_hour:02d}:{start_min:02d}:00"
                end_time = f"{end_hour:02d}:{end_min:02d}:00"
        cursor.execute("UPDATE doctors SET timings = %s, start_time = %s, end_time = %s WHERE id = %s",
                       (timings, start_time, end_time, doctor_id))
        self.db.connection.commit()
        cursor.close()
    
    def update_doctor_profile(self, doctor_id, data):
        cursor = self.db.get_connection().cursor()
        try:
            cursor.execute("""
                UPDATE doctors 
                SET name = %s, specialization = %s, hospital = %s, qualification = %s,
                    timings = %s, experience_years = %s, consultation_fee = %s, about = %s
                WHERE id = %s
            """, (data['name'], data['specialization'], data['hospital'], data['qualification'],
                  data['timings'], data['experience_years'], data['consultation_fee'], data['about'], doctor_id))
            self.db.connection.commit()
            cursor.close()
            return True, "Profile updated successfully"
        except Exception as e:
            self.db.connection.rollback()
            cursor.close()
            return False, f"Error updating profile: {str(e)}"
    
    def change_password(self, doctor_id, current_password, new_password):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("SELECT password_hash FROM doctors WHERE id = %s", (doctor_id,))
        doctor = cursor.fetchone()
        if not doctor:
            cursor.close()
            return False, "Doctor not found"
        if not self.check_password(doctor['password_hash'], current_password):
            cursor.close()
            return False, "Current password is incorrect"
        valid, message = self.validate_password(new_password)
        if not valid:
            cursor.close()
            return False, message
        new_password_hash = self.hash_password(new_password)
        cursor.execute("UPDATE doctors SET password_hash = %s WHERE id = %s", (new_password_hash, doctor_id))
        self.db.connection.commit()
        cursor.close()
        return True, "Password changed successfully"
    
    def update_availability(self, doctor_id, is_available):
        cursor = self.db.get_connection().cursor()
        cursor.execute("UPDATE doctors SET is_available = %s WHERE id = %s", (is_available, doctor_id))
        self.db.connection.commit()
        cursor.close()
        return True