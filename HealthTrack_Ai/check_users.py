# check_users.py
import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        database='healthtrack_ai',
        user='root',
        password=''
    )
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, full_name, email, email_verified, is_active FROM users")
    users = cursor.fetchall()
    
    print("\n" + "="*60)
    print("EXISTING USERS")
    print("="*60)
    
    if users:
        for user in users:
            print(f"\nID: {user['id']}")
            print(f"Name: {user['full_name']}")
            print(f"Email: {user['email']}")
            print(f"Email Verified: {user['email_verified']}")
            print(f"Active: {user['is_active']}")
            print("-" * 40)
    else:
        print("No users found")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")