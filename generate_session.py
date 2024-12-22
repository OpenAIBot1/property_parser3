from telethon import TelegramClient
from telethon.sessions import StringSession
from src.config.settings import API_ID, API_HASH
import asyncio
from telethon.errors import SessionPasswordNeededError
import base64

async def main():
    """Generate a new session string."""
    print("Creating new session...")
    
    # Create with no session
    client = TelegramClient(
        StringSession(),
        api_id=API_ID,
        api_hash=API_HASH,
        system_version="4.16.30-vxCUSTOM"
    )
    
    try:
        print("Connecting to Telegram...")
        await client.connect()
        
        if not await client.is_user_authorized():
            print("\nPlease enter your phone number (with country code, e.g., +1234567890):")
            phone = input().strip()
            
            # Request code
            await client.send_code_request(phone)
            print("\nCode sent! Please enter the code you received:")
            code = input().strip()
            
            try:
                # Try to sign in
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                # 2FA is enabled
                print("\n2FA is enabled. Please enter your password:")
                password = input().strip()
                await client.sign_in(password=password)
        
        # Get session string and encode it
        session_string = client.session.save()
        encoded_string = base64.urlsafe_b64encode(session_string.encode()).decode()
        
        print("\nGenerated session string (use this as SESSION_STRING in .env):")
        print("-" * 80)
        print(encoded_string)
        print("-" * 80)
        
        # Save to file for backup
        with open('session_string.txt', 'w') as f:
            f.write(encoded_string)
        print("\nSession string also saved to session_string.txt")
        
        # Verify connection
        me = await client.get_me()
        print(f"\nSuccessfully connected as: {me.first_name} (ID: {me.id})")
        print("\nPlease copy the session string between the lines above and update your .env file")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise
    finally:
        print("\nDisconnecting...")
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
