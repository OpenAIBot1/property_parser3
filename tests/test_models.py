import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.models import MessageGroup, Message, MediaItem

def test_message_group_creation(db_session):
    group = MessageGroup(
        channel_id=123,
        channel_name="test_channel",
        group_id=456,
        first_message_id=1,
        combined_text="Test message",
        posted_date=datetime.utcnow()
    )
    db_session.add(group)
    db_session.commit()

    assert db_session.query(MessageGroup).count() == 1
    assert db_session.query(MessageGroup).first().channel_name == "test_channel"

def test_message_relationship(db_session):
    group = MessageGroup(
        channel_id=123,
        channel_name="test_channel",
        group_id=456,
        first_message_id=1,
        combined_text="Test message",
        posted_date=datetime.utcnow()
    )
    message = Message(
        message_id=1,
        text="Test message",
        group=group
    )
    db_session.add(group)
    db_session.commit()

    assert len(group.messages) == 1
    assert group.messages[0].text == "Test message"

def test_media_relationship(db_session):
    group = MessageGroup(
        channel_id=123,
        channel_name="test_channel",
        group_id=456,
        first_message_id=1,
        combined_text="Test message",
        posted_date=datetime.utcnow()
    )
    media = MediaItem(
        media_type="photo",
        file_id="123456",
        file_size=1000,
        group=group
    )
    db_session.add(group)
    db_session.commit()

    assert len(group.media_items) == 1
    assert group.media_items[0].media_type == "photo"

def test_cascade_delete(db_session):
    group = MessageGroup(
        channel_id=123,
        channel_name="test_channel",
        group_id=456,
        first_message_id=1,
        combined_text="Test message",
        posted_date=datetime.utcnow()
    )
    message = Message(message_id=1, text="Test", group=group)
    media = MediaItem(media_type="photo", file_id="123", group=group)
    
    db_session.add(group)
    db_session.commit()
    
    db_session.delete(group)
    db_session.commit()
    
    assert db_session.query(Message).count() == 0
    assert db_session.query(MediaItem).count() == 0
