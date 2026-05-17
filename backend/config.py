"""
SignBridge Configuration
Loads settings from environment variables
"""

import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Application configuration"""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))

    # Paths — VIDEOS_PATH can be overridden via env var for deployment flexibility
    MODELS_PATH    = Path(os.getenv('MODELS_PATH',    str(BASE_DIR / 'models')))
    VIDEOS_PATH    = Path(os.getenv('VIDEOS_PATH',    str(BASE_DIR / 'Speech to Sign  ' / 'videos1')))
    STATIC_PATH    = BASE_DIR / 'frontend' / 'static'
    TEMPLATES_PATH = BASE_DIR / 'frontend' / 'templates'

    # ML Model settings
    GESTURE_CONFIDENCE_THRESHOLD = float(os.getenv('GESTURE_CONFIDENCE_THRESHOLD', 0.6))
    PREDICTION_BUFFER_SIZE       = int(os.getenv('PREDICTION_BUFFER_SIZE', 10))

    # Camera settings (local dev only — not used in cloud deployment)
    CAMERA_INDEX             = int(os.getenv('CAMERA_INDEX', 0))
    MAX_NUM_HANDS            = int(os.getenv('MAX_NUM_HANDS', 2))
    MIN_DETECTION_CONFIDENCE = float(os.getenv('MIN_DETECTION_CONFIDENCE', 0.7))
    MIN_TRACKING_CONFIDENCE  = float(os.getenv('MIN_TRACKING_CONFIDENCE', 0.7))

    # Deployment mode: 'local' uses server-side camera, 'cloud' uses browser WebRTC
    DEPLOYMENT_MODE = os.getenv('DEPLOYMENT_MODE', 'local')

    # Speech settings
    SPEECH_LANGUAGE = os.getenv('SPEECH_LANGUAGE', 'en-IN')
    TTS_ENABLED     = os.getenv('TTS_ENABLED', 'False').lower() == 'true'

    # Performance
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', 50))

    @classmethod
    def is_cloud(cls):
        return cls.DEPLOYMENT_MODE == 'cloud'

    @classmethod
    def validate(cls):
        if not cls.MODELS_PATH.exists():
            raise FileNotFoundError(f"Models directory not found: {cls.MODELS_PATH}")
        if not cls.VIDEOS_PATH.exists():
            raise FileNotFoundError(f"Videos directory not found: {cls.VIDEOS_PATH}")
        return True

    @classmethod
    def print_config(cls):
        print("=" * 60)
        print("🌉 SignBridge Configuration")
        print("=" * 60)
        print(f"📁 Base Directory  : {BASE_DIR}")
        print(f"📁 Models Path     : {cls.MODELS_PATH}")
        print(f"📁 Videos Path     : {cls.VIDEOS_PATH}")
        print(f"🎯 Confidence      : {cls.GESTURE_CONFIDENCE_THRESHOLD}")
        print(f"🚀 Deployment Mode : {cls.DEPLOYMENT_MODE}")
        print(f"🌐 Server          : {cls.HOST}:{cls.PORT}")
        print("=" * 60)


# Singleton
config = Config()
