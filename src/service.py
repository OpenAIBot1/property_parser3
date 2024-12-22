#!/usr/bin/env python3
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, UTC

from src.database.engine import init_db
from src.parser.telegram_parser import TelegramParser
from src.telegram.session_manager import SessionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('telegram_parser.log')
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup the environment for the service."""
    # Create necessary directories
    Path('sessions').mkdir(exist_ok=True)
    Path('logs').mkdir(exist_ok=True)

async def main():
    """Main service function."""
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized")

        # Create and start parser
        parser = TelegramParser()
        await parser.start()
        
        try:
            # Run parser continuously
            while True:
                await parser.parse_channels()
                await asyncio.sleep(300)  # 5 minutes interval
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await parser.stop()
            
    except Exception as e:
        logger.error(f"Service error: {str(e)}")
        raise

if __name__ == "__main__":
    setup_environment()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
