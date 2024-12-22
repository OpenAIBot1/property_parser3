import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.models import Base
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

@pytest.fixture
def engine():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def mock_telegram_message():
    class MockPhotoSize:
        def __init__(self, size):
            self.size = size

    class MockPhoto:
        def __init__(self):
            self.id = 12345
            self.sizes = [MockPhotoSize(100), MockPhotoSize(200)]

    class MockDocument:
        def __init__(self):
            self.id = 12345
            self.size = 1000
            self.mime_type = 'image/jpeg'
            self.attributes = []

    class MockMediaPhoto(MessageMediaPhoto):
        def __init__(self):
            self.photo = MockPhoto()
            self.ttl_seconds = None

    class MockMediaDocument(MessageMediaDocument):
        def __init__(self):
            self.document = MockDocument()
            self.ttl_seconds = None

    class MockMessage:
        def __init__(self, id=1, text="Test message", grouped_id=None, media_type=None):
            self.id = id
            self.text = text
            self.grouped_id = grouped_id
            self.date = datetime.now(timezone.utc)
            
            if media_type == 'photo':
                self.media = MockMediaPhoto()
            elif media_type == 'document':
                self.media = MockMediaDocument()
            else:
                self.media = None

    return MockMessage
