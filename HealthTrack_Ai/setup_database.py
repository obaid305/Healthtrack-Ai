# setup_database.py - Complete Database Setup with All Doctors
import mysql.connector
from mysql.connector import Error

def setup_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        cursor = connection.cursor()
        
        # Drop database if exists
        cursor.execute("DROP DATABASE IF EXISTS healthtrack_ai")
        print("✓ Dropped existing database")
        
        # Create database
        cursor.execute("CREATE DATABASE healthtrack_ai")
        print("✓ Created new database")
        
        cursor.execute("USE healthtrack_ai")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                date_of_birth DATE,
                gender VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
        """)
        print("✓ Created users table")
        
        # Create doctors table with proper structure
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
                last_login TIMESTAMP NULL
            )
        """)
        print("✓ Created doctors table")
        
        # Create appointments table
        cursor.execute("""
            CREATE TABLE appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                doctor_id INT NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                status ENUM('scheduled', 'completed', 'cancelled', 'rescheduled') DEFAULT 'scheduled',
                symptoms TEXT,
                predicted_disease VARCHAR(255),
                confidence_score DECIMAL(5,2),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                cancelled_at TIMESTAMP NULL,
                cancellation_reason TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(id),
                UNIQUE KEY unique_appointment (doctor_id, appointment_date, appointment_time)
            )
        """)
        print("✓ Created appointments table")
        
        # Create patient_history table
        cursor.execute("""
            CREATE TABLE patient_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                appointment_id INT,
                symptoms TEXT,
                predicted_disease VARCHAR(255),
                confidence_score DECIMAL(5,2),
                doctor_specialization VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (appointment_id) REFERENCES appointments(id)
            )
        """)
        print("✓ Created patient_history table")
        
        # Insert all doctors from Excel data
        doctors_data = [
            # ALLAMA IQBAL HOSPITAL HARIPUR
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Shahzad Gul', 'MBBS, FCPS (Medicine), FCPS (Rheumatology), MRCP (Rheumatology), SCE Rheumatology(UK), Post graduate Dip in Diabetes (AKU, Karachi)', 'Rheumatologist', '11:00 AM - 02:00 PM', '11:00:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 15, 4.8, 120),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Niaz Akbar Afridi', 'MBBS, Diploma (Dermatology)', 'Dermatologist', '02:30 PM - 05:30 PM', '14:30:00', '17:30:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 12, 4.6, 85),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Syed Danish Mehmood', 'MBBS, FCPS (Orthopaedic Surgery)', 'Orthopedic Surgeon', '03:00 PM - 05:00 PM', '15:00:00', '17:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 10, 4.7, 95),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Arif Hussain', 'MBBS, FCPS (Paediatrics)', 'Pediatrician', '08:30 AM - 01:00 PM', '08:30:00', '13:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 18, 4.9, 150),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Malik Ehsan', 'MBBS, MD (Neurology)', 'Neurologist', '04:00 PM - 06:00 PM', '16:00:00', '18:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 14, 4.7, 80),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Abdul Qadeer Khan', 'MBBS, MS (Orthopaedic Surgery)', 'Orthopedic Surgeon', '10:00 AM - 02:00 PM', '10:00:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 16, 4.8, 110),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Muhammad Akram Khan', 'MBBS', 'Internal Medicine Specialist', '04:00 PM - 08:00 PM', '16:00:00', '20:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 20, 4.5, 200),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Mubbashir Ali Baig', 'MBBS, MS Neurosurgery', 'Neuro Surgeon', '04:00 PM - 08:00 PM', '16:00:00', '20:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 9, 4.6, 60),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Ayesha Imtiaz', 'MBBS, FCPS (Obstetrics & Gynaecology)', 'Gynecologist', '04:00 PM - 07:00 PM', '16:00:00', '19:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 8, 4.7, 75),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Ghullam Kibriya', 'MBBS, MCPS Family Medicine, Diploma in Cardiology', 'Cardiologist', '08:30 AM - 02:00 PM', '08:30:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 22, 4.9, 180),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Nazneen Dilnawaz Pt', 'DPT', 'Physiotherapist', '09:00 AM - 01:30 PM', '09:00:00', '13:30:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 5, 4.5, 40),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Syed Ali Akbar', 'MBBS, FCPS (General Surgery)', 'General Surgeon', '09:00 AM - 12:00 PM', '09:00:00', '12:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 17, 4.8, 130),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Atif Khan', 'MBBS, FCPS (Surgery)', 'General Surgeon', '10:00 AM - 05:00 PM', '10:00:00', '17:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 13, 4.6, 90),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Adnan Tahir', 'MBBS, MS (Cardiac Surgery)', 'Cardiac Surgeon', '09:00 AM - 02:00 PM', '09:00:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 11, 4.7, 70),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Anfal Tahir', 'MBBS', 'General Physician', '09:30 AM - 02:00 PM', '09:30:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 4, 4.4, 30),
            ('ALLAMA IQBAL HOSPITAL HARIPUR', 'Dr. Najam Siddiqui', 'MBBS, FCPS', 'Pediatrician', '10:00 AM - 10:00 PM', '10:00:00', '22:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 19, 4.8, 140),
            
            # Haripur International Hospital
            ('Haripur International Hospital', 'Dr. Ibrahim Mushtaq', 'MBBS, FCPS (Neuro Surgery)', 'Neuro Surgeon', '10:00 AM - 02:00 PM', '10:00:00', '14:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 12, 4.7, 85),
            ('Haripur International Hospital', 'Ms. Sidra Mufti', 'M.Phil (Psychology), Post Magistral Diploma in Clinical Psychology, M.Sc. (Psychology)', 'Psychologist', 'By Appointment', '09:00:00', '17:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 7, 4.6, 45),
            
            # Mehar General Hospital
            ('Mehar General Hospital', 'Dr. Imran Ullah', 'MBBS, MCPS (PSYCHIATRY)', 'Psychiatrist', '10:00 AM - 05:00 PM', '10:00:00', '17:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 15, 4.7, 95),
            ('Mehar General Hospital', 'Dr. Muhammad Ashraf', 'BDS', 'Dentist', '09:00 AM - 08:00 PM', '09:00:00', '20:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 14, 4.8, 110),
            
            # Yahya Hospital
            ('Yahya Hospital Haripur', 'Dr. Hina Shaukat', 'MBBS, FCPS (Gastroenterology), MRCP', 'Gastroenterologist', '04:00 PM - 06:30 PM', '16:00:00', '18:30:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 10, 4.7, 80),
            ('Yahya Hospital Haripur', 'Dr. Zahid Hassan', 'MBBS, FCPS (Neurology), Fellowship In Stroke & vascular Neurology', 'Neurologist', '02:00 PM - 04:00 PM', '14:00:00', '16:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 13, 4.8, 100),
            ('Yahya Hospital Haripur', 'Dr. Muhammad Umer Suleman', 'MBBS, R.M.P (Pak), G.M.C (U.K), I.M.C (Ireland)', 'General Practitioner', '09:00 AM - 05:00 PM', '09:00:00', '17:00:00', '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]', 8, 4.5, 50),
            ('Yahya Hospital Haripur', 'Dr. Muhammad Tahir', 'MBBS', 'General Practitioner', '03:00 PM - 05:30 PM', '15:00:00', '17:30:00', '["Monday","Tuesday","Wednesday","Thursday","Friday"]', 6, 4.4, 35)
        ]
        
        insert_query = """
            INSERT INTO doctors 
            (hospital, name, qualification, specialization, timings, start_time, end_time, working_days, 
             experience_years, rating, total_reviews) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(insert_query, doctors_data)
        connection.commit()
        
        print(f"✓ Inserted {cursor.rowcount} doctors")
        
        # Set default passwords for doctors
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        
        cursor.execute("SELECT id, name, email FROM doctors WHERE email IS NULL")
        doctors_to_update = cursor.fetchall()
        
        for doctor in doctors_to_update:
            doctor_id = doctor[0]
            doctor_name = doctor[1]
            email = doctor_name.lower().replace(' ', '.').replace('dr.', '').strip() + '@healthtrack.com'
            password_hash = bcrypt.generate_password_hash('doctor123').decode('utf-8')
            cursor.execute("UPDATE doctors SET email = %s, password_hash = %s WHERE id = %s", 
                          (email, password_hash, doctor_id))
            print(f"  ✓ Set credentials for {doctor_name}: {email} / doctor123")
        
        connection.commit()
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM doctors")
        count = cursor.fetchone()[0]
        print(f"✓ Total doctors in database: {count}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ Database setup completed successfully!")
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Setting up HealthTrack AI Database...")
    print("=" * 50)
    setup_database()