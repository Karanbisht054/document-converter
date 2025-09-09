import os
from datetime import datetime

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    UPLOAD_FOLDER = 'uploads'
    CONVERTED_FOLDER = 'converted'
    TEMP_FOLDER = 'temp'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Database configuration (optional)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///document_converter.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OCR configuration
    TESSERACT_CMD = os.environ.get('TESSERACT_CMD') or r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    OCR_LANGUAGES = 'eng+hin'  # English + Hindi
    
    # File cleanup settings
    CLEANUP_AFTER_HOURS = 24  # Clean up files after 24 hours
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}