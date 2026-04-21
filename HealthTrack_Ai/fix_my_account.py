# fix_my_account.py
import mysql.connector
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Your credentials
email = "obaidy586@gmail.com"
new_password = "Test@123"

print("\n" + "="*60)
print("FIXING YOUR ACCOUNT")
print("="*60)

connection = mysql.connector.connect(
    host='localhost',
    database='healthtrack_ai',
    user='root',
    password=''
)

cursor = connection.cursor(dictionary=True)

# Check if user exists
cursor.execute("SELECT id, full_name, email, email_verified, password_hash FROM users WHERE email = %s", (email,))
user = cursor.fetchone()

if user:
    print(f"\n✅ User found:")
    print(f"   Name: {user['full_name']}")
    print(f"   Email: {user['email']}")
    print(f"   Email Verified: {'Yes' if user['email_verified'] else 'No'}")
    
    # Hash the new password
    password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    
    # Update user
    cursor.execute("""
        UPDATE users 
        SET password_hash = %s, 
            email_verified = TRUE,
            verification_token = NULL,
            reset_token = NULL,
            reset_token_expiry = NULL,
            is_active = TRUE
        WHERE email = %s
    """, (password_hash, email))
    
    connection.commit()
    
    # Verify the update
    cursor.execute("SELECT email_verified, password_hash FROM users WHERE email = %s", (email,))
    updated = cursor.fetchone()
    
    print(f"\n✅ Account Updated:")
    print(f"   Email Verified: {'Yes' if updated['email_verified'] else 'No'}")
    
    # Test the password
    is_valid = bcrypt.check_password_hash(updated['password_hash'], new_password)
    print(f"   Password Valid: {is_valid}")
    
    if is_valid and updated['email_verified']:
        print(f"\n{'='*60}")
        print(f"✅ LOGIN SHOULD WORK NOW!")
        print(f"{'='*60}")
        print(f"Email: {email}")
        print(f"Password: {new_password}")
        print(f"{'='*60}")
    else:
        print(f"\n❌ Still having issues. Please run debug script.")
        
else:
    print(f"\n❌ User not found. Please register first.")
    print(f"   Go to: http://localhost:5000/register")

cursor.close()
connection.close()
