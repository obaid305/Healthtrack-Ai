# test_db_connection.py
import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        database='healthtrack_ai',
        user='root',
        password=''
    )
    
    if connection.is_connected():
        print("✓ MySQL Database connection successful")
        
        cursor = connection.cursor()
        
        # Check doctors table
        cursor.execute("SELECT COUNT(*) FROM doctors")
        count = cursor.fetchone()[0]
        print(f"✓ Found {count} doctors in database")
        
        # Show sample doctors
        cursor.execute("SELECT name, specialization, hospital FROM doctors LIMIT 5")
        print("\nSample Doctors:")
        for row in cursor.fetchall():
            print(f"  - {row[0]} ({row[1]}) at {row[2]}")
        
        cursor.close()
        connection.close()
        
except Error as e:
    print(f"✗ Error: {e}")