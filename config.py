# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'default_not_so_secret_key')
    APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'default_not_so_secret_key')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    ZEPTO_KEY = os.environ.get('ZEPTO_KEY')
    ZEPTO_OTP_ID = os.environ.get('ZEPTO_OTP_ID')
    ZEPTO_WELCOME_ID = os.environ.get('ZEPTO_WELCOME_ID')
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    TOMORROW_API_KEY = os.environ.get('TOMORROW_API_KEY')
    SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
    SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

