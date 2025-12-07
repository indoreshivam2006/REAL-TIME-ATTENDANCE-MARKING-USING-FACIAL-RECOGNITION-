from flask import Blueprint, request, jsonify
from models.teacher import Teacher
from models.student import Student
from models.attendance import Attendance
from config import Config

admin_bp = Blueprint('admin', __name__)

def verify_admin(username, password):
    """Verify admin credentials"""
    return (username == Config.ADMIN_USERNAME and 
            password == Config.ADMIN_PASSWORD)

@admin_bp.route('/api/admin/signin', methods=['POST'])
def admin_signin():
    """Admin login"""
    try:
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({
                'success': False,
                'error': 'Missing credentials'
            }), 400
        
        if verify_admin(username, password):
            return jsonify({
                'success': True,
                'message': 'Admin login successful',
                'user': {
                    'username': username,
                    'userType': 'admin'
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid admin credentials'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_teachers = len(Teacher.get_all())
        total_students = len(Student.get_all())
        total_sessions = len(Attendance.get_all_sessions())
        
        # Get recent sessions
        sessions = Attendance.get_all_sessions()
        recent_sessions = sorted(
            sessions,
            key=lambda x: x.get('createdAt', ''),
            reverse=True
        )[:5]
        
        return jsonify({
            'success': True,
            'stats': {
                'totalTeachers': total_teachers,
                'totalStudents': total_students,
                'totalSessions': total_sessions,
                'recentSessions': recent_sessions
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/teachers', methods=['GET'])
def get_all_teachers():
    """Get all teachers"""
    try:
        teachers = Teacher.get_all()
        
        return jsonify({
            'success': True,
            'teachers': teachers,
            'count': len(teachers)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/teachers/<teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    """Delete a teacher"""
    try:
        success = Teacher.delete(teacher_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Teacher not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Teacher deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/students', methods=['GET'])
def get_all_students():
    """Get all students"""
    try:
        students = Student.get_all()
        
        return jsonify({
            'success': True,
            'students': students,
            'count': len(students)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/students/<student_id>', methods=['DELETE'])
def delete_student_admin(student_id):
    """Delete a student (admin)"""
    try:
        success = Student.delete(student_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Student deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/sessions', methods=['GET'])
def get_all_sessions():
    """Get all sessions"""
    try:
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

@admin_bp.route('/api/admin/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session"""
    try:
        success = Attendance.delete_session(session_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Session deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/analytics', methods=['GET'])
def get_analytics():
    """Get attendance analytics"""
    try:
        # Get all sessions
        sessions = Attendance.get_all_sessions()
        
        # Group by department
        dept_stats = {}
        for session in sessions:
            dept = session.get('department', 'Unknown')
            if dept not in dept_stats:
                dept_stats[dept] = {
                    'sessions': 0,
                    'totalPresent': 0
                }
            dept_stats[dept]['sessions'] += 1
            dept_stats[dept]['totalPresent'] += session.get('totalPresent', 0)
        
        # Get total students per department
        students = Student.get_all()
        dept_students = {}
        for student in students:
            dept = student.get('department', 'Unknown')
            dept_students[dept] = dept_students.get(dept, 0) + 1
        
        return jsonify({
            'success': True,
            'analytics': {
                'departmentStats': dept_stats,
                'departmentStudents': dept_students,
                'totalSessions': len(sessions)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
