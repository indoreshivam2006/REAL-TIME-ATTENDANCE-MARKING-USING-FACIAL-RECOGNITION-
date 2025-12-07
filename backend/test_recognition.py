#!/usr/bin/env python
"""Test face recognition with actual images"""

import sys
import os
import cv2

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from face_recognition.recognizer import FaceRecognizer
from face_recognition.detector import FaceDetector
from config import Config

# Initialize
Config.init_app()
recognizer = FaceRecognizer()
detector = FaceDetector()

print("=" * 60)
print("Testing Face Recognition")
print("=" * 60)

# Get student images
student_folder = os.path.join(Config.FACE_IMAGES_FOLDER, "jlu08315")
if not os.path.exists(student_folder):
    print("❌ Student folder not found!")
    sys.exit(1)

# Get first image
images = [f for f in os.listdir(student_folder) if f.endswith('.jpg')]
if not images:
    print("❌ No images found!")
    sys.exit(1)

test_image_path = os.path.join(student_folder, images[0])
print(f"\nTesting with: {test_image_path}")

# Load image
img = cv2.imread(test_image_path, cv2.IMREAD_GRAYSCALE)
if img is None:
    print("❌ Failed to load image!")
    sys.exit(1)

print(f"Image shape: {img.shape}")

# Ensure correct size
if img.shape != (100, 100):
    img = cv2.resize(img, (100, 100))
    print(f"Resized to: {img.shape}")

# Apply histogram equalization
img = cv2.equalizeHist(img)

# Predict
print("\nPredicting...")
student_id, confidence = recognizer.predict(img)

print(f"\nResults:")
print(f"  Student ID: {student_id}")
print(f"  Confidence: {confidence}")
print(f"  Threshold: {Config.FACE_RECOGNITION_THRESHOLD}")
print(f"  Match: {'YES ✅' if student_id else 'NO ❌'}")

if confidence:
    print(f"\n  Confidence is {'BELOW' if confidence < Config.FACE_RECOGNITION_THRESHOLD else 'ABOVE'} threshold")
    print(f"  Difference: {abs(confidence - Config.FACE_RECOGNITION_THRESHOLD)}")

print("\n" + "=" * 60)
