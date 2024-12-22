# Telegram Channel Parser

A Python-based Telegram channel parser that saves posts to a database. Built for Railway deployment.

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

2. Get your Telegram API credentials:
   - Go to https://my.telegram.org/apps
   - Create a new application
   - Copy API_ID and API_HASH to your .env file

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the parser:
   ```bash
   python parser.py
   ```

## Configuration

- `API_ID`: Your Telegram API ID
- `API_HASH`: Your Telegram API Hash
- `SESSION_NAME`: Name for your session file
- `CHANNEL_NAMES`: Comma-separated list of channel usernames or links to parse

## Database

The parser uses SQLite by default, storing data in `posts.db`. For Railway deployment, you can change the `DATABASE_URL` in the environment variables.
