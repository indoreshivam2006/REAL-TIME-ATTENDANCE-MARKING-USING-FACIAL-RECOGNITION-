from flask import Blueprint, request, jsonify
from models.attendance import Attendance
from models.student import Student
from face_recognition.cnn_recognizer import CNNFaceRecognizer
from face_recognition.mtcnn_detector import get_face_detector
from openpyxl import Workbook
from datetime import datetime
import os
from config import Config

attendance_bp = Blueprint('attendance', __name__)

# Initialize face detector and recognizer (CNN-based)
detector = get_face_detector()
recognizer = CNNFaceRecognizer()

@attendance_bp.route('/api/attendance/create_session', methods=['POST'])
def create_session():
    """Create a new attendance session"""
    try:
        data = request.get_json()
        
        date = data.get('date')
        subject = data.get('subject')
        department = data.get('department')
        year = data.get('year')
        division = data.get('division')
        teacher_id = data.get('teacherId')
        
        if not all([date, subject, department, year, division]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        session, error = Attendance.create_session(
            date, subject, department, year, division, teacher_id
        )
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Session created successfully',
            'session_id': session['sessionId'],
            'session': session
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attendance_bp.route('/api/attendance/real-mark', methods=['POST'])
def real_time_mark():
    """Real-time face recognition and attendance marking"""
    try:
        data = request.get_json()
        
        image = data.get('image')  # Base64 encoded
        session_id = data.get('session_id')
        
        # Optional filters for demo mode (when no session_id)
        department = data.get('department')
        year = data.get('year')
        division = data.get('division')
        
        if not image:
            return jsonify({
                'success': False,
                'error': 'No image provided'
            }), 400
        
        # Recognize faces in the image
        results = recognizer.recognize_from_base64(image, detector)
        
        if not results:
            return jsonify({
                'success': True,
                'message': 'No faces detected',
                'faces': []
            }), 200
        
        # If session_id is provided, mark attendance
        if session_id:
            session = Attendance.get_session(session_id)
            if not session:
                return jsonify({
                    'success': False,
                    'error': 'Session not found'
                }), 404
            
            # Mark attendance for recognized students
            for result in results:
                if result['match']:
                    student_id = result['match']['studentId']
                    confidence = result['match']['confidence']
                    
                    # Mark attendance
                    record, error = Attendance.mark_attendance(
                        session_id, student_id, confidence
                    )
                    
                    if error and error != "Already marked":
                        print(f"Error marking attendance for {student_id}: {error}")
        
        return jsonify({
            'success': True,
            'faces': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        print(f"Error in real-time recognition: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attendance_bp.route('/api/attendance/session/<session_id>', methods=['GET'])
def get_session_attendance(session_id):
    """Get attendance records for a session"""
    try:
        session = Attendance.get_session(session_id)
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        records = Attendance.get_session_attendance(session_id)
        
        # Enrich records with student details
        enriched_records = []
        for record in records:
            student = Student.find_by_id(record['studentId'])
            if student:
                record['student'] = student
            enriched_records.append(record)
        
        return jsonify({
            'success': True,
            'session': session,
            'attendance': enriched_records,
            'count': len(enriched_records)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attendance_bp.route('/api/attendance/student/<student_id>', methods=['GET'])
def get_student_attendance(student_id):
    """Get attendance history for a student"""
    try:
        student = Student.find_by_id(student_id)
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
        
        records = Attendance.get_student_attendance(student_id)
        
        # Enrich records with session details
        enriched_records = []
        for record in records:
            session = Attendance.get_session(record['sessionId'])
            if session:
                record['session'] = session
            enriched_records.append(record)
        
        return jsonify({
            'success': True,
            'student': student,
            'attendance': enriched_records,
            'count': len(enriched_records)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attendance_bp.route('/api/attendance/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions or filter by parameters"""
    try:
        department = request.args.get('department')
        year = request.args.get('year')
        division = request.args.get('division')
        date = request.args.get('date')
        
        if any([department, year, division, date]):
            sessions = Attendance.get_sessions_by_filters(department, year, division, date)
        else:
            sessions = Attendance.get_all_sessions()
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'count': len(sessions)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attendance_bp.route('/api/attendance/export', methods=['POST'])
def export_attendance():
    """Export attendance to Excel"""
    try:
        data = request.get_json()
        
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session ID required'
            }), 400
        
        session = Attendance.get_session(session_id)
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        records = Attendance.get_session_attendance(session_id)
        
        # Create Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Attendance"
        
        # Headers
        ws.append([
            'Student ID',
            'Name',
            'Department',
            'Year',
            'Division',
            'Timestamp',
            'Status'
        ])
        
        # Data rows
        for record in records:
            student = Student.find_by_id(record['studentId'])
            if student:
                ws.append([
                    student['studentId'],
                    student['name'],
                    student['department'],
                    student['year'],
                    student['division'],
                    record['timestamp'],
                    record['status']
                ])
        
        # Save file
        filename = f"attendance_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        wb.save(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Attendance exported successfully',
            'filename': filename,
            'filepath': filepath
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@attendance_bp.route('/api/attendance/stats', methods=['GET'])
def get_attendance_stats():
    """Get attendance statistics"""
    try:
        department = request.args.get('department')
        year = request.args.get('year')
        division = request.args.get('division')
        
        stats = Attendance.get_attendance_stats(department, year, division)
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
