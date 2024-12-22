#!/usr/bin/env python3
from src.database.engine import init_db
from src.config.settings import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Migrate database to use BigInteger columns."""
    logger.info(f"Starting database migration using {DATABASE_URL}")
    
    try:
        # This will drop all tables and recreate them with BigInteger columns
        init_db(drop_all=True)
        logger.info("Migration completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_database()
