"""
Routes package initialization
"""
from .student import student_bp
from .admin import admin_bp

__all__ = ['student_bp', 'admin_bp']
