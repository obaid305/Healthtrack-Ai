import mysql.connector
import json

connection = mysql.connector.connect(
    host='localhost',
    database='healthtrack_ai',
    user='root',
    password=''
)

cursor = connection.cursor()

# Get all doctors
cursor.execute("SELECT id, name, start_time, end_time FROM doctors")
doctors = cursor.fetchall()

print("Updating working days for all doctors...\n")

for doctor in doctors:
    doctor_id = doctor[0]
    doctor_name = doctor[1]
    start_time = doctor[2]
    end_time = doctor[3]
    
    # Set working days based on doctor's schedule
    # Most doctors work Monday-Friday, some work Saturday too
    if doctor_id in [4, 6, 9, 10, 13, 15, 16, 19, 20, 23]:
        working_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    else:
        working_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    working_days_json = json.dumps(working_days)
    
    cursor.execute(
        "UPDATE doctors SET working_days = %s WHERE id = %s",
        (working_days_json, doctor_id)
    )
    print(f"✓ Updated {doctor_name} (ID: {doctor_id}) - Works on: {', '.join(working_days)}")

connection.commit()
print(f"\n✅ Updated {cursor.rowcount} doctors")

cursor.close()
connection.close()