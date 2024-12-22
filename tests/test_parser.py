import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path
import asyncio
from datetime import datetime, timezone

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.parser.telegram_parser import TelegramParser
from src.database.models import MessageGroup, Message, MediaItem
from src.config import settings

@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.is_connected.return_value = True
    return client

@pytest.mark.asyncio
async def test_process_media_photo(db_session, mock_telegram_message, mock_client):
    parser = TelegramParser(client=mock_client)
    message = mock_telegram_message(id=1, media_type='photo')
    group = MessageGroup(
        channel_id=123,
        channel_name="test_channel",
        group_id=456,
        first_message_id=1,
        combined_text="Test message",
        posted_date=datetime.now(timezone.utc)
    )
    db_session.add(group)
    db_session.flush()

    await parser._process_media(message, group)
    db_session.commit()

    media = db_session.query(MediaItem).first()
    assert media is not None
    assert media.media_type == 'photo'
    assert media.file_size == 200  # Max size from mock

@pytest.mark.asyncio
async def test_process_media_document(db_session, mock_telegram_message, mock_client):
    parser = TelegramParser(client=mock_client)
    message = mock_telegram_message(id=1, media_type='document')
    group = MessageGroup(
        channel_id=123,
        channel_name="test_channel",
        group_id=456,
        first_message_id=1,
        combined_text="Test message",
        posted_date=datetime.now(timezone.utc)
    )
    db_session.add(group)
    db_session.flush()

    await parser._process_media(message, group)
    db_session.commit()

    media = db_session.query(MediaItem).first()
    assert media is not None
    assert media.media_type == 'document'
    assert media.file_size == 1000
    assert media.mime_type == 'image/jpeg'

@pytest.mark.asyncio
async def test_message_grouping(db_session, mock_telegram_message, mock_client):
    # Mock settings to use only our test channel
    settings.CHANNEL_NAMES = ['test_channel']
    
    parser = TelegramParser(client=mock_client)
    
    # Mock channel entity
    channel = Mock()
    channel.id = 123
    channel.username = "test_channel"
    channel.title = "Test Channel"

    # Create a group of messages with a fixed group_id
    messages = [
        mock_telegram_message(id=1, text="Part 1", grouped_id=100),
        mock_telegram_message(id=2, text="Part 2", grouped_id=100),
        mock_telegram_message(id=3, text="Part 3", grouped_id=100)
    ]

    # Reverse the messages to simulate Telegram's newest-first order
    messages.reverse()

    mock_client.get_entity.return_value = channel
    # Make iter_messages return an async iterator
    async def async_iter_messages(*args, **kwargs):
        for msg in messages:
            yield msg
    mock_client.iter_messages = async_iter_messages

    # Patch get_db to use our test session
    with patch('src.parser.telegram_parser.get_db', return_value=iter([db_session])):
        await parser.parse_channels()

    # Verify the results
    group = db_session.query(MessageGroup).first()
    assert group is not None
    assert group.channel_id == 123
    assert group.group_id == 100
    assert group.first_message_id == 1
    assert group.combined_text == "Part 1\nPart 2\nPart 3"
    
    # Check that all messages were saved
    messages = db_session.query(Message).order_by(Message.message_id).all()
    assert len(messages) == 3
    assert [msg.message_id for msg in messages] == [1, 2, 3]
    assert [msg.text for msg in messages] == ["Part 1", "Part 2", "Part 3"]
