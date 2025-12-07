"""
MTCNN Face Detector using PyTorch
Multi-task Cascaded Convolutional Networks for face detection
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import cv2
import numpy as np
from PIL import Image
import torchvision.transforms as transforms


class PNet(nn.Module):
    """Proposal Network (P-Net)"""
    
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 10, kernel_size=3)
        self.prelu1 = nn.PReLU(10)
        self.pool1 = nn.MaxPool2d(2, 2, ceil_mode=True)
        self.conv2 = nn.Conv2d(10, 16, kernel_size=3)
        self.prelu2 = nn.PReLU(16)
        self.conv3 = nn.Conv2d(16, 32, kernel_size=3)
        self.prelu3 = nn.PReLU(32)
        self.conv4_1 = nn.Conv2d(32, 2, kernel_size=1)
        self.conv4_2 = nn.Conv2d(32, 4, kernel_size=1)
        
    def forward(self, x):
        x = self.pool1(self.prelu1(self.conv1(x)))
        x = self.prelu2(self.conv2(x))
        x = self.prelu3(self.conv3(x))
        scores = F.softmax(self.conv4_1(x), dim=1)
        boxes = self.conv4_2(x)
        return scores, boxes


class RNet(nn.Module):
    """Refine Network (R-Net)"""
    
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 28, kernel_size=3)
        self.prelu1 = nn.PReLU(28)
        self.pool1 = nn.MaxPool2d(3, 2, ceil_mode=True)
        self.conv2 = nn.Conv2d(28, 48, kernel_size=3)
        self.prelu2 = nn.PReLU(48)
        self.pool2 = nn.MaxPool2d(3, 2, ceil_mode=True)
        self.conv3 = nn.Conv2d(48, 64, kernel_size=2)
        self.prelu3 = nn.PReLU(64)
        self.dense4 = nn.Linear(576, 128)
        self.prelu4 = nn.PReLU(128)
        self.dense5_1 = nn.Linear(128, 2)
        self.dense5_2 = nn.Linear(128, 4)
        
    def forward(self, x):
        x = self.pool1(self.prelu1(self.conv1(x)))
        x = self.pool2(self.prelu2(self.conv2(x)))
        x = self.prelu3(self.conv3(x))
        x = x.view(x.size(0), -1)
        x = self.prelu4(self.dense4(x))
        scores = F.softmax(self.dense5_1(x), dim=1)
        boxes = self.dense5_2(x)
        return scores, boxes


class ONet(nn.Module):
    """Output Network (O-Net)"""
    
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3)
        self.prelu1 = nn.PReLU(32)
        self.pool1 = nn.MaxPool2d(3, 2, ceil_mode=True)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3)
        self.prelu2 = nn.PReLU(64)
        self.pool2 = nn.MaxPool2d(3, 2, ceil_mode=True)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3)
        self.prelu3 = nn.PReLU(64)
        self.pool3 = nn.MaxPool2d(2, 2, ceil_mode=True)
        self.conv4 = nn.Conv2d(64, 128, kernel_size=2)
        self.prelu4 = nn.PReLU(128)
        self.dense5 = nn.Linear(1152, 256)
        self.prelu5 = nn.PReLU(256)
        self.dense6_1 = nn.Linear(256, 2)
        self.dense6_2 = nn.Linear(256, 4)
        self.dense6_3 = nn.Linear(256, 10)
        
    def forward(self, x):
        x = self.pool1(self.prelu1(self.conv1(x)))
        x = self.pool2(self.prelu2(self.conv2(x)))
        x = self.pool3(self.prelu3(self.conv3(x)))
        x = self.prelu4(self.conv4(x))
        x = x.view(x.size(0), -1)
        x = self.prelu5(self.dense5(x))
        scores = F.softmax(self.dense6_1(x), dim=1)
        boxes = self.dense6_2(x)
        landmarks = self.dense6_3(x)
        return scores, boxes, landmarks


class SimpleFaceDetector:
    """
    Simplified face detector using OpenCV's DNN module with pre-trained model
    Faster and more reliable than MTCNN for this use case
    """
    
    def __init__(self, min_confidence=0.7):  # Increased from 0.5 to 0.7 for stricter detection
        self.min_confidence = min_confidence
        
        # Use OpenCV's DNN face detector (ResNet-based)
        # This is more accurate than Haar Cascade and faster than MTCNN
        model_file = "opencv_face_detector_uint8.pb"
        config_file = "opencv_face_detector.pbtxt"
        
        # Try to load DNN model, fallback to Haar Cascade if not available
        try:
            model_path = os.path.join(os.path.dirname(__file__), '..', 'data', model_file)
            config_path = os.path.join(os.path.dirname(__file__), '..', 'data', config_file)
            
            if os.path.exists(model_path) and os.path.exists(config_path):
                self.net = cv2.dnn.readNetFromTensorflow(model_path, config_path)
                self.use_dnn = True
                print("✅ Using DNN face detector")
            else:
                # Fallback to Haar Cascade
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
                self.use_dnn = False
                print("✅ Using Haar Cascade face detector (fallback)")
        except Exception as e:
            print(f"⚠️ DNN model loading failed: {e}")
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            self.use_dnn = False
            print("✅ Using Haar Cascade face detector (fallback)")
    
    def detect_faces(self, image):
        """
        Detect faces in an image with STRICT validation to prevent false positives
        
        Args:
            image: numpy array (BGR format from cv2)
        
        Returns:
            List of face bounding boxes [[x, y, w, h], ...]
        """
        if self.use_dnn:
            faces = self._detect_dnn(image)
        else:
            faces = self._detect_haar(image)
        
        # CRITICAL: Validate each detected face to prevent false positives in empty spaces
        validated_faces = []
        for face in faces:
            if self._validate_face_region(image, face):
                validated_faces.append(face)
            else:
                print(f"⚠️  Rejected false detection at {face}")
        
        return validated_faces if len(validated_faces) > 0 else np.array([])
    
    def _validate_face_region(self, image, box):
        """
        Validate that detected region is actually a face (not empty space/wall/object)
        
        Args:
            image: Full image
            box: Detected face box [x, y, w, h]
        
        Returns:
            True if valid face, False if false positive
        """
        x, y, w, h = [int(v) for v in box]
        
        # Ensure box is within image bounds
        if x < 0 or y < 0 or x + w > image.shape[1] or y + h > image.shape[0]:
            return False
        
        # Extract region
        region = image[y:y+h, x:x+w]
        
        if region.size == 0:
            return False
        
        # 1. Check if region has skin-like colors
        if not self._has_skin_tone(region):
            print(f"❌ No skin tone detected")
            return False
        
        # 2. Check for face-like structure (eyes, nose area)
        if not self._has_face_structure(region):
            print(f"❌ No face structure detected")
            return False
        
        # 3. Check edge density (faces have moderate edges, empty spaces have few)
        if not self._has_appropriate_edge_density(region):
            print(f"❌ Inappropriate edge density")
            return False
        
        return True
    
    def _has_skin_tone(self, region):
        """Check if region contains skin-like colors"""
        # Convert to HSV for better skin detection
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        
        # Skin tone ranges in HSV
        # Lower range (lighter skin)
        lower1 = np.array([0, 20, 70], dtype=np.uint8)
        upper1 = np.array([20, 255, 255], dtype=np.uint8)
        
        # Upper range (darker skin)
        lower2 = np.array([0, 10, 60], dtype=np.uint8)
        upper2 = np.array([25, 150, 255], dtype=np.uint8)
        
        # Create masks
        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Calculate percentage of skin pixels
        skin_percentage = np.sum(mask > 0) / mask.size
        
        # At least 15% of region should be skin-like
        return skin_percentage > 0.15
    
    def _has_face_structure(self, region):
        """Check if region has face-like structure using eye detection"""
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        
        # Try to detect eyes (strong indicator of face)
        try:
            eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )
            eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(10, 10))
            
            # If at least one eye detected, likely a face
            if len(eyes) > 0:
                return True
        except:
            pass
        
        # Alternative: Check for horizontal symmetry (faces are roughly symmetric)
        h, w = gray.shape
        if w > 20:
            left_half = gray[:, :w//2]
            right_half = cv2.flip(gray[:, w//2:], 1)
            
            # Resize to same size
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = cv2.resize(left_half, (min_width, h))
            right_half = cv2.resize(right_half, (min_width, h))
            
            # Calculate similarity
            diff = cv2.absdiff(left_half, right_half)
            symmetry_score = 1.0 - (np.mean(diff) / 255.0)
            
            # Faces have symmetry > 0.6
            if symmetry_score > 0.6:
                return True
        
        return False
    
    def _has_appropriate_edge_density(self, region):
        """Check edge density - faces have moderate edges, empty spaces have very few"""
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        
        # Calculate edge density
        edge_density = np.sum(edges > 0) / edges.size
        
        # Faces typically have 5-30% edge density
        # Empty walls/spaces have <3%
        # Busy backgrounds have >40%
        return 0.05 < edge_density < 0.35
    
    def _detect_dnn(self, image):
        """Detect faces using DNN"""
        h, w = image.shape[:2]
        
        # Prepare image for DNN
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)), 1.0,
            (300, 300), (104.0, 177.0, 123.0)
        )
        
        self.net.setInput(blob)
        detections = self.net.forward()
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > self.min_confidence:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")
                
                # Convert to (x, y, w, h) format
                x = max(0, x1)
                y = max(0, y1)
                width = min(w - x, x2 - x1)
                height = min(h - y, y2 - y1)
                
                if width > 20 and height > 20:  # Minimum face size
                    faces.append(np.array([x, y, width, height]))
        
        return faces if len(faces) > 0 else np.array([])
    
    def _detect_haar(self, image):
        """Detect faces using Haar Cascade with STRICT parameters"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,      # Increased from 1.05 for stricter detection
            minNeighbors=5,       # Increased from 3 to reduce false positives
            minSize=(40, 40)      # Increased from (20, 20) to ignore tiny detections
        )
        
        return faces
    
    def extract_face(self, image, box, output_size=160):
        """
        Extract and preprocess face from image
        
        Args:
            image: Input image (BGR)
            box: Face bounding box [x, y, w, h]
            output_size: Output face size (default: 160x160 for FaceNet)
        
        Returns:
            Preprocessed face image (RGB, 160x160)
        """
        x, y, w, h = [int(v) for v in box]
        
        # Add padding (10% on each side)
        padding = int(min(w, h) * 0.1)
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        
        # Extract face region
        face = image[y:y+h, x:x+w]
        
        # Convert BGR to RGB
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        
        # Resize to output size
        face = cv2.resize(face, (output_size, output_size))
        
        return face


import os

def get_face_detector(min_confidence=0.5):
    """
    Get face detector instance
    
    Args:
        min_confidence: Minimum confidence for face detection
    
    Returns:
        SimpleFaceDetector instance
    """
    return SimpleFaceDetector(min_confidence=min_confidence)
