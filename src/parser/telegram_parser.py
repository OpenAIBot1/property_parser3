import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from config import API_ID, API_HASH, SESSION_NAME, CHANNEL_NAMES
from models import Post, get_db

class TelegramParser:
    def __init__(self):
        self.client = TelegramClient(StringSession(), API_ID, API_HASH)

    async def start(self):
        await self.client.start()
        print("Client Created")
        # Save the session string for later use
        print("Session string:", self.client.session.save())

    async def parse_channels(self):
        db = next(get_db())
        
        for channel_name in CHANNEL_NAMES:
            if not channel_name:
                continue
                
            try:
                channel = await self.client.get_entity(channel_name)
                print(f"Parsing channel: {channel.title}")
                
                async for message in self.client.iter_messages(channel):
                    # Check if message already exists
                    existing_post = db.query(Post).filter(
                        Post.channel_id == channel.id,
                        Post.message_id == message.id
                    ).first()
                    
                    if existing_post:
                        continue
                        
                    if message.text:
                        post = Post(
                            channel_id=channel.id,
                            channel_name=channel.username or channel.title,
                            message_id=message.id,
                            text=message.text,
                            posted_date=message.date,
                            parsed_date=datetime.utcnow()
                        )
                        db.add(post)
                        print(f"Added new post from {channel.title}")
                
                await asyncio.sleep(1)  # Avoid hitting rate limits
                
            except Exception as e:
                print(f"Error parsing channel {channel_name}: {str(e)}")
                continue
        
        db.commit()

async def main():
    parser = TelegramParser()
    await parser.start()
    await parser.parse_channels()
    await parser.client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
