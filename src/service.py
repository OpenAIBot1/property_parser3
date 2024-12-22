#!/usr/bin/env python3
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, UTC

from src.database.engine import init_db
from src.parser.telegram_parser import TelegramParser
from src.telegram.session_manager import SessionManager
from src.config import settings

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
    print("\nService starting...")
    logger.info("Service starting")
    print(f"Using channel names: {settings.CHANNEL_NAMES}")
    logger.info(f"Using channel names: {settings.CHANNEL_NAMES}")
    
    if not settings.CHANNEL_NAMES:
        print("ERROR: No channel names configured!")
        logger.error("No channel names configured")
        return
        
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized")

        session_manager = SessionManager()
        parser = TelegramParser(session_manager)
        
        try:
            await parser.start()
            logger.info("Parser started")
            
            # Run parser continuously
            while True:
                try:
                    logger.info("Starting to parse channels...")
                    await parser.parse_channels()
                    logger.info("Finished parsing channels, waiting 5 minutes before next run...")
                    await asyncio.sleep(300)  # 5 minutes interval
                except Exception as e:
                    logger.error(f"Error during channel parsing: {str(e)}", exc_info=True)
                    logger.info("Waiting 60 seconds before retry...")
                    await asyncio.sleep(60)  # Wait 1 minute before retrying
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await parser.stop()
            logger.info("Parser stopped")
                
        except Exception as e:
            logger.error(f"Error in main service: {str(e)}")
            await parser.stop()
            raise
            
    except Exception as e:
        logger.error(f"Service error: {str(e)}")
        raise

if __name__ == "__main__":
    setup_environment()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
