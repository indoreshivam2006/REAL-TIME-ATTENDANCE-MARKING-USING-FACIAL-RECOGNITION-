#!/usr/bin/env python
"""Manual model training script"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from face_recognition.recognizer import FaceRecognizer
from config import Config

# Initialize directories
Config.init_app()

print("=" * 60)
print("Manual Face Recognition Model Training")
print("=" * 60)

# Initialize recognizer
recognizer = FaceRecognizer()

# Train the model
print("\nStarting training...")
success, message = recognizer.train(force_retrain=True)

if success:
    print(f"✅ {message}")
    print(f"\nModel saved to: {Config.LBPH_MODEL_PATH}")
    print(f"Label mappings: {recognizer.label_map}")
else:
    print(f"❌ {message}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Training Complete!")
print("=" * 60)
