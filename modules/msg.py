from pyrogram import Client
from pyrogram.enums import ChatType
import threading, os, time
from utils.logs import logError, stopColor, logSystem
from modules.other import show_current_datetime, saveTextfile

api_id = 26171520
api_hash = "018e37794a51b1721b4be9707cc9bb65"

os.makedirs("sessions", exist_ok=True)
app = Client("modules/sessions/telegram.session", api_id=api_id, api_hash=api_hash)

def telegram_contacts():
    try:
        while True:
            print(logSystem+"список контактов телеграм обновился"+stopColor+show_current_datetime())
            file_path = "modules/messengers/telegram.txt"
            if os.path.exists(file_path):
                os.remove(file_path)
            with app:
                with open("modules/messengers/telegram.txt", "w", encoding="utf-8") as file:
                    for dialog in app.get_dialogs():
                        if dialog.chat.type == ChatType.PRIVATE:
                            name = " ".join(dialog.chat.first_name.split()) if dialog.chat.first_name else ""
                            if dialog.chat.last_name:
                                name += " " + " ".join(dialog.chat.last_name.split())
                            
                            user_data = f"{name.strip()}|{dialog.chat.id}|@{dialog.chat.username or 'no_username'}\n"
                            file.write(user_data)
            time.sleep(600)
    except Exception as e:
        pass

def send_message_telegram(user_id, message):
    try:
        with app:
            app.send_message(chat_id=user_id, text=message)
    except Exception as e:
        saveTextfile('logs.txt', f"[ERROR] ошибка отправки сообщения :: {e}"+show_current_datetime(), True)
        print(logError+f"ошибка отправки сообщения :: {e}"+stopColor+show_current_datetime())

def telegram_contacts_thread():
    thread = threading.Thread(target=telegram_contacts, args=())
    thread.start()

def send_message_telegram_thread(user_id, message):
    thread = threading.Thread(target=send_message_telegram, args=(user_id, message,))
    thread.start()