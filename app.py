"""
Pattern Tracking System - Flask Backend
Main application entry point
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
from config import DevelopmentConfig, ProductionConfig
from models import Database
from ml_engine import MLEngine
from advanced_ml import AdvancedMLEngine
from routes import student_bp, admin_bp


def create_app():
    """
    Application factory pattern
    Creates and configures the Flask application
    """
    # Switch config based on environment
    env = os.environ.get('FLASK_ENV', 'development')
    config_class = ProductionConfig if env == 'production' else DevelopmentConfig

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app,
         resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}},
         supports_credentials=True)

    # Create data directory if it doesn't exist
    data_dir = os.path.dirname(app.config['DATABASE_PATH'])
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Initialize database
    db = Database(app.config['DATABASE_PATH'])
    app.config['DATABASE'] = db

    # Initialize ML engine
    ml_engine = MLEngine(threshold=app.config['ANOMALY_THRESHOLD'])
    app.config['ML_ENGINE'] = ml_engine

    # Initialize Advanced ML engine
    advanced_ml = AdvancedMLEngine(contamination=0.1)
    app.config['ADVANCED_ML_ENGINE'] = advanced_ml
    print("✅ Advanced ML Engine initialized (Isolation Forest, K-Means, Random Forest)")

    # Register blueprints
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Pattern Tracking System API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'student': {
                    'POST /api/student/submit-report': 'Submit symptom report',
                    'GET /api/student/health': 'Health check'
                },
                'admin': {
                    'POST /api/admin/login': 'Admin login',
                    'POST /api/admin/logout': 'Admin logout',
                    'GET /api/admin/analytics': 'Get comprehensive analytics',
                    'GET /api/admin/reports': 'Get all reports',
                    'GET /api/admin/stats': 'Get quick statistics',
                    'GET /api/admin/health': 'Health check'
                }
            }
        }), 200

    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'ml_engine': 'initialized'
        }), 200

    # Seed database endpoint (development only)
    @app.route('/api/seed-database', methods=['POST'])
    def seed_database():
        """Seed database with sample data - DEVELOPMENT ONLY"""
        if not app.config['DEBUG']:
            return jsonify({
                'success': False,
                'error': 'This endpoint is only available in debug mode'
            }), 403

        try:
            db = app.config['DATABASE']
            db.seed_sample_data(num_records=30)
            return jsonify({
                'success': True,
                'message': 'Database seeded with 30 sample reports'
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

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

    return app


if __name__ == '__main__':
    app = create_app()

    print("\n" + "="*60)
    print("🚀 Pattern Tracking System Backend")
    print("="*60)
    print(f"📊 Database: {app.config['DATABASE_PATH']}")
    print(f"🔧 Debug Mode: {app.config['DEBUG']}")
    print(f"🌐 CORS Enabled for: {', '.join(app.config['CORS_ORIGINS'])}")
    print(f"🧠 ML Engine: Initialized (threshold={app.config['ANOMALY_THRESHOLD']})")
    print("="*60)
    print("\n📍 API Endpoints:")
    print("   Student: http://localhost:5000/api/student/*")
    print("   Admin:   http://localhost:5000/api/admin/*")
    print("\n💡 Tip: Visit http://localhost:5000/ for API documentation")
    print("="*60 + "\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
    # Add this at module level, outside create_app()
app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )