# Telegram Channel Parser

A Python-based Telegram channel parser that saves posts to a PostgreSQL database. Built for Railway deployment.

## Features

- Automatic message grouping for multi-part posts
- Media handling (photos and documents)
- Continuous channel monitoring with configurable intervals
- Stateful parsing (remembers last parsed message for each channel)
- Graceful error handling and recovery
- Comprehensive logging
- Railway deployment ready with PostgreSQL support

## Local Development Setup

1. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

2. Get your Telegram API credentials:
   - Go to https://my.telegram.org/apps
   - Create a new application
   - Copy API_ID and API_HASH to your .env file

3. Generate a session string:
   ```bash
   python generate_session.py
   ```
   Copy the generated session string to your .env file.

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the service:
   ```bash
   python -m src.service
   ```

## Railway Deployment

1. Push your code to GitHub

2. On Railway:
   - Create a new project
   - Choose "Deploy from GitHub repo"
   - Select your repository

3. Add PostgreSQL Database:
   - Click "New"
   - Select "Database"
   - Choose "Add PostgreSQL"

4. Configure Environment Variables:
   - `TELEGRAM_API_ID`: Your Telegram API ID
   - `TELEGRAM_API_HASH`: Your Telegram API Hash
   - `SESSION_NAME`: Name for your session (optional)
   - `SESSION_STRING`: Your session string from generate_session.py
   - `CHANNEL_NAMES`: Comma-separated list of channel usernames to parse

Note: `DATABASE_URL` will be automatically set by Railway when you add PostgreSQL.

## Configuration

### Environment Variables
- `TELEGRAM_API_ID`: Your Telegram API ID
- `TELEGRAM_API_HASH`: Your Telegram API Hash
- `SESSION_NAME`: Name for your session (optional)
- `SESSION_STRING`: Session string for Telegram authentication
- `CHANNEL_NAMES`: Comma-separated list of channel usernames or links to parse
- `DATABASE_URL`: PostgreSQL connection URL (automatically set by Railway)

## Database Schema

The parser uses PostgreSQL for production and SQLite for development.

### Tables

#### ChannelState
Tracks the parsing state for each channel:
- `channel_id`: Unique identifier for the channel (BigInteger)
- `channel_name`: Username or title of the channel
- `last_message_id`: ID of the last parsed message
- `last_parsed_date`: Timestamp of the last successful parse

#### MessageGroup
Groups related messages together:
- `channel_id`: Channel identifier (BigInteger)
- `channel_name`: Channel name
- `group_id`: Group identifier from Telegram (BigInteger)
- `first_message_id`: ID of the first message in the group
- `combined_text`: Combined text of all messages in the group
- `posted_date`: When the message was posted
- `parsed_date`: When the message was parsed
- `message_link`: Link to the first message in the group

#### Message
Individual messages within a group:
- `message_id`: Telegram message identifier
- `text`: Message content
- `group_id`: Reference to the message group (BigInteger)

#### MediaItem
Media files attached to messages:
- `group_id`: Reference to the message group (BigInteger)
- `media_type`: Type of media (photo, document)
- `file_id`: Telegram file identifier
- `file_url`: Binary data of the media file
- `mime_type`: MIME type of the file
- `file_size`: Size of the file in bytes

## Monitoring and Logs

- Railway provides built-in logging and monitoring
- Application logs can be viewed in the Railway dashboard
- The parser logs:
  - Channel connections
  - Message processing status
  - Media downloads
  - Errors and retries

## Error Handling

The service includes robust error handling:
- Automatic retry on network errors
- 5-minute interval between parsing cycles
- 1-minute retry delay on errors
- Graceful handling of API rate limits
- Database transaction management for data integrity
