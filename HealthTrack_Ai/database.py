# database.py
import mysql.connector
from mysql.connector import Error
import json
import time

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                database='healthtrack_ai',
                user='root',
                password=''
            )
            print("✓ Connected to database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.create_database()
    
    def create_database(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password=''
            )
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS healthtrack_ai")
            connection.commit()
            cursor.close()
            connection.close()
            print("✓ Created database")
            time.sleep(1)
            self.connect()
        except Error as e:
            print(f"Error creating database: {e}")
    
    def create_tables(self):
        cursor = self.connection.cursor()
        
        # ============================================
        # CREATE TABLES IN CORRECT ORDER
        # ============================================
        
        # Drop existing tables in reverse order to avoid foreign key issues
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("DROP TABLE IF EXISTS notifications")
            cursor.execute("DROP TABLE IF EXISTS reviews")
            cursor.execute("DROP TABLE IF EXISTS patient_history")
            cursor.execute("DROP TABLE IF EXISTS appointments")
            cursor.execute("DROP TABLE IF EXISTS doctors")
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            print("✓ Dropped existing tables")
        except:
            pass
        
        # 1. Users table
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                date_of_birth DATE,
                gender VARCHAR(10),
                is_active BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(255),
                reset_token VARCHAR(255),
                reset_token_expiry DATETIME,
                last_login TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_active (is_active)
            ) ENGINE=InnoDB
        """)
        print("✓ Created users table")
        self.connection.commit()
        
        # 2. Doctors table
        cursor.execute("""
            CREATE TABLE doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                hospital VARCHAR(255),
                name VARCHAR(100) NOT NULL,
                qualification TEXT,
                specialization VARCHAR(100),
                timings VARCHAR(100),
                start_time TIME,
                end_time TIME,
                working_days JSON,
                consultation_duration INT DEFAULT 30,
                max_appointments_per_day INT DEFAULT 20,
                experience_years INT DEFAULT 0,
                about TEXT,
                consultation_fee DECIMAL(10,2) DEFAULT 1000.00,
                rating DECIMAL(3,2) DEFAULT 4.5,
                total_reviews INT DEFAULT 0,
                is_available BOOLEAN DEFAULT TRUE,
                email VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                INDEX idx_specialization (specialization),
                INDEX idx_available (is_available),
                INDEX idx_email (email)
            ) ENGINE=InnoDB
        """)
        print("✓ Created doctors table")
        self.connection.commit()
        
        # 3. Appointments table
        cursor.execute("""
            CREATE TABLE appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                doctor_id INT NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                status ENUM('scheduled', 'completed', 'cancelled', 'rescheduled', 'no_show') DEFAULT 'scheduled',
                symptoms TEXT,
                predicted_disease VARCHAR(255),
                confidence_score DECIMAL(5,2),
                notes TEXT,
                cancellation_reason TEXT,
                cancellation_time TIMESTAMP NULL,
                reschedule_count INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                cancelled_at TIMESTAMP NULL,
                reminder_sent BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
                UNIQUE KEY unique_appointment (doctor_id, appointment_date, appointment_time),
                INDEX idx_user (user_id),
                INDEX idx_doctor (doctor_id),
                INDEX idx_date (appointment_date),
                INDEX idx_status (status)
            ) ENGINE=InnoDB
        """)
        print("✓ Created appointments table")
        self.connection.commit()
        
        # 4. Patient history table
        cursor.execute("""
            CREATE TABLE patient_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                appointment_id INT,
                symptoms TEXT,
                predicted_disease VARCHAR(255),
                confidence_score DECIMAL(5,2),
                doctor_specialization VARCHAR(100),
                doctor_notes TEXT,
                prescription TEXT,
                follow_up_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL,
                INDEX idx_user (user_id)
            ) ENGINE=InnoDB
        """)
        print("✓ Created patient_history table")
        self.connection.commit()
        
        # 5. Reviews table
        cursor.execute("""
            CREATE TABLE reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                doctor_id INT NOT NULL,
                appointment_id INT,
                rating INT,
                review TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL,
                UNIQUE KEY unique_review (user_id, doctor_id, appointment_id),
                INDEX idx_doctor (doctor_id),
                CONSTRAINT chk_rating CHECK (rating >= 1 AND rating <= 5)
            ) ENGINE=InnoDB
        """)
        print("✓ Created reviews table")
        self.connection.commit()
        
        # 6. Notifications table
        cursor.execute("""
            CREATE TABLE notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                doctor_id INT,
                type ENUM('appointment_reminder', 'appointment_confirmation', 'appointment_cancelled', 'appointment_rescheduled', 'review_request'),
                title VARCHAR(255),
                message TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
                INDEX idx_user (user_id),
                INDEX idx_read (is_read)
            ) ENGINE=InnoDB
        """)
        print("✓ Created notifications table")
        self.connection.commit()
        
        cursor.close()
        
        # Insert doctors
        self.insert_doctors()
        
        print("\n✅ All tables created successfully!")
    
    def insert_doctors(self):
        """Insert all doctors from the provided data"""
        cursor = self.connection.cursor()
        
        # Doctor data
        doctors_data = [
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Shahzad Gul', 'MBBS, FCPS (Medicine), FCPS (Rheumatology), MRCP (Rheumatology)', 'Rheumatologist', '11:00 AM - 02:00 PM', '11:00:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 15, 4.8, 120, 'dr.shahzad.gul@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Niaz Akbar Afridi', 'MBBS, Diploma (Dermatology)', 'Dermatologist', '02:30 PM - 05:30 PM', '14:30:00', '17:30:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 12, 4.6, 85, 'dr.niaz.afridi@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Syed Danish Mehmood', 'MBBS, FCPS (Orthopaedic Surgery)', 'Orthopedic Surgeon', '03:00 PM - 05:00 PM', '15:00:00', '17:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 10, 4.7, 95, 'dr.syed.danish@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Arif Hussain', 'MBBS, FCPS (Paediatrics)', 'Pediatrician', '08:30 AM - 01:00 PM', '08:30:00', '13:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 30, 18, 4.9, 150, 'dr.arif.hussain@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Malik Ehsan', 'MBBS, MD (Neurology)', 'Neurologist', '04:00 PM - 06:00 PM', '16:00:00', '18:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 14, 4.7, 80, 'dr.malik.ehsan@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Abdul Qadeer Khan', 'MBBS, MS (Orthopaedic Surgery)', 'Orthopedic Surgeon', '10:00 AM - 02:00 PM', '10:00:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 30, 16, 4.8, 110, 'dr.abdul.qadeer@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Muhammad Akram Khan', 'MBBS', 'Internal Medicine Specialist', '04:00 PM - 08:00 PM', '16:00:00', '20:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 20, 4.5, 200, 'dr.muhammad.akram@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Mubbashir Ali Baig', 'MBBS, MS Neurosurgery', 'Neuro Surgeon', '04:00 PM - 08:00 PM', '16:00:00', '20:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 9, 4.6, 60, 'dr.mubbashir.baig@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Ayesha Imtiaz', 'MBBS, FCPS (Obstetrics & Gynaecology)', 'Gynecologist', '04:00 PM - 07:00 PM', '16:00:00', '19:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 30, 8, 4.7, 75, 'dr.ayesha.imtiaz@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Ghullam Kibriya', 'MBBS, MCPS Family Medicine, Diploma in Cardiology', 'Cardiologist', '08:30 AM - 02:00 PM', '08:30:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 30, 22, 4.9, 180, 'dr.ghullam.kibriya@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Nazneen Dilnawaz Pt', 'DPT', 'Physiotherapist', '09:00 AM - 01:30 PM', '09:00:00', '13:30:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 5, 4.5, 40, 'dr.nazneen.dilnawaz@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Syed Ali Akbar', 'MBBS, FCPS (General Surgery)', 'General Surgeon', '09:00 AM - 12:00 PM', '09:00:00', '12:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 17, 4.8, 130, 'dr.syed.ali@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Atif Khan', 'MBBS, FCPS (Surgery)', 'General Surgeon', '10:00 AM - 05:00 PM', '10:00:00', '17:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 30, 13, 4.6, 90, 'dr.atif.khan@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Adnan Tahir', 'MBBS, MS (Cardiac Surgery)', 'Cardiac Surgeon', '09:00 AM - 02:00 PM', '09:00:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 11, 4.7, 70, 'dr.adnan.tahir@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Anfal Tahir', 'MBBS', 'General Physician', '09:30 AM - 02:00 PM', '09:30:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 30, 4, 4.4, 30, 'dr.anfal.tahir@healthtrack.com'),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Najam Siddiqui', 'MBBS, FCPS', 'Pediatrician', '10:00 AM - 10:00 PM', '10:00:00', '22:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 30, 19, 4.8, 140, 'dr.najam.siddiqui@healthtrack.com'),
            ('Haripur International Hospital', 'Dr. Ibrahim Mushtaq', 'MBBS, FCPS (Neuro Surgery)', 'Neuro Surgeon', '10:00 AM - 02:00 PM', '10:00:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 12, 4.7, 85, 'dr.ibrahim.mushtaq@healthtrack.com'),
            ('Haripur International Hospital', 'Ms. Sidra Mufti', 'M.Phil (Psychology), Post Magistral Diploma in Clinical Psychology', 'Psychologist', '09:00 AM - 05:00 PM', '09:00:00', '17:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 7, 4.6, 45, 'ms.sidra.mufti@healthtrack.com'),
            ('Mehar General Hospital', 'Dr. Imran Ullah', 'MBBS, MCPS (PSYCHIATRY)', 'Psychiatrist', '10:00 AM - 05:00 PM', '10:00:00', '17:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 30, 15, 4.7, 95, 'dr.imran.ullah@healthtrack.com'),
            ('Mehar General Hospital', 'Dr. Muhammad Ashraf', 'BDS', 'Dentist', '09:00 AM - 08:00 PM', '09:00:00', '20:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 30, 14, 4.8, 110, 'dr.muhammad.ashraf@healthtrack.com'),
            ('Yahya Hospital Haripur', 'Dr. Hina Shaukat', 'MBBS, FCPS (Gastroenterology), MRCP', 'Gastroenterologist', '04:00 PM - 06:30 PM', '16:00:00', '18:30:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 10, 4.7, 80, 'dr.hina.shaukat@healthtrack.com'),
            ('Yahya Hospital Haripur', 'Dr. Zahid Hassan', 'MBBS, FCPS (Neurology), Fellowship In Stroke & vascular Neurology', 'Neurologist', '02:00 PM - 04:00 PM', '14:00:00', '16:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 13, 4.8, 100, 'dr.zahid.hassan@healthtrack.com'),
            ('Yahya Hospital Haripur', 'Dr. Muhammad Umer Suleman', 'MBBS, R.M.P (Pak), G.M.C (U.K), I.M.C (Ireland)', 'General Practitioner', '09:00 AM - 05:00 PM', '09:00:00', '17:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 30, 8, 4.5, 50, 'dr.umer.suleman@healthtrack.com'),
            ('Yahya Hospital Haripur', 'Dr. Muhammad Tahir', 'MBBS', 'General Practitioner', '03:00 PM - 05:30 PM', '15:00:00', '17:30:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 30, 6, 4.4, 35, 'dr.muhammad.tahir@healthtrack.com')
        ]
        
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        default_password = bcrypt.generate_password_hash('doctor123').decode('utf-8')
        
        insert_query = """
            INSERT INTO doctors 
            (hospital, name, qualification, specialization, timings, start_time, end_time, 
             working_days, consultation_duration, experience_years,
             rating, total_reviews, email, password_hash, is_available)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        """
        
        for doctor in doctors_data:
            try:
                cursor.execute(insert_query, doctor + (default_password,))
            except Exception as e:
                print(f"Error inserting doctor {doctor[1]}: {e}")
        
        self.connection.commit()
        cursor.close()
        print(f"✓ Inserted {len(doctors_data)} doctors")
    
    def get_connection(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection


# Run this if executed directly
if __name__ == "__main__":
    print("Setting up HealthTrack AI Database...")
    print("="*50)
    db = Database()
    db.create_tables()
    print("\n✅ Database setup complete!")