# update_doctor_days.py
import mysql.connector
import json

connection = mysql.connector.connect(
    host='localhost',
    database='healthtrack_ai',
    user='root',
    password=''
)

cursor = connection.cursor()

# Update working days for all doctors
updates = [
    (1, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (2, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (3, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (4, '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
    (5, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (6, '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
    (7, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (8, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (9, '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
    (10, '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
    (11, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (12, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (13, '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
    (14, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (15, '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
    (16, '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
    (17, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (18, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (19, '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
    (20, '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
    (21, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (22, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
    (23, '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
    (24, '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
]

for doctor_id, working_days in updates:
    cursor.execute(
        "UPDATE doctors SET working_days = %s WHERE id = %s",
        (working_days, doctor_id)
    )
    print(f"Updated doctor ID {doctor_id}")

connection.commit()
print(f"\n✅ Updated {cursor.rowcount} doctors with working days")

cursor.close()
connection.close()
print("✅ Done!")