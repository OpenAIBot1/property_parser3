from datetime import datetime, timezone as tz
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, LargeBinary, Text, Float, Boolean
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
    cleaned_listing = relationship("CleanedListing", backref="group")

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

class CleanedListing(Base):
    __tablename__ = 'cleaned_listings'

    id = Column(Integer, primary_key=True)
    group_id = Column(BigInteger, ForeignKey('message_groups.id'))
    original_text = Column(Text)
    processed_date = Column(DateTime, default=lambda: datetime.now(tz.utc))
    
    # Basic Details
    layout = Column(String)  # Stored as enum string value
    area_sqm = Column(Float)
    floor = Column(Integer)
    total_floors = Column(Integer)
    bedrooms = Column(Integer)
    has_balcony = Column(Boolean)

    # Location
    address = Column(Text)
    district = Column(String)
    nearby_landmarks = Column(Text)  # JSON array of strings

    # Financial
    monthly_rent_usd = Column(Float)
    summer_rent_usd = Column(Float)
    requires_first_last = Column(Boolean)
    deposit_amount_usd = Column(Float)
    commission = Column(Float)

    # Amenities
    heating_type = Column(String)  # Stored as enum string value
    has_oven = Column(Boolean)
    has_microwave = Column(Boolean)
    has_ac = Column(Boolean)
    has_internet = Column(Boolean)
    has_tv = Column(Boolean)
    has_parking = Column(Boolean)
    has_bathtub = Column(Boolean)
    is_furnished = Column(Boolean)

    # Contact
    phone_numbers = Column(Text)  # JSON array of strings
    whatsapp = Column(String)
    telegram = Column(String)
    contact_name = Column(String)

    # Terms
    min_lease_months = Column(Integer)
    max_lease_months = Column(Integer)
    pet_policy = Column(String)  # Stored as enum string value
    has_contract = Column(Boolean)

    # Media
    image_urls = Column(Text)  # JSON array of image URLs
    
    group = relationship("MessageGroup", backref="cleaned_listing")
