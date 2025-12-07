import cv2
import numpy as np
from config import Config
import os

class FaceDetector:
    """Face detection using Haar Cascade"""
    
    def __init__(self):
        self.cascade_path = Config.HAAR_CASCADE_PATH
        
        # Check if Haar Cascade file exists, if not use OpenCV's built-in
        if not os.path.exists(self.cascade_path):
            print(f"⚠️  Haar Cascade not found at {self.cascade_path}, using OpenCV default")
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        else:
            self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
        
        if self.face_cascade.empty():
            raise Exception("Failed to load Haar Cascade classifier")
        
        print("✅ Face detector initialized")
    
    def detect_faces(self, image):
        """
        Detect faces in an image
        
        Args:
            image: numpy array (BGR format from cv2)
        
        Returns:
            List of face bounding boxes [(x, y, w, h), ...]
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization for better detection
        gray = cv2.equalizeHist(gray)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=Config.SCALE_FACTOR,
            minNeighbors=Config.MIN_NEIGHBORS,
            minSize=Config.MIN_FACE_SIZE
        )
        
        return faces
    
    def extract_face(self, image, box):
        """
        Extract and preprocess face from image with enhanced quality
        
        Args:
            image: Input image
            box: Face bounding box [x, y, w, h]
        
        Returns:
            Preprocessed grayscale face image (100x100)
        """
        x, y, w, h = box
        
        # Add padding for better context (10% on each side)
        padding = int(min(w, h) * 0.1)
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        
        # Extract face region
        face = image[y:y+h, x:x+w]
        
        # Convert to grayscale if needed
        if len(face.shape) == 3:
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while preserving edges
        face = cv2.bilateralFilter(face, 5, 50, 50)
        
        # Resize to standard size
        face = cv2.resize(face, (100, 100))
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        face = clahe.apply(face)
        
        # Normalize pixel values
        face = cv2.normalize(face, None, 0, 255, cv2.NORM_MINMAX)
        
        return face
    
    def validate_face_quality(self, face_image):
        """
        Validate if the extracted face has good quality for recognition
        
        Args:
            face_image: Grayscale face image
        
        Returns:
            (is_valid, quality_score)
        """
        # Check if image is too dark or too bright
        mean_brightness = np.mean(face_image)
        if mean_brightness < 30 or mean_brightness > 225:
            return False, 0.0
        
        # Check contrast using standard deviation
        contrast = np.std(face_image)
        if contrast < 20:  # Too low contrast
            return False, 0.0
        
        # Calculate sharpness using Laplacian variance
        laplacian_var = cv2.Laplacian(face_image, cv2.CV_64F).var()
        if laplacian_var < 50:  # Too blurry
            return False, 0.0
        
        # Quality score (0-1)
        quality_score = min(1.0, (contrast / 100.0 + laplacian_var / 500.0) / 2)
        
        return True, quality_score
    
    def preprocess_image(self, image_path):
        """
        Load and preprocess image for face detection
        
        Args:
            image_path: Path to image file
        
        Returns:
            Preprocessed image (BGR format)
        """
        image = cv2.imread(image_path)
        if image is None:
            raise Exception(f"Failed to load image: {image_path}")
        
        return image
    
    def detect_and_extract(self, image_path):
        """
        Detect and extract all faces from an image
        
        Args:
            image_path: Path to image file
        
        Returns:
            List of (face_image, box) tuples
        """
        image = self.preprocess_image(image_path)
        faces = self.detect_faces(image)
        
        results = []
        for box in faces:
            face_img = self.extract_face(image, box)
            results.append((face_img, box))
        
        return results
    
    def detect_from_base64(self, base64_string):
        """
        Detect faces from base64 encoded image
        
        Args:
            base64_string: Base64 encoded image string
        
        Returns:
            List of face bounding boxes
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
            raise Exception("Failed to decode base64 image")
        
        return self.detect_faces(image), image
