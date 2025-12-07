from flask import Blueprint, request, jsonify
from models.student import Student
from face_recognition.detector import FaceDetector
from face_recognition.cnn_recognizer import CNNFaceRecognizer
from face_recognition.mtcnn_detector import get_face_detector
from config import Config
import os
import base64
import cv2
import numpy as np
from datetime import datetime

students_bp = Blueprint('students', __name__)

# Initialize face detector and recognizer (CNN-based)
detector = get_face_detector()
recognizer = CNNFaceRecognizer()

@students_bp.route('/api/students/register', methods=['POST'])
def register_student():
    """Register a new student with face images"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        student_id = data.get('studentId')
        department = data.get('department')
        year = data.get('year')
        division = data.get('division')
        email = data.get('email', '')
        phone = data.get('phone', '')
        face_images = data.get('faceImages', [])  # Base64 encoded images
        
        if not all([name, student_id, department, year, division]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        if not face_images or len(face_images) < 3:
            return jsonify({
                'success': False,
                'error': 'At least 3 face images are required'
            }), 400
        
        # Create student record
        student, error = Student.create(name, student_id, department, year, division, email, phone)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Create directory for student's face images
        student_folder = os.path.join(Config.FACE_IMAGES_FOLDER, student_id)
        os.makedirs(student_folder, exist_ok=True)
        
        # Save face images
        saved_images = []
        failed_images = []
        
        print(f"Processing {len(face_images)} images for student {student_id}")
        
        for idx, img_data in enumerate(face_images):
            try:
                # Remove data URL prefix if present
                if ',' in img_data:
                    img_data = img_data.split(',')[1]
                
                # Decode base64
                img_bytes = base64.b64decode(img_data)
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is None:
                    print(f"Failed to decode image {idx}")
                    failed_images.append(idx)
                    continue
                
                # Try to detect face in image
                faces = detector.detect_faces(img)
                
                if len(faces) > 0:
                    # Extract the largest face (RGB, 160x160 for CNN)
                    largest_face = max(faces, key=lambda box: box[2] * box[3])
                    face_img = detector.extract_face(img, largest_face, output_size=160)
                    # Convert RGB to BGR for saving with OpenCV
                    face_img = cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR)
                    print(f"Face detected in image {idx}, size: {largest_face[2]}x{largest_face[3]}")
                else:
                    # No face detected, but save the whole image resized
                    print(f"No face detected in image {idx}, saving full image")
                    # Resize to 160x160 for CNN
                    face_img = cv2.resize(img, (160, 160))
                
                # Save face image
                img_filename = f"{student_id}_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.jpg"
                img_path = os.path.join(student_folder, img_filename)
                
                # Save the image
                save_success = cv2.imwrite(img_path, face_img)
                
                if save_success:
                    saved_images.append(img_path)
                    print(f"✅ Saved image {idx} to {img_path}")
                    
                    # Update student record with image path
                    Student.add_face_image(student_id, img_path)
                else:
                    print(f"❌ Failed to save image {idx}")
                    failed_images.append(idx)
                
            except Exception as e:
                print(f"❌ Error processing image {idx}: {e}")
                import traceback
                traceback.print_exc()
                failed_images.append(idx)
                continue
        
        print(f"Saved {len(saved_images)} images, failed {len(failed_images)} images")
        
        if len(saved_images) == 0:
            # Delete student if no images were saved
            Student.delete(student_id)
            return jsonify({
                'success': False,
                'error': 'No valid face images could be processed'
            }), 400
        
        # Retrain the recognition model automatically
        print(f"🔄 Auto-training model with {len(saved_images)} new images...")
        success, message = recognizer.train(force_retrain=True)
        
        if success:
            print(f"✅ Model trained successfully: {message}")
        else:
            print(f"⚠️  Model training failed: {message}")
        
        return jsonify({
            'success': True,
            'message': f'Student registered with {len(saved_images)} face images',
            'student': student,
            'modelTraining': {
                'success': success,
                'message': message
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@students_bp.route('/api/students', methods=['GET'])
def get_students():
    """Get all students or filter by department/year/division"""
    try:
        department = request.args.get('department')
        year = request.args.get('year')
        division = request.args.get('division')
        
        if department or year or division:
            students = Student.find_by_filters(department, year, division)
        else:
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

@students_bp.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """Get student by ID"""
    try:
        student = Student.find_by_id(student_id)
        
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
        
        return jsonify({
            'success': True,
            'student': student
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@students_bp.route('/api/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    """Update student information"""
    try:
        data = request.get_json()
        
        # Remove fields that shouldn't be updated
        data.pop('_id', None)
        data.pop('studentId', None)
        data.pop('faceImages', None)
        data.pop('createdAt', None)
        
        success = Student.update(student_id, data)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Student updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@students_bp.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student"""
    try:
        success = Student.delete(student_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Student not found'
            }), 404
        
        # Retrain model after deletion
        recognizer.train(force_retrain=True)
        
        return jsonify({
            'success': True,
            'message': 'Student deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@students_bp.route('/api/students/search', methods=['GET'])
def search_students():
    """Search students by name or ID"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        students = Student.search(query)
        
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
