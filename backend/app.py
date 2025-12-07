from flask import Flask, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from config import Config

# Initialize directories first
Config.init_app()

# Import routes after config initialization
from routes.auth import auth_bp
from routes.students import students_bp
from routes.attendance import attendance_bp
from routes.admin import admin_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
bcrypt = Bcrypt(app)
CORS(app, resources={
    r"/api/*": {
        "origins": Config.CORS_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(students_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(admin_bp)

# Root endpoint
@app.route('/')
def index():
    return jsonify({
        'message': 'Face Recognition Attendance System API',
        'version': '1.0.0',
        'status': 'running'
    })

# Health check endpoint
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Face Recognition Attendance System - Backend Server")
    print("=" * 60)
    print(f"📍 Server running on: http://127.0.0.1:5000")
    print(f"🌐 CORS enabled for: {', '.join(Config.CORS_ORIGINS)}")
    print(f"💾 Database: {'MongoDB' if Config.MONGODB_URI else 'JSON Fallback'}")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
