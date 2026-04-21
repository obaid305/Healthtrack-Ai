# setup_doctor_credentials.py
import mysql.connector
from flask_bcrypt import Bcrypt

def setup_doctor_credentials():
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host='localhost',
            database='healthtrack_ai',
            user='root',
            password=''  # Your MySQL password if any
        )
        
        cursor = connection.cursor(dictionary=True)
        bcrypt = Bcrypt()
        
        # Check if any doctors need email or password
        cursor.execute("""
            SELECT id, name FROM doctors 
            WHERE email IS NULL OR password_hash IS NULL
        """)
        
        doctors = cursor.fetchall()
        
        if doctors:
            print(f"Found {len(doctors)} doctors needing login setup")
            
            for doctor in doctors:
                # Generate email from name if not exists
                if not doctor.get('email'):
                    email = doctor['name'].lower().replace(' ', '.').replace('dr.', '').strip()
                    email = email + '@healthtrack.com'
                    cursor.execute(
                        "UPDATE doctors SET email = %s WHERE id = %s",
                        (email, doctor['id'])
                    )
                    print(f"  ✓ Set email for Dr. {doctor['name']}: {email}")
                
                # Set default password
                if not doctor.get('password_hash'):
                    default_password = 'doctor123'
                    password_hash = bcrypt.generate_password_hash(default_password).decode('utf-8')
                    cursor.execute(
                        "UPDATE doctors SET password_hash = %s WHERE id = %s",
                        (password_hash, doctor['id'])
                    )
                    print(f"  ✓ Set password for Dr. {doctor['name']}: {default_password}")
            
            connection.commit()
            print("\n✅ Doctor credentials setup complete!")
        else:
            print("✓ All doctors already have login credentials")
        
        # Show all doctors with their login info
        cursor.execute("""
            SELECT id, name, email, is_active 
            FROM doctors 
            ORDER BY id
        """)
        
        doctors = cursor.fetchall()
        print("\n" + "="*60)
        print("Doctor Login Credentials:")
        print("="*60)
        for doctor in doctors:
            print(f"ID: {doctor['id']} | Name: {doctor['name']}")
            print(f"    Email: {doctor['email']}")
            print(f"    Password: doctor123")
            print(f"    Status: {'Active' if doctor['is_active'] else 'Inactive'}")
            print("-"*40)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("Setting Up Doctor Login Credentials")
    print("="*60)
    setup_doctor_credentials()