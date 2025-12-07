from datetime import datetime
from models.database import db
import uuid

class Attendance:
    """Attendance model for session and record management"""
    
    sessions_collection = 'sessions'
    attendance_collection = 'attendance'
    
    @staticmethod
    def create_session(date, subject, department, year, division, teacher_id=None):
        """Create a new attendance session"""
        session = {
            'sessionId': str(uuid.uuid4()),
            'date': date,
            'subject': subject,
            'department': department,
            'year': year,
            'division': division,
            'teacherId': teacher_id,
            'createdAt': datetime.now().isoformat(),
            'status': 'active',
            'totalPresent': 0
        }
        
        result = db.insert_one(Attendance.sessions_collection, session)
        return result, None
    
    @staticmethod
    def get_session(session_id):
        """Get session by ID"""
        return db.find_one(Attendance.sessions_collection, {'sessionId': session_id})
    
    @staticmethod
    def get_all_sessions():
        """Get all sessions"""
        return db.find(Attendance.sessions_collection)
    
    @staticmethod
    def get_sessions_by_filters(department=None, year=None, division=None, date=None):
        """Get sessions by filters"""
        query = {}
        if department:
            query['department'] = department
        if year:
            query['year'] = year
        if division:
            query['division'] = division
        if date:
            query['date'] = date
        
        return db.find(Attendance.sessions_collection, query)
    
    @staticmethod
    def mark_attendance(session_id, student_id, confidence):
        """Mark attendance for a student in a session"""
        # Check if already marked
        existing = db.find_one(
            Attendance.attendance_collection,
            {'sessionId': session_id, 'studentId': student_id}
        )
        
        if existing:
            return existing, "Already marked"
        
        attendance_record = {
            'sessionId': session_id,
            'studentId': student_id,
            'timestamp': datetime.now().isoformat(),
            'confidence': confidence,
            'status': 'present'
        }
        
        result = db.insert_one(Attendance.attendance_collection, attendance_record)
        
        # Update session total present count
        session = Attendance.get_session(session_id)
        if session:
            db.update_one(
                Attendance.sessions_collection,
                {'sessionId': session_id},
                {'totalPresent': session.get('totalPresent', 0) + 1}
            )
        
        return result, None
    
    @staticmethod
    def get_session_attendance(session_id):
        """Get all attendance records for a session"""
        return db.find(Attendance.attendance_collection, {'sessionId': session_id})
    
    @staticmethod
    def get_student_attendance(student_id):
        """Get all attendance records for a student"""
        return db.find(Attendance.attendance_collection, {'studentId': student_id})
    
    @staticmethod
    def get_student_attendance_by_filters(student_id, department=None, year=None, division=None):
        """Get student attendance with session filters"""
        # Get all attendance records for student
        attendance_records = Attendance.get_student_attendance(student_id)
        
        if not (department or year or division):
            return attendance_records
        
        # Filter by session details
        filtered_records = []
        for record in attendance_records:
            session = Attendance.get_session(record['sessionId'])
            if session:
                match = True
                if department and session.get('department') != department:
                    match = False
                if year and session.get('year') != year:
                    match = False
                if division and session.get('division') != division:
                    match = False
                
                if match:
                    record['session'] = session
                    filtered_records.append(record)
        
        return filtered_records
    
    @staticmethod
    def delete_session(session_id):
        """Delete a session and its attendance records"""
        # Delete all attendance records for this session
        db.delete_many(Attendance.attendance_collection, {'sessionId': session_id})
        
        # Delete the session
        return db.delete_one(Attendance.sessions_collection, {'sessionId': session_id})
    
    @staticmethod
    def get_attendance_stats(department=None, year=None, division=None):
        """Get attendance statistics"""
        sessions = Attendance.get_sessions_by_filters(department, year, division)
        
        total_sessions = len(sessions)
        total_attendance = db.count_documents(Attendance.attendance_collection)
        
        return {
            'totalSessions': total_sessions,
            'totalAttendance': total_attendance,
            'sessions': sessions
        }
