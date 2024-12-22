from datetime import datetime, timezone as tz
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import relationship
from src.database.engine import Base

class ChannelState(Base):
    __tablename__ = 'channel_states'

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, unique=True)
    channel_name = Column(String)
    last_message_id = Column(Integer)
    last_parsed_date = Column(DateTime)

class MessageGroup(Base):
    __tablename__ = 'message_groups'

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
    channel_name = Column(String)
    group_id = Column(BigInteger)
    first_message_id = Column(Integer)
    combined_text = Column(Text)
    posted_date = Column(DateTime)
    parsed_date = Column(DateTime, default=lambda: datetime.now(tz.utc))
    message_link = Column(String)  # Link to the first message in the group
    
    messages = relationship("Message", back_populates="group", cascade="all, delete-orphan")
    media_items = relationship("MediaItem", back_populates="group", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer)
    text = Column(Text)
    group_id = Column(BigInteger, ForeignKey('message_groups.id'))
    
    group = relationship("MessageGroup", back_populates="messages")

class MediaItem(Base):
    __tablename__ = 'media_items'

    id = Column(Integer, primary_key=True)
    group_id = Column(BigInteger, ForeignKey('message_groups.id'))
    media_type = Column(String)  # photo, video, document, etc.
    file_id = Column(String)
    mime_type = Column(String)
    file_size = Column(Integer)
    file_url = Column(LargeBinary)  # Store raw bytes
    
    group = relationship("MessageGroup", back_populates="media_items")
