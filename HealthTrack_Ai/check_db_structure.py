# check_db_structure.py
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
        cursor = connection.cursor()
        
        # Show all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check doctors table structure
        cursor.execute("DESCRIBE doctors")
        columns = cursor.fetchall()
        print("\nDoctors table columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM doctors")
        count = cursor.fetchone()[0]
        print(f"\nTotal doctors: {count}")
        
        cursor.close()
        connection.close()
        
except Error as e:
    print(f"Error: {e}")