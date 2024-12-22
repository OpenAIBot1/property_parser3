from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, create_engine, func, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime, UTC

Base = declarative_base()

class ChannelState(Base):
    __tablename__ = 'channel_states'

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, unique=True)
    channel_name = Column(String)
    last_message_id = Column(Integer)
    last_parsed_date = Column(DateTime, default=lambda: datetime.now(UTC))

class MessageGroup(Base):
    __tablename__ = 'message_groups'

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
    channel_name = Column(String)
    group_id = Column(Integer)  # Telegram's grouped_id
    first_message_id = Column(Integer)
    combined_text = Column(Text)
    posted_date = Column(DateTime)
    parsed_date = Column(DateTime, default=lambda: datetime.now(UTC))
    
    messages = relationship("Message", back_populates="group", cascade="all, delete-orphan")
    media_items = relationship("MediaItem", back_populates="group", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer)
    text = Column(Text)
    group_id = Column(Integer, ForeignKey('message_groups.id'))
    
    group = relationship("MessageGroup", back_populates="messages")

class MediaItem(Base):
    __tablename__ = 'media_items'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('message_groups.id', ondelete='CASCADE'))
    media_type = Column(String)  # photo, document, etc.
    file_id = Column(String)
    mime_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    # Changed to LargeBinary to store raw bytes, note that this will store binary data in the database
    file_url = Column(LargeBinary)  

    group = relationship("MessageGroup", back_populates="media_items")

# Database setup
from src.config.settings import DATABASE_URL

# Removed engine creation and moved it to engine.py
