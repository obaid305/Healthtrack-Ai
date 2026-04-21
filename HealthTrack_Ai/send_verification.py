# send_verification.py
import mysql.connector
import secrets
from datetime import datetime, timedelta

email = "obaidy586@gmail.com"

connection = mysql.connector.connect(
    host='localhost',
    database='healthtrack_ai',
    user='root',
    password=''
)

cursor = connection.cursor()

# Generate verification token
verification_token = secrets.token_urlsafe(32)

# Update user with verification token
cursor.execute("""
    UPDATE users 
    SET verification_token = %s 
    WHERE email = %s
""", (verification_token, email))

if cursor.rowcount > 0:
    connection.commit()
    verification_link = f"http://127.0.0.1:5000/verify-email/{verification_token}"
    
    print("\n" + "="*60)
    print("EMAIL VERIFICATION LINK")
    print("="*60)
    print(f"Click this link to verify your email:")
    print(verification_link)
    print("="*60)
    print("\nAfter clicking the link, you can login!")
else:
    print(f"User with email {email} not found")

cursor.close()
connection.close()