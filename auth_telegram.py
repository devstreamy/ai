from telethon.sync import TelegramClient
import logging

logging.basicConfig(level=logging.INFO)
api_id = 26171520
api_hash = "018e37794a51b1721b4be9707cc9bb65"

with TelegramClient('session_name', api_id, api_hash) as client:
    session = client.session.save()
    json = client.get_me().to_json()

print('Session:', session)
print('JSON:', json)