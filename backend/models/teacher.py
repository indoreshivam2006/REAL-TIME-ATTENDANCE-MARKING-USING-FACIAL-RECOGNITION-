from datetime import datetime
from models.database import db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class Teacher:
    """Teacher model for authentication and management"""
    
    collection = 'teachers'
    
    @staticmethod
    def create(username, email, password, employee_id=None):
        """Create a new teacher"""
        # Check if email already exists
        existing = db.find_one(Teacher.collection, {'email': email})
        if existing:
            return None, "Email already registered"
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        teacher = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'employeeId': employee_id or f"T{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'createdAt': datetime.now().isoformat(),
            'userType': 'teacher'
        }
        
        result = db.insert_one(Teacher.collection, teacher)
        # Remove password from response
        result.pop('password', None)
        return result, None
    
    @staticmethod
    def find_by_email(email):
        """Find teacher by email"""
        return db.find_one(Teacher.collection, {'email': email})
    
    @staticmethod
    def find_by_id(teacher_id):
        """Find teacher by ID"""
        teacher = db.find_one(Teacher.collection, {'_id': teacher_id})
        if teacher:
            teacher.pop('password', None)
        return teacher
    
    @staticmethod
    def verify_password(email, password):
        """Verify teacher password"""
        teacher = Teacher.find_by_email(email)
        if not teacher:
            return None, "Teacher not found"
        
        if bcrypt.check_password_hash(teacher['password'], password):
            teacher.pop('password', None)
            return teacher, None
        else:
            return None, "Invalid password"
    
    @staticmethod
    def get_all():
        """Get all teachers"""
        teachers = db.find(Teacher.collection)
        for teacher in teachers:
            teacher.pop('password', None)
        return teachers
    
    @staticmethod
    def update(teacher_id, updates):
        """Update teacher information"""
        # Don't allow password update through this method
        updates.pop('password', None)
        return db.update_one(Teacher.collection, {'_id': teacher_id}, updates)
    
    @staticmethod
    def delete(teacher_id):
        """Delete a teacher"""
        return db.delete_one(Teacher.collection, {'_id': teacher_id})
