import mysql.connector

connection = mysql.connector.connect(
    host='localhost',
    database='healthtrack_ai',
    user='root',
    password=''
)

cursor = connection.cursor(dictionary=True)

cursor.execute("""
    SELECT id, name, start_time, end_time, working_days, is_available 
    FROM doctors 
    ORDER BY id
""")

doctors = cursor.fetchall()

print("\n" + "="*80)
print("DOCTORS SCHEDULE")
print("="*80)

for d in doctors:
    print(f"\nID: {d['id']}")
    print(f"Name: {d['name']}")
    print(f"Start Time: {d['start_time']}")
    print(f"End Time: {d['end_time']}")
    print(f"Working Days: {d['working_days']}")
    print(f"Available: {d['is_available']}")
    print("-" * 50)

cursor.close()
connection.close()