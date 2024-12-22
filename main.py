import asyncio
from src.parser.telegram_parser import TelegramParser

async def main():
    parser = TelegramParser()
    await parser.start()
    await parser.parse_channels()
    await parser.client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
