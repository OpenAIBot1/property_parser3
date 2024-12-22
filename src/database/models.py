from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
    channel_name = Column(String)
    message_id = Column(Integer)
    text = Column(Text)
    posted_date = Column(DateTime)
    parsed_date = Column(DateTime)

# Create database and tables
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
