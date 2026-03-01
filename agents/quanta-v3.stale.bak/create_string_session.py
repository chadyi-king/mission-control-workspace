import asyncio

from config import load_settings

try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
except Exception as exc:
    raise RuntimeError("Telethon is required to create string session") from exc


async def main() -> None:
    settings = load_settings()
    client = TelegramClient(settings.telegram_session_file, settings.telegram_api_id, settings.telegram_api_hash)
    await client.start(phone=settings.telegram_phone)
    value = StringSession.save(client.session)
    print(value)
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
