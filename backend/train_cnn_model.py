#!/usr/bin/env python
"""Manual CNN model training script"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from face_recognition.cnn_recognizer import CNNFaceRecognizer
from config import Config

# Initialize directories
Config.init_app()

print("=" * 60)
print("CNN Face Recognition Model Training")
print("=" * 60)

# Initialize recognizer
recognizer = CNNFaceRecognizer()

# Train the model
print("\nStarting training...")
success, message = recognizer.train(force_retrain=True)

if success:
    print(f"✅ {message}")
    print(f"\nEmbeddings saved to: {Config.EMBEDDINGS_PATH}")
    print(f"Number of students: {len(recognizer.embeddings)}")
else:
    print(f"❌ {message}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Training Complete!")
print("=" * 60)
