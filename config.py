#!/usr/bin/env python3
"""
Configuration settings for Academic Integrity Checker
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///academic_integrity.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

    # Celery settings for background tasks
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # AI Model settings
    TRANSFORMERS_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model_cache')
    SPACY_MODEL = 'en_core_web_sm'

    # External API settings (add your own API keys)
    SERPAPI_KEY = os.environ.get('SERPAPI_KEY', '')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

    # Report settings
    REPORT_LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/images/logo.png')
    REPORT_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/fonts/')

    # Chrome extension settings
    CHROME_EXTENSION_ID = 'your-chrome-extension-id'

class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    SQLALCHEMY_ECHO = False

    # Use in-memory database for testing
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False

    # Use environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY environment variable must be set in production')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError('DATABASE_URL environment variable must be set in production')

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Create required directories
def create_directories():
    """Create necessary directories"""
    directories = [
        Config.UPLOAD_FOLDER,
        Config.TRANSFORMERS_CACHE,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/css'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/js'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/images'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/fonts'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ai_modules'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrome_extension'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests'),
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Create directories on import
create_directories()