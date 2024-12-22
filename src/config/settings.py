import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = os.getenv('SESSION_NAME', 'property_parser_session')
CHANNEL_NAMES = [name.strip() for name in os.getenv('CHANNEL_NAMES', '').split(',') if name.strip()]

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///posts.db')
