import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'face_recognition_attendance')
    
    # Admin Configuration
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Upload Configuration
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.getenv('UPLOAD_FOLDER', 'uploads'))
    FACE_IMAGES_FOLDER = os.path.join(BASE_DIR, os.getenv('FACE_IMAGES_FOLDER', 'uploads/faces'))
    MODELS_FOLDER = os.path.join(BASE_DIR, os.getenv('MODELS_FOLDER', 'models'))
    
    # Face Recognition Configuration
    FACE_RECOGNITION_THRESHOLD = int(os.getenv('FACE_RECOGNITION_THRESHOLD', '110'))  # Increased to 110 for better matching
    MIN_FACE_SIZE = (int(os.getenv('MIN_FACE_SIZE', '20')), int(os.getenv('MIN_FACE_SIZE', '20')))  # Reduced from 30
    SCALE_FACTOR = float(os.getenv('SCALE_FACTOR', '1.05'))  # Reduced from 1.1 for better detection
    MIN_NEIGHBORS = int(os.getenv('MIN_NEIGHBORS', '3'))  # Reduced from 5 for more lenient detection
    
    # Haar Cascade Path
    HAAR_CASCADE_PATH = os.path.join(BASE_DIR, 'data', 'haarcascade_frontalface_default.xml')
    
    # LBPH Model Path
    LBPH_MODEL_PATH = os.path.join(MODELS_FOLDER, 'lbph_model.yml')
    
    # CNN Model Paths
    CNN_MODEL_PATH = os.path.join(MODELS_FOLDER, 'facenet_model.pt')
    EMBEDDINGS_PATH = os.path.join(MODELS_FOLDER, 'face_embeddings.pkl')
    
    # Face Recognition Mode: 'lbph' or 'cnn'
    FACE_RECOGNITION_MODE = os.getenv('FACE_RECOGNITION_MODE', 'cnn')
    
    # CNN Similarity Threshold (cosine distance, lower is better)
    # 0.35 means faces with distance < 0.35 are considered matches (VERY STRICT)
    # Lower threshold = fewer false positives, perfect for classroom scenarios
    # Prevents showing student names in empty spaces
    CNN_SIMILARITY_THRESHOLD = float(os.getenv('CNN_SIMILARITY_THRESHOLD', '0.35'))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # JSON Fallback Storage
    JSON_STORAGE_PATH = os.path.join(BASE_DIR, 'data', 'storage')
    
    @staticmethod
    def init_app():
        """Initialize application directories"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.FACE_IMAGES_FOLDER, exist_ok=True)
        os.makedirs(Config.MODELS_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(Config.BASE_DIR, 'data'), exist_ok=True)
        os.makedirs(Config.JSON_STORAGE_PATH, exist_ok=True)
