# verify_email_fix.py
import mysql.connector

# Your email
email = "obaidy586@gmail.com"

connection = mysql.connector.connect(
    host='localhost',
    database='healthtrack_ai',
    user='root',
    password=''
)

cursor = connection.cursor()

# Update email_verified to TRUE
cursor.execute("""
    UPDATE users 
    SET email_verified = TRUE 
    WHERE email = %s
""", (email,))

if cursor.rowcount > 0:
    connection.commit()
    print(f"✅ Email {email} has been verified!")
    print("\nYou can now login with your password.")
else:
    print(f"❌ User with email {email} not found")

# Check the result
cursor.execute("SELECT id, full_name, email, email_verified FROM users WHERE email = %s", (email,))
user = cursor.fetchone()
if user:
    print(f"\nUser Details:")
    print(f"   ID: {user[0]}")
    print(f"   Name: {user[1]}")
    print(f"   Email: {user[2]}")
    print(f"   Email Verified: {'Yes' if user[3] else 'No'}")

cursor.close()
connection.close()