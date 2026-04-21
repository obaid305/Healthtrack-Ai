# create_verified_user_direct.py
import mysql.connector
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Connect to database
connection = mysql.connector.connect(
    host='localhost',
    database='healthtrack_ai',
    user='root',
    password=''
)

cursor = connection.cursor()

# Delete existing test user if exists
cursor.execute("DELETE FROM users WHERE email = 'testuser@example.com'")
print("✓ Removed existing test user")

# Create new verified user
full_name = "Test User"
email = "testuser@example.com"
password = "Test@123"
phone = "03001234567"

# Hash password
password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

# Insert user with email_verified = TRUE
cursor.execute("""
    INSERT INTO users (full_name, email, password_hash, phone, email_verified, is_active)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (full_name, email, password_hash, phone, True, True))

connection.commit()
print(f"✓ Created new verified user: {email}")

# Verify insertion
cursor.execute("SELECT id, full_name, email, email_verified FROM users WHERE email = %s", (email,))
user = cursor.fetchone()
print(f"\n✅ User created successfully!")
print(f"   ID: {user[0]}")
print(f"   Name: {user[1]}")
print(f"   Email: {user[2]}")
print(f"   Email Verified: {user[3]}")

print("\n" + "="*50)
print("LOGIN CREDENTIALS")
print("="*50)
print(f"Email: {email}")
print(f"Password: {password}")
print("="*50)

cursor.close()
connection.close()