#!/usr/bin/env python3
from src.database.engine import get_db, init_db
from src.database.models import Base, MessageGroup, Message, MediaItem, ChannelState

def cleanup_database():
    db = next(get_db())
    
    # Drop all tables
    Base.metadata.drop_all(bind=db.get_bind())
    print("All tables dropped")
    
    # Recreate tables
    Base.metadata.create_all(bind=db.get_bind())
    print("Database tables recreated")

if __name__ == "__main__":
    cleanup_database()
