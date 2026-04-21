# doctor_routes.py - Fixed duplicate method and indentation
import re

class DoctorRoutes:
    def __init__(self, db):
        self.db = db
    
    def get_doctor(self, doctor_id):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
        doctor = cursor.fetchone()
        cursor.close()
        return doctor
    
    def search_doctors(self, search='', specialization='', availability=''):
        cursor = self.db.get_connection().cursor(dictionary=True)
        query = "SELECT * FROM doctors WHERE 1=1"
        params = []
        if search:
            query += " AND (LOWER(name) LIKE LOWER(%s) OR LOWER(hospital) LIKE LOWER(%s))"
            search_pattern = f'%{search}%'
            params.extend([search_pattern, search_pattern])
        if specialization:
            query += " AND LOWER(specialization) LIKE LOWER(%s)"
            params.append(f'%{specialization}%')
        if availability == 'available':
            query += " AND is_available = TRUE"
        query += " ORDER BY rating DESC, name"
        cursor.execute(query, params)
        doctors = cursor.fetchall()
        cursor.close()
        return doctors
    
    def get_doctors_by_specialization(self, specialization):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, hospital, qualification, specialization, timings, rating
            FROM doctors 
            WHERE LOWER(specialization) LIKE LOWER(%s) AND is_available = TRUE
            ORDER BY rating DESC
        """, (f'%{specialization}%',))
        doctors = cursor.fetchall()
        cursor.close()
        return doctors
    
    def get_all_specializations(self):
        cursor = self.db.get_connection().cursor()
        cursor.execute("""
            SELECT DISTINCT specialization FROM doctors 
            WHERE specialization IS NOT NULL AND specialization != ''
            ORDER BY specialization
        """)
        specializations = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return specializations
    
    def get_doctor_stats(self, doctor_id):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as total FROM appointments 
            WHERE doctor_id = %s AND status = 'completed'
        """, (doctor_id,))
        total_appointments = cursor.fetchone()['total']
        cursor.execute("""
            SELECT AVG(rating) as avg_rating, COUNT(*) as review_count 
            FROM reviews WHERE doctor_id = %s
        """, (doctor_id,))
        rating_data = cursor.fetchone()
        cursor.close()
        return {
            'total_appointments': total_appointments,
            'avg_rating': rating_data['avg_rating'] or 0,
            'review_count': rating_data['review_count'] or 0
        }