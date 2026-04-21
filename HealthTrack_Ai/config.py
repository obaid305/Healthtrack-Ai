# config.py - Fixed: email password required, debug default False
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'healthtrack-ai-secret-key-2024-change-in-production'
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600
    
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'healthtrack_ai'
    
    # Email configuration - must be set in environment
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'ai.healthtrack@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Must be set in .env
    MAIL_DEFAULT_SENDER = f'HealthTrack AI <{MAIL_USERNAME}>'
    MAIL_DEBUG = os.environ.get('MAIL_DEBUG', 'False').lower() == 'true'
    APP_URL = os.environ.get('APP_URL') or 'http://localhost:5000'
    
    # Model paths
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'disease_prediction_model.pkl')
    SYMPTOM_NAMES_PATH = os.path.join(os.path.dirname(__file__), 'models', 'symptom_names.pkl')
    ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'models', 'disease_label_encoder.pkl')
    
    MIN_ADVANCE_BOOKING_HOURS = 1
    MAX_APPOINTMENTS_PER_DAY = 20
    CONSULTATION_DURATION_MINUTES = 30
    CANCELLATION_DEADLINE_HOURS = 24
    MAX_RESCHEDULE_COUNT = 2
    
    BCRYPT_ROUNDS = 12
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    ITEMS_PER_PAGE = 10
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}
    TIMEZONE = 'Asia/Karachi'
    RATELIMIT_ENABLED = False
    RATELIMIT_DEFAULT = "100 per day"
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/healthtrack.log'
    
    # Debug mode - default False for production
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'