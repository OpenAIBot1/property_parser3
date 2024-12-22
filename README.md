# Telegram Channel Parser

A Python-based Telegram channel parser that saves posts to a database. Built for Railway deployment.

## Features

- Automatic message grouping for multi-part posts
- Media handling (photos and documents)
- Continuous channel monitoring with configurable intervals
- Stateful parsing (remembers last parsed message for each channel)
- Graceful error handling and recovery
- Comprehensive logging

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

4. Run the service:
   ```bash
   ./run_service.sh
   ```

## Configuration

### Environment Variables
- `API_ID`: Your Telegram API ID
- `API_HASH`: Your Telegram API Hash
- `SESSION_NAME`: Name for your session file
- `CHANNEL_NAMES`: Comma-separated list of channel usernames or links to parse
- `DATABASE_URL`: Database connection URL (defaults to SQLite)

### Parser Settings
- `parse_interval`: Time between parsing cycles in seconds (default: 300)
- Logging configuration in `service.py`

## Database Schema

The parser uses SQLite by default, storing data in `posts.db`. For Railway deployment, you can change the `DATABASE_URL` in the environment variables.

### Tables

#### ChannelState
Tracks the parsing state for each channel:
- `channel_id`: Unique identifier for the channel
- `channel_name`: Username or title of the channel
- `last_message_id`: ID of the last parsed message
- `last_parsed_date`: Timestamp of the last successful parse

#### MessageGroup
Groups related messages together:
- `channel_id`: Channel identifier
- `channel_name`: Channel name
- `group_id`: Group identifier from Telegram
- `first_message_id`: ID of the first message in the group
- `combined_text`: Combined text of all messages in the group
- `posted_date`: When the message was posted
- `parsed_date`: When the message was parsed

#### Message
Individual messages within a group:
- `message_id`: Telegram message identifier
- `text`: Message content
- `group_id`: Reference to the message group

#### MediaItem
Media files attached to messages:
- `group_id`: Reference to the message group
- `media_type`: Type of media (photo, document)
- `file_id`: Telegram file identifier
- `file_url`: URL to the media file (if available)
- `mime_type`: MIME type of the file
- `file_size`: Size of the file in bytes

## Running as a Service

The parser can be run as a continuous service using the provided `run_service.sh` script. The service:
- Initializes the database if needed
- Handles graceful shutdown on SIGTERM/SIGINT
- Provides comprehensive logging to both console and file
- Automatically recovers from errors and network issues

To stop the service, press Ctrl+C or send a SIGTERM signal.

## Logs

Logs are written to both:
- Console (stdout)
- `telegram_parser.log` file

Log entries include timestamps, log levels, and detailed error information when available.
