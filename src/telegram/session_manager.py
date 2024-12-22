from telethon import TelegramClient
from telethon.sessions import StringSession
from src.config.settings import API_ID, API_HASH, SESSION_STRING
import base64

class SessionManager:
    """Manages Telegram session."""
    
    def __init__(self):
        """Initialize session manager."""
        self.client = None
        
    def _decode_session_string(self, encoded_string):
        """Decode the base64 session string.
        
        Args:
            encoded_string: Base64 encoded session string
            
        Returns:
            str: Decoded session string
        """
        try:
            # Remove any whitespace and decode
            cleaned = encoded_string.strip()
            decoded = base64.urlsafe_b64decode(cleaned).decode()
            return decoded
        except Exception as e:
            print(f"Error decoding session string: {str(e)}")
            raise ValueError(f"Invalid session string format: {str(e)}")
        
    async def get_client(self):
        """Get or create Telegram client using session string.
        
        Returns:
            TelegramClient: Connected Telegram client
        """
        if self.client and self.client.is_connected():
            return self.client
            
        print("\nCreating new client from session string...")
        
        try:
            # Decode the session string
            session_string = self._decode_session_string(SESSION_STRING)
            
            # Create client
            self.client = TelegramClient(
                StringSession(session_string),
                API_ID,
                API_HASH,
                system_version="4.16.30-vxCUSTOM"
            )
            
            print("Connecting to Telegram...")
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                print("Session string is invalid or expired. Please generate a new one.")
                raise ValueError("Invalid session string")
                
            me = await self.client.get_me()
            print(f"Connected successfully as {me.first_name} (ID: {me.id})")
            return self.client
            
        except Exception as e:
            print(f"Error connecting client: {str(e)}")
            if self.client:
                await self.client.disconnect()
            raise
        
    async def disconnect(self):
        """Disconnect the client if connected."""
        if self.client:
            try:
                await self.client.disconnect()
                print("Client disconnected")
            except Exception as e:
                print(f"Error disconnecting client: {str(e)}")
            finally:
                self.client = None
