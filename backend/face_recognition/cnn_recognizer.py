"""
CNN-based Face Recognizer using FaceNet
Replaces LBPH with deep learning approach for higher accuracy
"""

import torch
import torch.nn.functional as F
import cv2
import numpy as np
import os
import pickle
from config import Config
from models.student import Student
from face_recognition.facenet_model import get_facenet_model
from face_recognition.mtcnn_detector import get_face_detector
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import torchvision.transforms as transforms
from typing import Optional, Tuple, List, Dict


class CNNFaceRecognizer:
    """CNN-based Face Recognition using FaceNet"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🔧 Using device: {self.device}")
        
        # Load FaceNet model
        self.model = get_facenet_model(pretrained='vggface2', device=self.device)
        self.model.eval()
        
        # Face detector
        self.detector = get_face_detector(min_confidence=0.5)
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        
        # Embeddings storage
        self.embeddings_path = Config.EMBEDDINGS_PATH
        self.embeddings = {}  # {student_id: [embedding1, embedding2, ...]}
        self.is_trained = False
        
        # Load existing embeddings
        self.load_embeddings()
        
        print("✅ CNN Face recognizer initialized")
    
    def preprocess_face(self, face_image):
        """
        Preprocess face image for FaceNet
        
        Args:
            face_image: RGB face image (numpy array or PIL Image)
        
        Returns:
            Preprocessed tensor
        """
        if isinstance(face_image, np.ndarray):
            # Convert numpy array to PIL Image
            face_image = Image.fromarray(face_image)
        
        # Ensure correct size (160x160 for FaceNet)
        if face_image.size != (160, 160):
            face_image = face_image.resize((160, 160), Image.BILINEAR)
        
        # Apply transformations
        face_tensor = self.transform(face_image)
        
        return face_tensor.unsqueeze(0)  # Add batch dimension
    
    def get_embedding(self, face_image):
        """
        Extract face embedding using FaceNet
        
        Args:
            face_image: RGB face image (160x160)
        
        Returns:
            512-dimensional embedding vector
        """
        with torch.no_grad():
            face_tensor = self.preprocess_face(face_image)
            face_tensor = face_tensor.to(self.device)
            embedding = self.model(face_tensor)
            embedding = embedding.cpu().numpy().flatten()
        
        return embedding
    
    def train(self, force_retrain=False):
        """
        Train the CNN model by extracting embeddings for all registered students
        
        Args:
            force_retrain: Force retraining even if embeddings exist
        
        Returns:
            Success status and message
        """
        if self.is_trained and not force_retrain:
            return True, "Model already trained"
        
        # Get all students with face images
        students = Student.get_all()
        
        embeddings = {}
        total_images = 0
        failed_images = 0
        
        print(f"🔄 Training CNN model with {len(students)} students...")
        
        for student in students:
            face_images = student.get('faceImages', [])
            if not face_images:
                continue
            
            student_id = student['studentId']
            student_embeddings = []
            
            # Extract embeddings for each face image
            for img_path in face_images:
                if not os.path.exists(img_path):
                    failed_images += 1
                    continue
                
                try:
                    # Read image
                    img = cv2.imread(img_path)
                    if img is None:
                        failed_images += 1
                        continue
                    
                    # Detect face (in case the saved image is full image, not just face)
                    faces = self.detector.detect_faces(img)
                    
                    if len(faces) > 0:
                        # Extract the largest face
                        largest_face = max(faces, key=lambda box: box[2] * box[3])
                        face_rgb = self.detector.extract_face(img, largest_face, output_size=160)
                    else:
                        # If no face detected, assume the image is already a cropped face
                        face_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        face_rgb = cv2.resize(face_rgb, (160, 160))
                    
                    # Get embedding
                    embedding = self.get_embedding(face_rgb)
                    student_embeddings.append(embedding)
                    total_images += 1
                    
                except Exception as e:
                    print(f"❌ Error processing {img_path}: {e}")
                    failed_images += 1
                    continue
            
            if len(student_embeddings) > 0:
                embeddings[student_id] = student_embeddings
                print(f"✅ {student_id}: {len(student_embeddings)} embeddings")
        
        if len(embeddings) == 0:
            return False, "No face images found for training"
        
        # Save embeddings
        self.embeddings = embeddings
        self.is_trained = True
        self.save_embeddings()
        
        message = f"Model trained with {total_images} images from {len(embeddings)} students"
        if failed_images > 0:
            message += f" ({failed_images} images failed)"
        
        print(f"✅ {message}")
        return True, message
    
    def predict(self, face_image):
        """
        Predict identity from face image using cosine similarity
        
        Args:
            face_image: RGB face image (160x160)
        
        Returns:
            (student_id, confidence) or (None, None) if not recognized
            Note: For cosine similarity, lower distance = better match
        """
        if not self.is_trained or len(self.embeddings) == 0:
            return None, None
        
        try:
            # Get embedding for input face
            query_embedding = self.get_embedding(face_image)
            
            # Compare with all stored embeddings
            best_match = None
            best_distance = float('inf')
            
            for student_id, student_embeddings in self.embeddings.items():
                for stored_embedding in student_embeddings:
                    # Calculate cosine distance (1 - cosine similarity)
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        stored_embedding.reshape(1, -1)
                    )[0][0]
                    distance = 1 - similarity
                    
                    if distance < best_distance:
                        best_distance = distance
                        best_match = student_id
            
            # Threshold for recognition (cosine distance < 0.6 means good match)
            threshold = Config.CNN_SIMILARITY_THRESHOLD
            
            if best_distance < threshold:
                # Convert distance to confidence percentage (0-100)
                confidence = (1 - best_distance) * 100
                print(f"✅ Match: {best_match} (distance: {best_distance:.3f}, confidence: {confidence:.1f}%)")
                return best_match, best_distance
            else:
                print(f"❌ No match (best distance: {best_distance:.3f}, threshold: {threshold})")
                return None, best_distance
                
        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def save_embeddings(self):
        """Save embeddings to disk"""
        try:
            os.makedirs(os.path.dirname(self.embeddings_path), exist_ok=True)
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(self.embeddings, f)
            print(f"✅ Embeddings saved to {self.embeddings_path}")
            return True
        except Exception as e:
            print(f"Error saving embeddings: {e}")
            return False
    
    def load_embeddings(self):
        """Load embeddings from disk"""
        try:
            if not os.path.exists(self.embeddings_path):
                print("ℹ️  No trained embeddings found")
                return False
            
            with open(self.embeddings_path, 'rb') as f:
                self.embeddings = pickle.load(f)
            
            self.is_trained = len(self.embeddings) > 0
            print(f"✅ Loaded embeddings for {len(self.embeddings)} students")
            return True
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            return False
    
    def recognize_from_base64(self, base64_string, detector=None):
        """
        Recognize faces from base64 encoded image with STRICT accuracy controls
        
        Args:
            base64_string: Base64 encoded image
            detector: Not used (kept for compatibility)
        
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
        faces = self.detector.detect_faces(image)
        
        if len(faces) == 0:
            return []
        
        # Filter faces by minimum size (remove tiny detections)
        MIN_FACE_SIZE = 80  # Minimum 80x80 pixels
        filtered_faces = []
        for box in faces:
            x, y, w, h = box
            if w >= MIN_FACE_SIZE and h >= MIN_FACE_SIZE:
                filtered_faces.append(box)
        
        if len(filtered_faces) == 0:
            print("⚠️  All detected faces too small, ignoring")
            return []
        
        # Remove duplicate/overlapping faces (same person detected multiple times)
        unique_faces = self._remove_duplicate_faces(filtered_faces)
        print(f"📊 Detected {len(faces)} faces, filtered to {len(unique_faces)} unique faces")
        
        results = []
        recognized_students = set()  # Track already recognized students
        
        for idx, box in enumerate(unique_faces):
            # Extract face
            face_rgb = self.detector.extract_face(image, box, output_size=160)
            
            # Quality check - reject poor quality faces
            quality_score = self._assess_face_quality(face_rgb)
            if quality_score < 0.3:
                print(f"⚠️  Face {idx} rejected: poor quality (score: {quality_score:.2f})")
                results.append({'box': box.tolist(), 'match': None})
                continue
            
            # Recognize with STRICT threshold
            student_id, distance = self.predict(face_rgb)
            
            result = {'box': box.tolist(), 'match': None}
            
            if student_id:
                # CRITICAL: Prevent duplicate recognition of same student
                if student_id in recognized_students:
                    print(f"⚠️  {student_id} already recognized, skipping duplicate")
                    continue
                
                # Get student details
                student = Student.find_by_id(student_id)
                if student:
                    confidence = (1 - distance) * 100  # Convert to percentage
                    
                    # STRICT VALIDATION: Only accept high confidence matches
                    if confidence >= 60:  # At least 60% confidence required
                        result['match'] = {
                            'studentId': student_id,
                            'name': student.get('name'),
                            'confidence': float(confidence),
                            'distance': float(distance)
                        }
                        recognized_students.add(student_id)
                        print(f"✅ MATCH: {student.get('name')} (confidence: {confidence:.1f}%, distance: {distance:.3f})")
                    else:
                        print(f"❌ REJECTED: {student.get('name')} (confidence too low: {confidence:.1f}%)")
            
            results.append(result)
        
        matched_count = sum(1 for r in results if r['match'])
        print(f"📊 Unique faces: {len(unique_faces)}, Matched: {matched_count}")
        return results
    
    def _remove_duplicate_faces(self, faces):
        """
        Remove duplicate/overlapping face detections (same person detected multiple times)
        Uses IoU (Intersection over Union) to detect overlaps
        """
        if len(faces) <= 1:
            return faces
        
        # Convert to numpy array for easier processing
        boxes = np.array(faces)
        
        # Calculate areas
        areas = boxes[:, 2] * boxes[:, 3]
        
        # Sort by area (largest first)
        order = areas.argsort()[::-1]
        
        keep = []
        while len(order) > 0:
            i = order[0]
            keep.append(i)
            
            if len(order) == 1:
                break
            
            # Calculate IoU with remaining boxes
            xx1 = np.maximum(boxes[i, 0], boxes[order[1:], 0])
            yy1 = np.maximum(boxes[i, 1], boxes[order[1:], 1])
            xx2 = np.minimum(boxes[i, 0] + boxes[i, 2], boxes[order[1:], 0] + boxes[order[1:], 2])
            yy2 = np.minimum(boxes[i, 1] + boxes[i, 3], boxes[order[1:], 1] + boxes[order[1:], 3])
            
            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)
            
            intersection = w * h
            union = areas[i] + areas[order[1:]] - intersection
            iou = intersection / union
            
            # Keep only boxes with IoU < 0.3 (not overlapping)
            inds = np.where(iou < 0.3)[0]
            order = order[inds + 1]
        
        return [faces[i] for i in keep]
    
    def _assess_face_quality(self, face_rgb):
        """
        Assess face image quality
        Returns score 0-1 (higher is better)
        """
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2GRAY)
        
        # Check brightness
        mean_brightness = np.mean(gray)
        if mean_brightness < 40 or mean_brightness > 220:
            return 0.1  # Too dark or too bright
        
        # Check contrast
        contrast = np.std(gray)
        if contrast < 30:
            return 0.2  # Too low contrast
        
        # Check sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 100:
            return 0.3  # Too blurry
        
        # Calculate overall quality score
        brightness_score = 1.0 - abs(mean_brightness - 128) / 128
        contrast_score = min(1.0, contrast / 80.0)
        sharpness_score = min(1.0, laplacian_var / 500.0)
        
        quality = (brightness_score + contrast_score + sharpness_score) / 3.0
        return quality
