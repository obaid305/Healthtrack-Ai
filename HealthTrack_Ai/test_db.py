# test_db.py
import mysql.connector
from mysql.connector import Error

def test_database_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='healthtrack_ai',
            user='root',
            password=''  # Update this if you have a password
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✓ Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"✓ Connected to database: {record[0]}")
            
            # Check if doctors table has data
            cursor.execute("SELECT COUNT(*) FROM doctors")
            count = cursor.fetchone()[0]
            print(f"✓ Doctors table has {count} records")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"✗ Error while connecting to MySQL: {e}")
        return False

if __name__ == "__main__":
    print("Testing Database Connection...")
    test_database_connection()