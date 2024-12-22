import os
from dotenv import load_dotenv
from pathlib import Path

# Force reload environment variables
print("\nLoading environment variables...")
env_path = Path(__file__).parent.parent.parent / '.env'
print(f"Loading .env from: {env_path}")
load_dotenv(env_path, override=True)

# Debug: Print raw channel names from env
raw_channel_names = os.getenv('CHANNEL_NAMES', '')
print(f"Raw CHANNEL_NAMES from env: '{raw_channel_names}'")

# Split and debug print
split_names = raw_channel_names.split(',')
print(f"Split channel names: {split_names}")

# Channel names to parse with detailed processing
CHANNEL_NAMES = []
for name in split_names:
    stripped = name.strip()
    if stripped:
        CHANNEL_NAMES.append(stripped)
        print(f"Added channel: '{stripped}'")
    else:
        print(f"Skipped empty channel name: '{name}'")

print(f"Final processed channel names: {CHANNEL_NAMES}")

# Telegram API credentials
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')

# Session configuration
SESSION_NAME = os.getenv('SESSION_NAME', 'property_parser_session')
SESSION_STRING = os.getenv('SESSION_STRING', '').strip()
print(f"Found session string of length: {len(SESSION_STRING)}")
if not SESSION_STRING:
    raise ValueError("SESSION_STRING environment variable is required")

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///telegram_parser.db')
