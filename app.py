"""
Pattern Tracking System - Flask Backend
Main application entry point
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
import hashlib

from config import DevelopmentConfig, ProductionConfig
from models import Database
from ml_engine import MLEngine
from advanced_ml import AdvancedMLEngine
from routes import student_bp, admin_bp


def create_app():
    """Application factory pattern"""
    env = os.environ.get('FLASK_ENV', 'development')
    config_class = ProductionConfig if env == 'production' else DevelopmentConfig

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # Ensure data directory exists
    data_dir = os.path.dirname(app.config['DATABASE_PATH'])
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Initialize database
    db = Database(app.config['DATABASE_PATH'])
    app.config['DATABASE'] = db

    # Initialize ML engines
    ml_engine = MLEngine(threshold=app.config['ANOMALY_THRESHOLD'])
    app.config['ML_ENGINE'] = ml_engine

    advanced_ml = AdvancedMLEngine(contamination=0.1)
    app.config['ADVANCED_ML_ENGINE'] = advanced_ml
    print("✅ Advanced ML Engine initialized")

    # Register routes
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # ------------------ BASIC ROUTES ------------------

    @app.route('/')
    def index():
        return jsonify({
            'name': 'Pattern Tracking System API',
            'version': '1.0.0',
            'status': 'running'
        }), 200

    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'ml_engine': 'initialized'
        }), 200

    # ------------------ ADMIN RESET (FIXED) ------------------

    @app.route('/reset-admin')
    def reset_admin():
        try:
            db = app.config['DATABASE']
            conn = db.get_connection()

            new_pass = "ADMIN123"
            hashed = hashlib.sha256(new_pass.encode()).hexdigest()

            # Check if user exists
            user = conn.execute(
                "SELECT * FROM users WHERE username=?",
                ("admin@gmail.com",)
            ).fetchone()

            if user:
                conn.execute(
                    "UPDATE users SET password=? WHERE username=?",
                    (hashed, "admin@gmail.com")
                )
                message = "✅ Admin password UPDATED"
            else:
                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    ("admin@gmail.com", hashed)
                )
                message = "✅ Admin user CREATED"

            conn.commit()
            conn.close()

            return jsonify({
                "success": True,
                "message": message,
                "login": {
                    "username": "admin@gmail.com",
                    "password": "ADMIN123"
                }
            }), 200

        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    # ------------------ ERROR HANDLERS ------------------

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

    return app


# WSGI entry point
app = create_app()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Pattern Tracking System Backend")
    print("="*60)
    print(f"📊 Database: {app.config['DATABASE_PATH']}")
    print(f"🔧 Debug Mode: {app.config['DEBUG']}")
    print(f"🌐 CORS Enabled for: {', '.join(app.config['CORS_ORIGINS'])}")
    print("="*60)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )