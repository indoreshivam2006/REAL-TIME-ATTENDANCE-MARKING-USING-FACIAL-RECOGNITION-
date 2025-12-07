from flask import Blueprint, request, jsonify
from models.teacher import Teacher

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    """Teacher registration endpoint"""
    try:
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('userType', 'teacher')
        
        if not all([username, email, password]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        if user_type != 'teacher':
            return jsonify({
                'success': False,
                'error': 'Only teacher registration is supported'
            }), 400
        
        # Create teacher
        teacher, error = Teacher.create(username, email, password)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Teacher registered successfully',
            'user': teacher
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/api/signin', methods=['POST'])
def signin():
    """Teacher login endpoint"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('userType', 'teacher')
        
        if not all([email, password]):
            return jsonify({
                'success': False,
                'error': 'Missing email or password'
            }), 400
        
        if user_type != 'teacher':
            return jsonify({
                'success': False,
                'error': 'Only teacher login is supported'
            }), 400
        
        # Verify credentials
        teacher, error = Teacher.verify_password(email, password)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 401
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': teacher
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    try:
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
