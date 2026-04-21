from datetime import datetime, timedelta

class DoctorAppointmentRoutes:
    def __init__(self, db):
        self.db = db
    
    def get_doctor_appointments(self, doctor_id, filter_type='all'):
        """Get appointments for a specific doctor"""
        cursor = self.db.get_connection().cursor(dictionary=True)
        
        today = datetime.now().date()
        now = datetime.now().time()
        
        if filter_type == 'today':
            query = """
                SELECT a.*, u.full_name as patient_name, u.email as patient_email, u.phone as patient_phone,
                       p.predicted_disease, p.confidence_score
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                LEFT JOIN patient_history p ON a.id = p.appointment_id
                WHERE a.doctor_id = %s AND a.appointment_date = %s AND a.status != 'cancelled'
                ORDER BY a.appointment_time ASC
            """
            cursor.execute(query, (doctor_id, today))
            
        elif filter_type == 'upcoming':
            query = """
                SELECT a.*, u.full_name as patient_name, u.email as patient_email, u.phone as patient_phone,
                       p.predicted_disease, p.confidence_score
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                LEFT JOIN patient_history p ON a.id = p.appointment_id
                WHERE a.doctor_id = %s AND a.appointment_date > %s AND a.status != 'cancelled'
                ORDER BY a.appointment_date ASC, a.appointment_time ASC
                LIMIT 20
            """
            cursor.execute(query, (doctor_id, today))
            
        elif filter_type == 'past':
            query = """
                SELECT a.*, u.full_name as patient_name, u.email as patient_email, u.phone as patient_phone,
                       p.predicted_disease, p.confidence_score
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                LEFT JOIN patient_history p ON a.id = p.appointment_id
                WHERE a.doctor_id = %s AND a.appointment_date < %s AND a.status != 'cancelled'
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
                LIMIT 20
            """
            cursor.execute(query, (doctor_id, today))
            
        elif filter_type == 'cancelled':
            query = """
                SELECT a.*, u.full_name as patient_name, u.email as patient_email, u.phone as patient_phone
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                WHERE a.doctor_id = %s AND a.status = 'cancelled'
                ORDER BY a.created_at DESC
                LIMIT 20
            """
            cursor.execute(query, (doctor_id,))
            
        else:  # all appointments
            query = """
                SELECT a.*, u.full_name as patient_name, u.email as patient_email, u.phone as patient_phone,
                       p.predicted_disease, p.confidence_score
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                LEFT JOIN patient_history p ON a.id = p.appointment_id
                WHERE a.doctor_id = %s
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
                LIMIT 50
            """
            cursor.execute(query, (doctor_id,))
        
        appointments = cursor.fetchall()
        
        # Format time for display
        for apt in appointments:
            if hasattr(apt['appointment_time'], 'seconds'):
                total_seconds = apt['appointment_time'].seconds
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                ampm = 'AM' if hours < 12 else 'PM'
                hour12 = hours if hours <= 12 else hours - 12
                if hour12 == 0:
                    hour12 = 12
                apt['appointment_time_str'] = f"{hour12:02d}:{minutes:02d} {ampm}"
            elif hasattr(apt['appointment_time'], 'strftime'):
                apt['appointment_time_str'] = apt['appointment_time'].strftime('%I:%M %p')
            else:
                apt['appointment_time_str'] = str(apt['appointment_time'])
        
        cursor.close()
        return appointments
    
    def get_appointment_stats(self, doctor_id):
        """Get appointment statistics for dashboard"""
        cursor = self.db.get_connection().cursor(dictionary=True)
        
        today = datetime.now().date()
        
        # Today's appointments count
        cursor.execute("""
            SELECT COUNT(*) as count FROM appointments 
            WHERE doctor_id = %s AND appointment_date = %s AND status != 'cancelled'
        """, (doctor_id, today))
        today_count = cursor.fetchone()['count']
        
        # Upcoming appointments count
        cursor.execute("""
            SELECT COUNT(*) as count FROM appointments 
            WHERE doctor_id = %s AND appointment_date > %s AND status != 'cancelled'
        """, (doctor_id, today))
        upcoming_count = cursor.fetchone()['count']
        
        # Total patients (unique)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count FROM appointments 
            WHERE doctor_id = %s AND status != 'cancelled'
        """, (doctor_id,))
        total_patients = cursor.fetchone()['count']
        
        # Completed appointments
        cursor.execute("""
            SELECT COUNT(*) as count FROM appointments 
            WHERE doctor_id = %s AND status = 'completed'
        """, (doctor_id,))
        completed_count = cursor.fetchone()['count']
        
        cursor.close()
        
        return {
            'today_count': today_count,
            'upcoming_count': upcoming_count,
            'total_patients': total_patients,
            'completed_count': completed_count
        }
    
    def update_appointment_status(self, appointment_id, doctor_id, status, notes=None):
        """Update appointment status"""
        cursor = self.db.get_connection().cursor()
        
        try:
            # Verify appointment belongs to doctor
            cursor.execute("""
                SELECT id FROM appointments 
                WHERE id = %s AND doctor_id = %s
            """, (appointment_id, doctor_id))
            
            if not cursor.fetchone():
                cursor.close()
                return False, "Appointment not found or unauthorized"
            
            # Update status
            cursor.execute("""
                UPDATE appointments 
                SET status = %s, notes = COALESCE(%s, notes), updated_at = NOW()
                WHERE id = %s
            """, (status, notes, appointment_id))
            
            self.db.connection.commit()
            cursor.close()
            return True, f"Appointment {status} successfully"
            
        except Exception as e:
            self.db.connection.rollback()
            cursor.close()
            return False, f"Error updating appointment: {str(e)}"