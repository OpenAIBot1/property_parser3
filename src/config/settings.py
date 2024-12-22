import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_NAME = os.getenv('SESSION_NAME', 'property_parser_session')
CHANNEL_NAMES = os.getenv('CHANNEL_NAMES', '').split(',')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///posts.db')
