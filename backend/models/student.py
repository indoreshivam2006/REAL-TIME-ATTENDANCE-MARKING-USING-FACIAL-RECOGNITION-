from datetime import datetime
from models.database import db
import os
import shutil
from config import Config

class Student:
    """Student model for registration and management"""
    
    collection = 'students'
    
    @staticmethod
    def create(name, student_id, department, year, division, email=None, phone=None):
        """Create a new student"""
        # Check if student ID already exists
        existing = db.find_one(Student.collection, {'studentId': student_id})
        if existing:
            return None, "Student ID already registered"
        
        student = {
            'name': name,
            'studentId': student_id,
            'department': department,
            'year': year,
            'division': division,
            'email': email or '',
            'phone': phone or '',
            'faceImages': [],
            'faceEncodings': [],
            'createdAt': datetime.now().isoformat(),
            'isActive': True
        }
        
        result = db.insert_one(Student.collection, student)
        return result, None
    
    @staticmethod
    def find_by_id(student_id):
        """Find student by student ID"""
        return db.find_one(Student.collection, {'studentId': student_id})
    
    @staticmethod
    def find_by_db_id(db_id):
        """Find student by database ID"""
        return db.find_one(Student.collection, {'_id': db_id})
    
    @staticmethod
    def find_by_filters(department=None, year=None, division=None):
        """Find students by filters"""
        query = {}
        if department:
            query['department'] = department
        if year:
            query['year'] = year
        if division:
            query['division'] = division
        
        return db.find(Student.collection, query)
    
    @staticmethod
    def get_all():
        """Get all students"""
        return db.find(Student.collection)
    
    @staticmethod
    def update(student_id, updates):
        """Update student information"""
        updates['updatedAt'] = datetime.now().isoformat()
        return db.update_one(Student.collection, {'studentId': student_id}, updates)
    
    @staticmethod
    def add_face_image(student_id, image_path):
        """Add face image path to student"""
        student = Student.find_by_id(student_id)
        if not student:
            return False
        
        face_images = student.get('faceImages', [])
        face_images.append(image_path)
        
        return db.update_one(
            Student.collection,
            {'studentId': student_id},
            {'faceImages': face_images}
        )
    
    @staticmethod
    def delete(student_id):
        """Delete a student and their face images"""
        student = Student.find_by_id(student_id)
        if not student:
            return False
        
        # Delete face images from filesystem
        for image_path in student.get('faceImages', []):
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error deleting image {image_path}: {e}")
        
        # Delete student folder if exists
        student_folder = os.path.join(Config.FACE_IMAGES_FOLDER, student_id)
        if os.path.exists(student_folder):
            try:
                shutil.rmtree(student_folder)
            except Exception as e:
                print(f"Error deleting folder {student_folder}: {e}")
        
        return db.delete_one(Student.collection, {'studentId': student_id})
    
    @staticmethod
    def search(query):
        """Search students by name or student ID"""
        all_students = db.find(Student.collection)
        results = []
        query_lower = query.lower()
        
        for student in all_students:
            if (query_lower in student.get('name', '').lower() or 
                query_lower in student.get('studentId', '').lower()):
                results.append(student)
        
        return results
    
    @staticmethod
    def get_active_students(department=None, year=None, division=None):
        """Get active students with optional filters"""
        query = {'isActive': True}
        if department:
            query['department'] = department
        if year:
            query['year'] = year
        if division:
            query['division'] = division
        
        return db.find(Student.collection, query)
