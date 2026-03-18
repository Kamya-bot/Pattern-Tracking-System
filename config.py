"""
Configuration file for Pattern Tracking System Backend
"""
import os
from datetime import timedelta


class Config:
    """Base configuration - values should come from environment variables in production"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or None  # MUST be set in production
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

    # Database settings
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'health_reports.db')

    # CORS settings — add your production frontend URL here before going live
    CORS_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost:5500',  # Live Server
        'http://127.0.0.1:5500',
    ]

    # Session settings
    SESSION_COOKIE_HTTPONLY = True   # prevent JS access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax' # CSRF protection
    SESSION_COOKIE_SECURE = os.environ.get('HTTPS', 'false').lower() == 'true'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # ML settings
    ANOMALY_THRESHOLD = 2.0  # Standard deviations for anomaly detection
    MIN_DATA_POINTS = 10     # Minimum data points for ML analysis

    @staticmethod
    def validate():
        """Call this at startup to catch missing critical config"""
        if not os.environ.get('SECRET_KEY'):
            raise RuntimeError(
                "SECRET_KEY environment variable is not set. "
                "Run: set SECRET_KEY=your-random-secret-key"
            )


class DevelopmentConfig(Config):
    """Local development — relaxed settings"""
    DEBUG = True
    SECRET_KEY = 'dev-only-secret-key-do-not-use-in-production'
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production — strict settings"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # requires HTTPS