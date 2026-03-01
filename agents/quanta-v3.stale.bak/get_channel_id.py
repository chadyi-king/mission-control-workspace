from telethon.sync import TelegramClient
from runtime_secrets import TELEGRAM_API_ID, TELEGRAM_API_HASH

client = TelegramClient('quanta_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)

client.start()

for d in client.iter_dialogs():
    print(d.name, d.id)
