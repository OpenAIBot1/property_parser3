from telethon import TelegramClient
from telethon.sessions import StringSession
import os
from src.config.settings import API_ID, API_HASH, SESSION_NAME

class SessionManager:
    def __init__(self):
        self.client = None
        self.session_file = os.path.join('sessions', 'session_string.txt')

    async def get_client(self):
        """Get or create a Telegram client."""
        if self.client:
            return self.client

        # Load or create session string
        if os.path.exists(self.session_file):
            print("Loading existing session...")
            with open(self.session_file, 'r') as f:
                session_string = f.read().strip()
            session = StringSession(session_string)
        else:
            print("Creating new session...")
            session = StringSession()

        # Create client
        self.client = TelegramClient(session, API_ID, API_HASH)
        
        # Connect and save session
        await self.client.connect()
        if not await self.client.is_user_authorized():
            print("Please enter your phone number:")
            phone = input()
            await self.client.send_code_request(phone)
            print("Please enter the code you received:")
            code = input()
            await self.client.sign_in(phone, code)
            
            # Save session string
            session_string = self.client.session.save()
            os.makedirs('sessions', exist_ok=True)
            with open(self.session_file, 'w') as f:
                f.write(session_string)
                
        print("Client ready")
        return self.client

    async def stop_client(self):
        """Disconnect the client."""
        if self.client:
            await self.client.disconnect()
            self.client = None
