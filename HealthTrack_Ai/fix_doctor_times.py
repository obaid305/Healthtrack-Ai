# fix_doctor_times.py
import mysql.connector
from datetime import time

connection = mysql.connector.connect(
    host='localhost',
    database='healthtrack_ai',
    user='root',
    password=''
)

cursor = connection.cursor()

# Fix any doctors with invalid times
updates = [
    # (doctor_id, start_time, end_time)
    (1, '11:00:00', '14:00:00'),   # Dr. Shahzad Gul
    (2, '14:30:00', '17:30:00'),   # Dr. Niaz Akbar Afridi
    (3, '15:00:00', '17:00:00'),   # Dr. Syed Danish Mehmood
    (4, '08:30:00', '13:00:00'),   # Dr. Arif Hussain
    (5, '16:00:00', '18:00:00'),   # Dr. Malik Ehsan
    (6, '10:00:00', '14:00:00'),   # Dr. Abdul Qadeer Khan
    (7, '16:00:00', '20:00:00'),   # Dr. Muhammad Akram Khan
    (8, '16:00:00', '20:00:00'),   # Dr. Mubbashir Ali Baig
    (9, '16:00:00', '19:00:00'),   # Dr. Ayesha Imtiaz
    (10, '08:30:00', '14:00:00'),  # Dr. Ghullam Kibriya
    (11, '09:00:00', '13:30:00'),  # Dr. Nazneen Dilnawaz Pt
    (12, '09:00:00', '12:00:00'),  # Dr. Syed Ali Akbar
    (13, '10:00:00', '17:00:00'),  # Dr. Atif Khan
    (14, '09:00:00', '14:00:00'),  # Dr. Adnan Tahir
    (15, '09:30:00', '14:00:00'),  # Dr. Anfal Tahir
    (16, '10:00:00', '22:00:00'),  # Dr. Najam Siddiqui
    (17, '10:00:00', '14:00:00'),  # Dr. Ibrahim Mushtaq
    (18, '09:00:00', '17:00:00'),  # Ms. Sidra Mufti
    (19, '10:00:00', '17:00:00'),  # Dr. Imran Ullah
    (20, '09:00:00', '20:00:00'),  # Dr. Muhammad Ashraf
    (21, '16:00:00', '18:30:00'),  # Dr. Hina Shaukat
    (22, '14:00:00', '16:00:00'),  # Dr. Zahid Hassan
    (23, '09:00:00', '17:00:00'),  # Dr. Muhammad Umer Suleman
    (24, '15:00:00', '17:30:00'),  # Dr. Muhammad Tahir
]

for doctor_id, start_time, end_time in updates:
    cursor.execute("""
        UPDATE doctors 
        SET start_time = %s, end_time = %s 
        WHERE id = %s
    """, (start_time, end_time, doctor_id))
    print(f"Updated doctor ID {doctor_id}: {start_time} - {end_time}")

connection.commit()
print(f"\n✅ Updated {cursor.rowcount} doctors")

cursor.close()
connection.close()