from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.settings import DATABASE_URL
import os

# Create the engine
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(drop_all=False):
    """Initialize database.
    
    Args:
        drop_all (bool): If True, drop all tables before creating them
    """
    # Import all models to ensure they are registered
    from src.database.models import ChannelState, MessageGroup, Message, MediaItem
    
    if drop_all:
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
