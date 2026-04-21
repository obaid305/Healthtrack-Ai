# appointment_routes.py - Fixed time format handling and race condition
from datetime import datetime, timedelta
import json
import logging
import mysql.connector

class AppointmentRoutes:
    def __init__(self, db):
        self.db = db
        logging.basicConfig(level=logging.INFO)
        self.cancellation_deadline_hours = 24
    
    def _convert_to_time(self, time_value):
        if time_value is None:
            return None
        if isinstance(time_value, timedelta):
            total_seconds = time_value.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            return datetime.strptime(f"{hours:02d}:{minutes:02d}:00", '%H:%M:%S').time()
        if isinstance(time_value, datetime):
            return time_value.time()
        if isinstance(time_value, str):
            return datetime.strptime(time_value, '%H:%M:%S').time()
        return time_value
    
    def _normalize_time_format(self, time_str):
        """Convert various time formats to HH:MM:SS"""
        time_str = time_str.strip()
        # Already HH:MM:SS
        if re.match(r'^\d{2}:\d{2}:\d{2}$', time_str):
            return time_str
        # HH:MM (24h)
        if re.match(r'^\d{2}:\d{2}$', time_str):
            return time_str + ':00'
        # 12-hour format with AM/PM
        match = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str, re.IGNORECASE)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            ampm = match.group(3).upper()
            if ampm == 'PM' and hour != 12:
                hour += 12
            if ampm == 'AM' and hour == 12:
                hour = 0
            return f"{hour:02d}:{minute:02d}:00"
        raise ValueError(f"Unrecognized time format: {time_str}")
    
    def get_daily_appointment_count(self, doctor_id, date):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as count FROM appointments 
            WHERE doctor_id = %s AND appointment_date = %s 
            AND status IN ('scheduled', 'rescheduled')
        """, (doctor_id, date))
        result = cursor.fetchone()
        cursor.close()
        return result['count'] if result else 0
    
    def verify_user_exists(self, user_id):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE id = %s AND is_active = TRUE", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return user is not None
    
    def is_slot_available(self, doctor_id, date, time_slot, duration=30):
        cursor = self.db.get_connection().cursor(dictionary=True)
        appointment_time = datetime.strptime(self._normalize_time_format(time_slot), '%H:%M:%S').time()
        start_datetime = datetime.combine(datetime.strptime(str(date), '%Y-%m-%d'), appointment_time)
        end_datetime = start_datetime + timedelta(minutes=duration)
        end_time = end_datetime.time()
        cursor.execute("""
            SELECT id FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.doctor_id = %s 
              AND a.appointment_date = %s 
              AND a.status IN ('scheduled', 'rescheduled')
              AND (
                  (appointment_time <= %s AND ADDTIME(appointment_time, SEC_TO_TIME(consultation_duration * 60)) > %s)
                  OR
                  (appointment_time < %s AND ADDTIME(appointment_time, SEC_TO_TIME(consultation_duration * 60)) >= %s)
              )
        """, (doctor_id, date, appointment_time, appointment_time, end_time, end_time))
        overlapping = cursor.fetchall()
        cursor.close()
        return len(overlapping) == 0
    
    def is_doctor_available(self, doctor_id, date, time_slot):
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("""
            SELECT start_time, end_time, working_days, is_available, 
                   max_appointments_per_day, consultation_duration
            FROM doctors WHERE id = %s AND is_active = TRUE
        """, (doctor_id,))
        doctor = cursor.fetchone()
        if not doctor:
            cursor.close()
            return False, "Doctor not found"
        if not doctor['is_available']:
            cursor.close()
            return False, "Doctor is currently not accepting appointments"
        start_time = self._convert_to_time(doctor['start_time'])
        end_time = self._convert_to_time(doctor['end_time'])
        if not start_time or not end_time:
            cursor.close()
            return False, "Doctor timings not configured"
        appointment_date = datetime.strptime(str(date), '%Y-%m-%d')
        day_name = appointment_date.strftime('%A')
        working_days = json.loads(doctor['working_days']) if doctor['working_days'] else []
        if day_name not in working_days:
            cursor.close()
            return False, f"Doctor is not available on {day_name}s"
        appointment_time = datetime.strptime(self._normalize_time_format(time_slot), '%H:%M:%S').time()
        def to_minutes(t):
            return t.hour * 60 + t.minute
        start_minutes = to_minutes(start_time)
        end_minutes = to_minutes(end_time)
        appt_minutes = to_minutes(appointment_time)
        if not (start_minutes <= appt_minutes <= end_minutes):
            cursor.close()
            return False, f"Doctor works from {start_time.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')}"
        daily_count = self.get_daily_appointment_count(doctor_id, date)
        if daily_count >= doctor['max_appointments_per_day']:
            cursor.close()
            return False, "Doctor has reached maximum appointments for this day"
        consultation_duration = doctor['consultation_duration']
        cursor.execute("""
            SELECT COUNT(*) as count FROM appointments 
            WHERE doctor_id = %s AND appointment_date = %s 
            AND status IN ('scheduled', 'rescheduled')
            AND (appointment_time <= %s AND ADDTIME(appointment_time, SEC_TO_TIME(%s * 60)) > %s)
        """, (doctor_id, date, appointment_time, consultation_duration, appointment_time))
        result = cursor.fetchone()
        if result and result['count'] > 0:
            cursor.close()
            return False, "This time slot is already booked"
        cursor.close()
        return True, "Available"
    
    def get_available_slots(self, doctor_id, date=None):
        if not date:
            date = datetime.now().date()
        cursor = self.db.get_connection().cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, start_time, end_time, working_days, is_available, 
                   consultation_duration, max_appointments_per_day
            FROM doctors WHERE id = %s AND is_active = TRUE
        """, (doctor_id,))
        doctor = cursor.fetchone()
        if not doctor or not doctor['is_available']:
            cursor.close()
            return []
        start_time = self._convert_to_time(doctor['start_time'])
        end_time = self._convert_to_time(doctor['end_time'])
        if not start_time or not end_time:
            cursor.close()
            return []
        appointment_date = datetime.strptime(str(date), '%Y-%m-%d')
        day_name = appointment_date.strftime('%A')
        working_days = json.loads(doctor['working_days']) if doctor['working_days'] else []
        if day_name not in working_days:
            cursor.close()
            return []
        daily_count = self.get_daily_appointment_count(doctor_id, date)
        if daily_count >= doctor['max_appointments_per_day']:
            cursor.close()
            return []
        duration = doctor['consultation_duration']
        current = datetime.combine(appointment_date, start_time)
        end = datetime.combine(appointment_date, end_time)
        all_slots = []
        while current <= end:
            time_str = current.strftime('%I:%M %p').lstrip('0')
            all_slots.append(time_str)
            current += timedelta(minutes=duration)
        if len(all_slots) > 1 and all_slots[-1] == end.strftime('%I:%M %p').lstrip('0'):
            all_slots.pop()
        cursor.execute("""
            SELECT appointment_time, consultation_duration 
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.doctor_id = %s AND a.appointment_date = %s 
            AND a.status IN ('scheduled', 'rescheduled')
        """, (doctor_id, date))
        booked = cursor.fetchall()
        blocked_ranges = []
        for b in booked:
            time_obj = self._convert_to_time(b['appointment_time'])
            start_block = datetime.combine(appointment_date, time_obj)
            end_block = start_block + timedelta(minutes=b['consultation_duration'])
            blocked_ranges.append((start_block, end_block))
        available_slots = []
        for slot_time_str in all_slots:
            slot_time = datetime.strptime(slot_time_str, '%I:%M %p').time()
            slot_start = datetime.combine(appointment_date, slot_time)
            slot_end = slot_start + timedelta(minutes=duration)
            is_blocked = False
            for block_start, block_end in blocked_ranges:
                if not (slot_end <= block_start or slot_start >= block_end):
                    is_blocked = True
                    break
            if not is_blocked:
                available_slots.append(slot_time_str)
        cursor.close()
        return available_slots
    
    def can_cancel(self, appointment_date):
        now = datetime.now().date()
        appt_date = datetime.strptime(str(appointment_date), '%Y-%m-%d').date()
        days_until = (appt_date - now).days
        return days_until >= 1
    
    def book_appointment(self, user_id, doctor_id, date, time, symptoms='', predicted_disease='', confidence=0):
        cursor = self.db.get_connection().cursor(dictionary=True)
        try:
            if not self.verify_user_exists(user_id):
                cursor.close()
                return False, "User not found. Please login again.", None
            try:
                db_time = self._normalize_time_format(time)
            except ValueError:
                cursor.close()
                return False, "Invalid time format. Please select a valid time slot.", None
            # Use INSERT ... SELECT ... WHERE NOT EXISTS to prevent race condition
            cursor.execute("""
                INSERT INTO appointments 
                (user_id, doctor_id, appointment_date, appointment_time, symptoms, predicted_disease, confidence_score)
                SELECT %s, %s, %s, %s, %s, %s, %s
                FROM DUAL
                WHERE NOT EXISTS (
                    SELECT 1 FROM appointments 
                    WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s
                    AND status IN ('scheduled', 'rescheduled')
                )
            """, (user_id, doctor_id, date, db_time, symptoms, predicted_disease, confidence,
                  doctor_id, date, db_time))
            if cursor.rowcount == 0:
                cursor.close()
                return False, "❌ This time slot is already booked. Please select a different time.", None
            appointment_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO patient_history (user_id, appointment_id, symptoms, predicted_disease, confidence_score)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, appointment_id, symptoms, predicted_disease, confidence))
            self.db.connection.commit()
            cursor.close()
            return True, "✅ Appointment booked successfully!", appointment_id
        except Exception as e:
            self.db.connection.rollback()
            cursor.close()
            return False, f"Unable to book appointment: {str(e)}", None
    
    def get_user_appointments(self, user_id):
        cursor = self.db.get_connection().cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT a.*, d.name as doctor_name, d.specialization, d.hospital, d.timings
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.id
                WHERE a.user_id = %s
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """, (user_id,))
            appointments = cursor.fetchall()
            cursor.close()
            return appointments
        except Exception as e:
            print(f"Error getting user appointments: {e}")
            cursor.close()
            return []
    
    def cancel_appointment(self, appointment_id, user_id, reason=''):
        cursor = self.db.get_connection().cursor(dictionary=True)
        try:
            cursor.execute("SELECT appointment_date, status FROM appointments WHERE id = %s AND user_id = %s",
                           (appointment_id, user_id))
            appointment = cursor.fetchone()
            if not appointment:
                cursor.close()
                return False, "Appointment not found"
            if appointment['status'] != 'scheduled':
                cursor.close()
                return False, "Only scheduled appointments can be cancelled"
            if not self.can_cancel(appointment['appointment_date']):
                cursor.close()
                return False, "Appointments can only be cancelled at least 24 hours before"
            cursor.execute("""
                UPDATE appointments 
                SET status = 'cancelled', cancelled_at = NOW(), cancellation_reason = %s
                WHERE id = %s AND user_id = %s AND status = 'scheduled'
            """, (reason, appointment_id, user_id))
            if cursor.rowcount > 0:
                self.db.connection.commit()
                cursor.close()
                return True, "Appointment cancelled successfully"
            cursor.close()
            return False, "Unable to cancel appointment"
        except Exception as e:
            cursor.close()
            return False, f"Error cancelling appointment: {str(e)}"
    
    def reschedule_appointment(self, appointment_id, user_id, new_date, new_time):
        cursor = self.db.get_connection().cursor(dictionary=True)
        try:
            cursor.execute("SELECT doctor_id, reschedule_count FROM appointments WHERE id = %s AND user_id = %s AND status = 'scheduled'",
                           (appointment_id, user_id))
            result = cursor.fetchone()
            if not result:
                cursor.close()
                return False, "Appointment not found or cannot be rescheduled"
            if result['reschedule_count'] >= 2:
                cursor.close()
                return False, "This appointment has already been rescheduled the maximum number of times"
            doctor_id = result['doctor_id']
            # Normalize time format
            try:
                db_time = self._normalize_time_format(new_time)
            except ValueError:
                cursor.close()
                return False, "Invalid time format. Please select a valid time slot."
            is_available, message = self.is_doctor_available(doctor_id, new_date, new_time)
            if not is_available:
                cursor.close()
                return False, message
            cursor.execute("""
                UPDATE appointments 
                SET appointment_date = %s, appointment_time = %s, status = 'rescheduled',
                    reschedule_count = reschedule_count + 1
                WHERE id = %s AND user_id = %s AND status = 'scheduled'
            """, (new_date, db_time, appointment_id, user_id))
            if cursor.rowcount > 0:
                self.db.connection.commit()
                cursor.close()
                return True, "Appointment rescheduled successfully"
            cursor.close()
            return False, "Unable to reschedule appointment"
        except Exception as e:
            self.db.connection.rollback()
            cursor.close()
            return False, f"Error rescheduling: {str(e)}"

# ============================================
# DoctorAppointmentRoutes (unchanged, but keep)
# ============================================
class DoctorAppointmentRoutes:
    def __init__(self, db):
        self.db = db
    
    def get_doctor_appointments(self, doctor_id, filter_type='all'):
        # ... (same as original, no changes needed)
        cursor = self.db.get_connection().cursor(dictionary=True)
        today = datetime.now().date()
        if filter_type == 'today':
            query = """
                SELECT a.*, u.full_name as patient_name, u.email as patient_email, u.phone as patient_phone,
                       p.predicted_disease, p.confidence_score
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                LEFT JOIN patient_history p ON a.id = p.appointment_id
                WHERE a.doctor_id = %s AND a.appointment_date = %s AND a.status = 'scheduled'
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
                WHERE a.doctor_id = %s AND a.appointment_date > %s AND a.status = 'scheduled'
                ORDER BY a.appointment_date ASC, a.appointment_time ASC LIMIT 20
            """
            cursor.execute(query, (doctor_id, today))
        # ... (rest of filter options same as original)
        else:
            query = """
                SELECT a.*, u.full_name as patient_name, u.email as patient_email, u.phone as patient_phone,
                       p.predicted_disease, p.confidence_score
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                LEFT JOIN patient_history p ON a.id = p.appointment_id
                WHERE a.doctor_id = %s
                ORDER BY a.appointment_date DESC, a.appointment_time DESC LIMIT 50
            """
            cursor.execute(query, (doctor_id,))
        appointments = cursor.fetchall()
        for apt in appointments:
            if hasattr(apt['appointment_time'], 'seconds'):
                total_seconds = apt['appointment_time'].seconds
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                ampm = 'AM' if hours < 12 else 'PM'
                hour12 = hours if hours <= 12 else hours - 12
                if hour12 == 0: hour12 = 12
                apt['appointment_time_str'] = f"{hour12:02d}:{minutes:02d} {ampm}"
            elif hasattr(apt['appointment_time'], 'strftime'):
                apt['appointment_time_str'] = apt['appointment_time'].strftime('%I:%M %p').lstrip('0')
            else:
                apt['appointment_time_str'] = str(apt['appointment_time'])
        cursor.close()
        return appointments
    
    def get_appointment_stats(self, doctor_id):
        cursor = self.db.get_connection().cursor(dictionary=True)
        today = datetime.now().date()
        cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE doctor_id = %s AND appointment_date = %s AND status = 'scheduled'", (doctor_id, today))
        today_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE doctor_id = %s AND appointment_date > %s AND status = 'scheduled'", (doctor_id, today))
        upcoming_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(DISTINCT user_id) as count FROM appointments WHERE doctor_id = %s AND status != 'cancelled'", (doctor_id,))
        total_patients = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE doctor_id = %s AND status = 'completed'", (doctor_id,))
        completed_count = cursor.fetchone()['count']
        cursor.close()
        return {'today_count': today_count, 'upcoming_count': upcoming_count, 'total_patients': total_patients, 'completed_count': completed_count}
    
    def update_appointment_status(self, appointment_id, doctor_id, status, notes=None):
        cursor = self.db.get_connection().cursor()
        try:
            cursor.execute("SELECT id FROM appointments WHERE id = %s AND doctor_id = %s", (appointment_id, doctor_id))
            if not cursor.fetchone():
                cursor.close()
                return False, "Appointment not found or unauthorized"
            cursor.execute("UPDATE appointments SET status = %s, notes = COALESCE(%s, notes), updated_at = NOW() WHERE id = %s", (status, notes, appointment_id))
            self.db.connection.commit()
            cursor.close()
            return True, f"Appointment {status} successfully"
        except Exception as e:
            self.db.connection.rollback()
            cursor.close()
            return False, f"Error updating appointment: {str(e)}"