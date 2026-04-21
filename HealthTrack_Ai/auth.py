# auth.py - Fixed: password reset does NOT auto-verify email
from flask_bcrypt import Bcrypt
import re
from datetime import datetime, timedelta
import secrets

class Auth:
    def __init__(self, db):
        self.db = db
        self.bcrypt = Bcrypt()
        self.common_passwords = {
            'password', '123456', '12345678', '12345', '123456789',
            'qwerty', 'abc123', 'password123', 'admin', 'letmein',
            'welcome', 'monkey', 'dragon', 'master', 'football',
            'iloveyou', 'princess', 'rockyou', 'sunshine', 'password1'
        }
    
    def hash_password(self, password):
        return self.bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password_hash, password):
        return self.bcrypt.check_password_hash(password_hash, password)
    
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone):
        if not phone:
            return True, ""
        pattern = r'^\+?[0-9]{10,15}$'
        if re.match(pattern, phone.replace(' ', '').replace('-', '')):
            return True, ""
        return False, "Phone number must be 10-15 digits"
    
    def validate_password(self, password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long", 1
        if password.lower() in self.common_passwords:
            return False, "Password is too common. Please choose a stronger password", 1
        score = 0
        if re.search(r'[A-Z]', password): score += 1
        if re.search(r'[a-z]', password): score += 1
        if re.search(r'\d', password): score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password): score += 1
        if score < 3:
            return False, "Password must contain at least 3 of: uppercase, lowercase, numbers, special characters", score
        strength = "fair" if score == 3 else "good" if score == 4 else "strong"
        return True, f"Password is {strength}", score
    
    def generate_verification_token(self):
        return secrets.token_urlsafe(32)
    
    def generate_reset_token(self, email):
        cursor = self.db.get_connection().cursor()
        reset_token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=1)
        cursor.execute("UPDATE users SET reset_token = %s, reset_token_expiry = %s WHERE email = %s",
                       (reset_token, expiry, email))
        if cursor.rowcount > 0:
            self.db.connection.commit()
            cursor.close()
            return reset_token
        cursor.close()
        return None
    
    def verify_email(self, token):
        cursor = self.db.get_connection().cursor()
        cursor.execute("UPDATE users SET email_verified = TRUE, verification_token = NULL WHERE verification_token = %s", (token,))
        if cursor.rowcount > 0:
            self.db.connection.commit()
            cursor.close()
            return True
        cursor.close()
        return False
    
    def register(self, full_name, email, password, phone=''):
        if not self.validate_email(email):
            return False, "Invalid email format", None, None
        valid_password, message, strength = self.validate_password(password)
        if not valid_password:
            return False, message, None, None
        if not full_name or len(full_name.strip()) < 2:
            return False, "Full name is required (minimum 2 characters)", None, None
        valid_phone, phone_message = self.validate_phone(phone)
        if not valid_phone:
            return False, phone_message, None, None
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            return False, "Email already registered", None, None
        password_hash = self.hash_password(password)
        verification_token = self.generate_verification_token()
        try:
            cursor.execute("""
                INSERT INTO users (full_name, email, password_hash, phone, verification_token, email_verified, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (full_name.strip(), email, password_hash, phone.strip(), verification_token, False, True))
            user_id = cursor.lastrowid
            self.db.connection.commit()
            cursor.close()
            return True, "Registration successful! Please check your email to verify your account.", user_id, verification_token
        except Exception as e:
            print(f"Registration error: {e}")
            return False, "Registration failed. Please try again.", None, None
    
    def authenticate(self, email, password):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("SELECT id, full_name, email, password_hash, email_verified, is_active FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if not user:
            return None, "Invalid email or password"
        if not user['is_active']:
            return None, "Your account has been deactivated. Please contact support."
        if not user['email_verified']:
            return None, "Please verify your email before logging in. Check your inbox for the verification link."
        if not self.check_password(user['password_hash'], password):
            return None, "Invalid email or password"
        cursor = self.db.get_connection().cursor()
        cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))
        self.db.connection.commit()
        cursor.close()
        return {'id': user['id'], 'full_name': user['full_name'], 'email': user['email']}, None
    
    def reset_password(self, token, new_password):
        """Reset password without auto-verifying email"""
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE reset_token = %s AND reset_token_expiry > NOW()", (token,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            return False, "Invalid or expired reset token"
        valid_password, message, _ = self.validate_password(new_password)
        if not valid_password:
            cursor.close()
            return False, message
        password_hash = self.hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = %s, reset_token = NULL, reset_token_expiry = NULL WHERE id = %s",
                       (password_hash, user['id']))
        self.db.connection.commit()
        cursor.close()
        return True, "Password reset successful! You can now login."
    
    def change_password(self, user_id, old_password, new_password):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            return False, "User not found"
        if not self.check_password(user['password_hash'], old_password):
            cursor.close()
            return False, "Current password is incorrect"
        valid_password, message, _ = self.validate_password(new_password)
        if not valid_password:
            cursor.close()
            return False, message
        password_hash = self.hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))
        self.db.connection.commit()
        cursor.close()
        return True, "Password changed successfully"
    
    def update_profile(self, user_id, full_name, phone, date_of_birth=None, gender=None):
        cursor = self.db.get_connection().cursor()
        valid_phone, phone_message = self.validate_phone(phone)
        if not valid_phone:
            cursor.close()
            return False, phone_message
        try:
            cursor.execute("""
                UPDATE users SET full_name = %s, phone = %s, date_of_birth = %s, gender = %s WHERE id = %s
            """, (full_name.strip(), phone.strip(), date_of_birth, gender, user_id))
            self.db.connection.commit()
            cursor.close()
            return True, "Profile updated successfully"
        except Exception as e:
            cursor.close()
            return False, f"Error updating profile: {str(e)}"
    
    def get_user_by_id(self, user_id):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("SELECT id, full_name, email, phone, date_of_birth, gender, email_verified, is_active, created_at, last_login FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return user