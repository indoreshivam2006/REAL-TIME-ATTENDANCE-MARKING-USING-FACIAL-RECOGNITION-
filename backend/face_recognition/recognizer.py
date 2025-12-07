import cv2
import numpy as np
import os
import pickle
from config import Config
from models.student import Student

class FaceRecognizer:
    """LBPH Face Recognition"""
    
    def __init__(self):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.model_path = Config.LBPH_MODEL_PATH
        self.is_trained = False
        self.label_map = {}  # Maps label numbers to student IDs
        self.reverse_label_map = {}  # Maps student IDs to label numbers
        
        # Try to load existing model
        self.load_model()
        
        print("✅ Face recognizer initialized")
    
    def train(self, force_retrain=False):
        """
        Train the LBPH model with all registered students
        
        Args:
            force_retrain: Force retraining even if model exists
        
        Returns:
            Success status and message
        """
        if self.is_trained and not force_retrain:
            return True, "Model already trained"
        
        # Get all students with face images
        students = Student.get_all()
        
        faces = []
        labels = []
        label_counter = 0
        self.label_map = {}
        self.reverse_label_map = {}
        
        for student in students:
            face_images = student.get('faceImages', [])
            if not face_images:
                continue
            
            student_id = student['studentId']
            
            # Assign label to this student
            if student_id not in self.reverse_label_map:
                self.reverse_label_map[student_id] = label_counter
                self.label_map[label_counter] = student_id
                label_counter += 1
            
            label = self.reverse_label_map[student_id]
            
            # Load and process each face image
            for img_path in face_images:
                if not os.path.exists(img_path):
                    continue
                
                try:
                    # Read image in grayscale
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is None:
                        continue
                    
                    # Resize to standard size
                    img = cv2.resize(img, (100, 100))
                    
                    # Apply histogram equalization
                    img = cv2.equalizeHist(img)
                    
                    faces.append(img)
                    labels.append(label)
                except Exception as e:
                    print(f"Error processing image {img_path}: {e}")
                    continue
        
        if len(faces) == 0:
            return False, "No face images found for training"
        
        # Train the model
        try:
            self.recognizer.train(faces, np.array(labels))
            self.is_trained = True
            
            # Save the model
            self.save_model()
            
            return True, f"Model trained with {len(faces)} images from {len(self.label_map)} students"
        except Exception as e:
            return False, f"Training failed: {str(e)}"
    
    def predict(self, face_image):
        """
        Predict identity from face image with enhanced accuracy (OPTIMIZED for speed)
        
        Args:
            face_image: Grayscale face image (numpy array)
        
        Returns:
            (student_id, confidence) or (None, None) if not recognized
        """
        if not self.is_trained:
            return None, None
        
        try:
            # Ensure image is correct size
            if face_image.shape != (100, 100):
                face_image = cv2.resize(face_image, (100, 100))
            
            # Apply CLAHE for better contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            face_image = clahe.apply(face_image)
            
            # Normalize
            face_image = cv2.normalize(face_image, None, 0, 255, cv2.NORM_MINMAX)
            
            # OPTIMIZED: Reduced to 3 predictions instead of 5 for faster processing
            predictions = []
            confidences = []
            
            # Original prediction
            label1, conf1 = self.recognizer.predict(face_image)
            predictions.append(label1)
            confidences.append(conf1)
            
            # Prediction with brightness adjustment (only 2 variations instead of 4)
            brightened = cv2.convertScaleAbs(face_image, alpha=1.1, beta=10)
            label2, conf2 = self.recognizer.predict(brightened)
            predictions.append(label2)
            confidences.append(conf2)
            
            darkened = cv2.convertScaleAbs(face_image, alpha=0.9, beta=-10)
            label3, conf3 = self.recognizer.predict(darkened)
            predictions.append(label3)
            confidences.append(conf3)
            
            # Find most common prediction (voting)
            from collections import Counter
            label_counts = Counter(predictions)
            most_common_label = label_counts.most_common(1)[0][0]
            
            # Get average confidence for the most common label
            matching_confidences = [confidences[i] for i, l in enumerate(predictions) if l == most_common_label]
            avg_confidence = np.mean(matching_confidences)
            
            # OPTIMIZED: Threshold set to 110 for good balance (was 90)
            if avg_confidence < 110 and label_counts[most_common_label] >= 2:
                student_id = self.label_map.get(most_common_label)
                print(f"✅ Match: {student_id} (conf: {avg_confidence:.1f}, votes: {label_counts[most_common_label]}/3)")
                return student_id, avg_confidence
            else:
                return None, avg_confidence
                
        except Exception as e:
            print(f"Prediction error: {e}")
            return None, None
    
    def save_model(self):
        """Save trained model and label mappings"""
        try:
            # Save LBPH model
            self.recognizer.save(self.model_path)
            
            # Save label mappings
            mappings_path = self.model_path.replace('.yml', '_mappings.pkl')
            with open(mappings_path, 'wb') as f:
                pickle.dump({
                    'label_map': self.label_map,
                    'reverse_label_map': self.reverse_label_map
                }, f)
            
            print(f"✅ Model saved to {self.model_path}")
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_model(self):
        """Load trained model and label mappings"""
        try:
            if not os.path.exists(self.model_path):
                print("ℹ️  No trained model found")
                return False
            
            # Load LBPH model
            self.recognizer.read(self.model_path)
            
            # Load label mappings
            mappings_path = self.model_path.replace('.yml', '_mappings.pkl')
            if os.path.exists(mappings_path):
                with open(mappings_path, 'rb') as f:
                    mappings = pickle.load(f)
                    self.label_map = mappings['label_map']
                    self.reverse_label_map = mappings['reverse_label_map']
            
            self.is_trained = True
            print(f"✅ Model loaded from {self.model_path}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def recognize_from_base64(self, base64_string, detector):
        """
        Recognize faces from base64 encoded image
        
        Args:
            base64_string: Base64 encoded image
            detector: FaceDetector instance
        
        Returns:
            List of recognition results
        """
        import base64
        
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to image
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return []
        
        # Detect faces
        faces = detector.detect_faces(image)
        
        results = []
        for idx, box in enumerate(faces):
            # Extract face
            face_img = detector.extract_face(image, box)
            
            # Simplified quality check (faster)
            mean_brightness = np.mean(face_img)
            if mean_brightness < 30 or mean_brightness > 225:
                print(f"⚠️  Face {idx} rejected: poor lighting")
                results.append({'box': box.tolist(), 'match': None})
                continue
            
            # Recognize
            student_id, confidence = self.predict(face_img)
            
            result = {'box': box.tolist(), 'match': None}
            
            if student_id:
                # Get student details
                student = Student.find_by_id(student_id)
                if student and confidence < 110:  # Increased from 90 for better matching
                    result['match'] = {
                        'studentId': student_id,
                        'name': student.get('name'),
                        'confidence': float(confidence)
                    }
                    print(f"✅ MATCH: {student.get('name')} (conf: {confidence:.1f})")
            
            results.append(result)
        
        print(f"📊 Faces: {len(faces)}, Matched: {sum(1 for r in results if r['match'])}")
        return results
