import asyncio
import os
from datetime import datetime, timezone as tz
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeImageSize, DocumentAttributeVideo, DocumentAttributeAudio, DocumentAttributeSticker, DocumentAttributeAnimated
from telethon.sessions import StringSession
from src.config.settings import API_ID, API_HASH, SESSION_NAME, CHANNEL_NAMES
from src.database.models import MessageGroup, Message, MediaItem, ChannelState
from src.database.engine import get_db
from src.telegram.session_manager import SessionManager

class TelegramParser:
    def __init__(self):
        self._running = False
        self.session_manager = SessionManager()
        self.client = None
        
    async def start(self):
        """Start the parser."""
        self.client = await self.session_manager.get_client()
        self._running = True
        
    async def stop(self):
        """Stop the parser."""
        self._running = False
        await self.session_manager.stop_client()

    async def _download_media(self, message, media):
        """Download media and return the file bytes."""
        try:
            file = await message.client.download_media(media, file=bytes, thumb=-1)
            if file:
                return file
        except Exception as e:
            print(f"Error downloading media: {str(e)}")
        return None

    async def _process_media(self, message, db_group):
        """Process all media from a message and save to database."""
        if not message.media:
            return False
            
        has_media = False
        
        try:
            # Handle photos
            if isinstance(message.media, MessageMediaPhoto):
                file_data = await self._download_media(message, message.media)
                if file_data:
                    photo = message.media.photo
                    media_item = MediaItem(
                        group_id=db_group.id,
                        media_type='photo',
                        file_id=str(photo.id),
                        file_size=max(size.size for size in photo.sizes if hasattr(size, 'size')),
                        mime_type='image/jpeg',
                        file_url=file_data
                    )
                    db_group.media_items.append(media_item)
                    has_media = True
            
            # Handle documents
            elif isinstance(message.media, MessageMediaDocument):
                file_data = await self._download_media(message, message.media)
                if file_data:
                    document = message.media.document
                    media_type = 'document'
                    
                    # Determine media type from attributes
                    for attr in document.attributes:
                        if isinstance(attr, DocumentAttributeVideo):
                            media_type = 'video'
                            break
                        elif isinstance(attr, DocumentAttributeAudio):
                            media_type = 'audio'
                            break
                        elif isinstance(attr, DocumentAttributeSticker):
                            media_type = 'sticker'
                            break
                        elif isinstance(attr, DocumentAttributeAnimated):
                            media_type = 'animation'
                            break
                        elif isinstance(attr, DocumentAttributeImageSize):
                            media_type = 'photo'
                            break
                    
                    media_item = MediaItem(
                        group_id=db_group.id,
                        media_type=media_type,
                        file_id=str(document.id),
                        file_size=document.size,
                        mime_type=getattr(document, 'mime_type', None),
                        file_url=file_data
                    )
                    db_group.media_items.append(media_item)
                    has_media = True
                    
        except Exception as e:
            print(f"Error processing media: {str(e)}")
            
        return has_media

    async def _get_message_group(self, channel, message):
        """Get all messages in the same group as the given message."""
        if not message or not message.grouped_id:
            return [message] if message else []
            
        try:
            # Get messages in a range around this message
            messages = []
            
            # Get messages before
            before = await self.client.get_messages(
                channel,
                limit=5,
                max_id=message.id
            )
            if before:
                messages.extend(before)
                
            # Get messages after
            after = await self.client.get_messages(
                channel,
                limit=5,
                min_id=message.id-1
            )
            if after:
                messages.extend(after)
                
            # Add the current message if not in the lists
            if message.id not in {msg.id for msg in messages if msg}:
                messages.append(message)
                
            if not messages:
                return [message]
                
            # Filter messages from the same group
            group_messages = [msg for msg in messages if msg and msg.grouped_id == message.grouped_id]
            
            # Sort by ID and remove duplicates
            unique_messages = []
            seen_ids = set()
            for msg in sorted(group_messages, key=lambda x: x.id):
                if msg.id not in seen_ids:
                    unique_messages.append(msg)
                    seen_ids.add(msg.id)
                    
            return unique_messages if unique_messages else [message]
            
        except Exception as e:
            print(f"Error getting message group: {str(e)}")
            return [message] if message else []

    async def _process_message_group(self, channel, message, db):
        """Process a message group and save to database."""
        if not message:
            return None
            
        try:
            # Get all messages in the group
            messages = await self._get_message_group(channel, message)
            if not messages:
                print(f"No messages found in group for message {message.id}")
                return None
                
            # Get the first and last message IDs
            first_id = min(msg.id for msg in messages)
            last_id = max(msg.id for msg in messages)
            
            print(f"Processing message group: {len(messages)} messages, IDs {first_id}-{last_id}")
                
            # Create message group
            db_group = MessageGroup(
                channel_id=channel.id,
                channel_name=channel.username or channel.title,
                group_id=message.grouped_id or message.id,
                first_message_id=first_id,
                combined_text='\n'.join(msg.text for msg in messages if msg and msg.text),
                posted_date=message.date,
                parsed_date=datetime.now(tz.utc)
            )
            db.add(db_group)
            db.flush()
            
            # Process each message in the group
            has_media = False
            media_count = 0
            for msg in messages:
                if not msg:
                    continue
                    
                # Save message
                db_message = Message(
                    message_id=msg.id,
                    text=msg.text,
                    group_id=db_group.id
                )
                db_group.messages.append(db_message)
                
                # Process media if present
                if await self._process_media(msg, db_group):
                    has_media = True
                    media_count += 1
            
            # Only commit if the group has media
            if has_media:
                db.commit()
                print(f"Saved message group {db_group.group_id} ({len(messages)} messages, {media_count} media items)")
                return last_id
            else:
                db.rollback()
                print(f"Skipped message group {db_group.group_id} (no media)")
                return None
                
        except Exception as e:
            db.rollback()
            print(f"Error processing message group: {str(e)}")
            return None

    async def parse_channels(self):
        """Parse all channels for new messages."""
        if not self.client or not self.client.is_connected():
            self.client = await self.session_manager.get_client()
            
        db = next(get_db())
        
        while self._running:
            for channel_name in CHANNEL_NAMES:
                if not channel_name:
                    continue
                    
                try:
                    # Get channel
                    channel = await self.client.get_entity(channel_name)
                    print(f"\nChecking channel: {channel.title}")
                    
                    # Get or create channel state
                    channel_state = db.query(ChannelState).filter(
                        ChannelState.channel_id == channel.id
                    ).first()
                    
                    if not channel_state:
                        print("New channel, getting latest message")
                        # Get latest message
                        latest_messages = await self.client.get_messages(channel, limit=1)
                        if not latest_messages:
                            print("No messages in channel")
                            continue
                            
                        latest_message = latest_messages[0]
                        if not latest_message:
                            print("No messages in channel")
                            continue
                            
                        # Process the message group
                        last_id = await self._process_message_group(channel, latest_message, db)
                        
                        # Create channel state
                        channel_state = ChannelState(
                            channel_id=channel.id,
                            channel_name=channel.username or channel.title,
                            last_message_id=last_id if last_id is not None else latest_message.id,
                            last_parsed_date=datetime.now(tz.utc)
                        )
                        db.add(channel_state)
                        db.commit()
                        print(f"Created channel state with last_message_id = {channel_state.last_message_id}")
                        
                    else:
                        print(f"Checking for new messages after ID {channel_state.last_message_id}")
                        # Get new messages
                        new_messages = await self.client.get_messages(
                            channel,
                            min_id=channel_state.last_message_id
                        )
                        
                        if not new_messages:
                            print("No new messages")
                            continue
                            
                        # Process each message group
                        highest_id = channel_state.last_message_id
                        for message in reversed(new_messages):  # Process in chronological order
                            if not message:
                                continue
                            last_id = await self._process_message_group(channel, message, db)
                            if last_id:
                                highest_id = max(highest_id, last_id)
                        
                        # Update channel state
                        if highest_id > channel_state.last_message_id:
                            channel_state.last_message_id = highest_id
                            channel_state.last_parsed_date = datetime.now(tz.utc)
                            db.commit()
                            print(f"Updated channel state: last_message_id = {highest_id}")
                    
                except Exception as e:
                    print(f"Error parsing channel {channel_name}: {str(e)}")
                    continue
                    
                await asyncio.sleep(1)  # Avoid hitting rate limits
            
            # Wait before checking for new messages
            await asyncio.sleep(60)  # Check every minute

async def main():
    parser = TelegramParser()
    await parser.start()
    try:
        await parser.parse_channels()
    except KeyboardInterrupt:
        await parser.stop()
