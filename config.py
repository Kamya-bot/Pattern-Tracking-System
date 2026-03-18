"""
Configuration file for Pattern Tracking System Backend
"""
import os
from datetime import timedelta


class Config:
    """Base configuration - values should come from environment variables in production"""

    SECRET_KEY = os.environ.get('SECRET_KEY') or None
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'health_reports.db')

    CORS_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost:5500',
        'http://127.0.0.1:5500',
        'https://kamya-bot.github.io',
        'https://pattern-tracking-system.netlify.app',
    ]

    # Cross-origin cookie settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None'   # required for cross-origin requests
    SESSION_COOKIE_SECURE = True       # required when SameSite=None
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # ML settings
    ANOMALY_THRESHOLD = 2.0
    MIN_DATA_POINTS = 10


class DevelopmentConfig(Config):
    """Local development — relaxed settings"""
    DEBUG = True
    SECRET_KEY = 'dev-only-secret-key-do-not-use-in-production'
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'


class ProductionConfig(Config):
    """Production — strict settings"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'