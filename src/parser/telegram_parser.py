import asyncio
import os
from datetime import datetime, timezone as tz, timedelta
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeImageSize, DocumentAttributeVideo, DocumentAttributeAudio, DocumentAttributeSticker, DocumentAttributeAnimated
from telethon.sessions import StringSession
from src.config.settings import API_ID, API_HASH, SESSION_NAME, CHANNEL_NAMES
from src.database.models import MessageGroup, Message, MediaItem, ChannelState
from src.database.engine import get_db
from src.telegram.session_manager import SessionManager
import logging

class TelegramParser:
    """Parser for Telegram channels."""
    
    def __init__(self, session_manager):
        """Initialize parser.
        
        Args:
            session_manager: SessionManager instance for handling Telegram sessions
        """
        self.session_manager = session_manager
        self.client = None
        self._running = False
        self.logger = logging.getLogger(__name__)
        
    async def start(self):
        """Start the parser."""
        self.logger.info("Starting parser...")
        self._running = True
        self.client = await self.session_manager.get_client()
        self.logger.info("Parser started successfully")
        
    async def stop(self):
        """Stop the parser."""
        self.logger.info("Stopping parser...")
        self._running = False
        if self.session_manager:
            await self.session_manager.disconnect()
        self.logger.info("Parser stopped")

    async def _download_media(self, message, media):
        """Download media and return the file bytes."""
        try:
            file = await message.client.download_media(media, file=bytes, thumb=-1)
            if file:
                return file
        except Exception as e:
            self.logger.error(f"Error downloading media: {str(e)}")
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
            self.logger.error(f"Error processing media: {str(e)}")
            
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
                limit=15,
                max_id=message.id
            )
            if before:
                messages.extend(before)
                
            # Get messages after
            after = await self.client.get_messages(
                channel,
                limit=15,
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
            self.logger.error(f"Error getting message group: {str(e)}")
            return [message] if message else []

    async def _process_message_group(self, channel, message, db):
        """Process a message group and save to database."""
        if not message:
            return None
            
        try:
            # Get all messages in the group
            messages = await self._get_message_group(channel, message)
            if not messages:
                self.logger.info(f"No messages found in group for message {message.id}")
                return None
                
            # Get the first and last message IDs
            first_id = min(msg.id for msg in messages)
            last_id = max(msg.id for msg in messages)
            
            self.logger.info(f"Processing message group: {len(messages)} messages, IDs {first_id}-{last_id}")
            
            # Generate message link
            if channel.username:
                message_link = f"https://t.me/{channel.username}/{first_id}"
            else:
                message_link = f"https://t.me/c/{channel.id}/{first_id}"
                
            # Create message group
            db_group = MessageGroup(
                channel_id=channel.id,
                channel_name=channel.username or channel.title,
                group_id=message.grouped_id or message.id,
                first_message_id=first_id,
                combined_text='\n'.join(msg.text for msg in messages if msg and msg.text),
                posted_date=message.date,
                parsed_date=datetime.now(tz.utc),
                message_link=message_link
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
                self.logger.info(f"Saved message group {db_group.group_id} ({len(messages)} messages, {media_count} media items)")
                self.logger.info(f"Message link: {message_link}")
                return last_id
            else:
                db.rollback()
                self.logger.info(f"Skipped message group {db_group.group_id} (no media)")
                return None
                
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error processing message group: {str(e)}")
            return None

    async def _cleanup_old_data(self, db):
        """Remove data older than 48 hours."""
        try:
            cutoff_time = datetime.now(tz.utc) - timedelta(hours=48)
            self.logger.info(f"Running cleanup for data older than {cutoff_time.isoformat()}")
            
            # Find old message groups
            old_groups = db.query(MessageGroup).filter(
                MessageGroup.posted_date < cutoff_time
            ).all()
            
            if not old_groups:
                self.logger.info("No old message groups found to clean up")
                return
                
            self.logger.info(f"Found {len(old_groups)} message groups to clean up")
            
            # Delete old groups (cascade will handle related records)
            for group in old_groups:
                self.logger.info(f"Deleting group {group.id} posted at {group.posted_date.isoformat()}")
                db.delete(group)
            
            db.commit()
            self.logger.info(f"Successfully cleaned up {len(old_groups)} old message groups")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
            db.rollback()

    async def parse_channels(self):
        """Parse all channels for new messages."""
        if not self.client or not self.client.is_connected():
            self.logger.info("Connecting client...")
            self.client = await self.session_manager.get_client()
            self.logger.info("Client connected successfully")
            
        db = next(get_db())
        
        # Run cleanup before parsing
        await self._cleanup_old_data(db)
        
        self.logger.info(f"\nStarting to parse channels: {CHANNEL_NAMES}")
        self.logger.info(f"Parser running state: {self._running}")
        
        for channel_name in CHANNEL_NAMES:
            if not channel_name:
                continue
                
            try:
                # Get channel
                self.logger.info(f"\n{'='*50}")
                self.logger.info(f"Processing channel: {channel_name}")
                try:
                    # Try with @ prefix if not present
                    if not channel_name.startswith('@'):
                        self.logger.info(f"Trying with @ prefix...")
                        try:
                            channel = await self.client.get_entity(f"@{channel_name}")
                        except:
                            self.logger.info(f"Failed with @ prefix, trying original name...")
                            channel = await self.client.get_entity(channel_name)
                    else:
                        channel = await self.client.get_entity(channel_name)
                        
                    self.logger.info(f"Successfully connected to channel: {channel.title}")
                    self.logger.info(f"Channel ID: {channel.id}")
                    self.logger.info(f"Channel username: {channel.username}")
                    
                except ValueError as e:
                    self.logger.error(f"Error accessing channel {channel_name}: {str(e)}")
                    self.logger.info("Try using the full channel URL (t.me/...) or channel ID")
                    self.logger.info("Make sure you have joined the channel")
                    continue
                except Exception as e:
                    self.logger.error(f"Unexpected error accessing channel {channel_name}: {str(e)}")
                    continue
                
                # Get or create channel state
                channel_state = db.query(ChannelState).filter(
                    ChannelState.channel_id == channel.id
                ).first()
                
                if not channel_state:
                    self.logger.info("\nNew channel detected, getting latest message")
                    # Get latest message
                    latest_messages = await self.client.get_messages(channel, limit=1)
                    if not latest_messages:
                        self.logger.info("No messages found in channel")
                        continue
                        
                    latest_message = latest_messages[0]
                    if not latest_message:
                        self.logger.info("No valid message found")
                        continue
                        
                    self.logger.info(f"Found latest message ID: {latest_message.id}")
                    
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
                    self.logger.info(f"Created channel state with last_message_id = {channel_state.last_message_id}")
                    
                else:
                    self.logger.info(f"\nExisting channel, last_message_id = {channel_state.last_message_id}")
                    # Get latest message to determine max_id
                    latest_messages = await self.client.get_messages(channel, limit=1)
                    if not latest_messages or not latest_messages[0]:
                        self.logger.info("No messages found in channel")
                        continue
                        
                    max_message_id = latest_messages[0].id
                    self.logger.info(f"Latest message ID: {max_message_id}")
                    
                    # Get new messages with both min_id and max_id
                    new_messages = await self.client.get_messages(
                        channel,
                        min_id=channel_state.last_message_id,
                        max_id=max_message_id
                    )
                    
                    if not new_messages:
                        self.logger.info("No new messages found")
                        continue
                        
                    self.logger.info(f"Found {len(new_messages)} new messages")
                    
                    # Track processed groups to avoid duplicates
                    processed_groups = set()
                    highest_id = channel_state.last_message_id
                    
                    # Process messages in chronological order
                    for message in reversed(new_messages):
                        if not message:
                            continue
                            
                        # Skip if we've already processed this group
                        group_id = message.grouped_id or message.id
                        if group_id in processed_groups:
                            self.logger.info(f"Skipping message {message.id} (group {group_id} already processed)")
                            continue
                            
                        # Get all messages in the group
                        group_messages = await self._get_message_group(channel, message)
                        if not group_messages:
                            continue
                            
                        # Find the first message in the group
                        first_message = min(group_messages, key=lambda m: m.id)
                        
                        # Process the group using the first message
                        last_id = await self._process_message_group(channel, first_message, db)
                        if last_id:
                            highest_id = max(highest_id, last_id)
                            processed_groups.add(group_id)
                    
                    # Update channel state
                    if highest_id > channel_state.last_message_id:
                        channel_state.last_message_id = highest_id
                        channel_state.last_parsed_date = datetime.now(tz.utc)
                        db.commit()
                        self.logger.info(f"Updated channel state: last_message_id = {highest_id}")
                
            except Exception as e:
                self.logger.error(f"Error parsing channel {channel_name}: {str(e)}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                continue

async def main():
    session_manager = SessionManager()
    parser = TelegramParser(session_manager)
    await parser.start()
    try:
        await parser.parse_channels()
    except KeyboardInterrupt:
        await parser.stop()
