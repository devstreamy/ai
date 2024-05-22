import openai, json, requests, time, base64, io
from modules.other import (saveTextfile, 
                           show_current_datetime)
from utils.logs import stopColor, logError, logWindow
from utils.config import chatgptCFG, nameConfig
from addon.checkbox import getConfigInfo
from PIL import ImageGrab

openai.api_key = getConfigInfo("main", "openai_apikey")
api_key = getConfigInfo("main", "openai_apikey")

def take_screenshot_to_base64():
    screenshot = ImageGrab.grab()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()
    base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
    return base64_encoded

def chatWithImage(getInfo):
    start_time = time.time()

    base64_image = take_screenshot_to_base64()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Ты умный голосовой помощник, и ты должен возвращать данные в том формате в котором я попрошу. Это снимок с экрана тебе нужно найти файл который я скажу и вернуть его название + папку в которой он находится. Пример: \nВходные данные:\n прочитай файл с историей чата\n Ответ:\n AI\\chat_history.json \n\n второй пример: \nВходные данные:\n открой файл конфигурации\n Ответ:\n calculator\\Cargo.toml \n\nТак же ты должен возвращать название папки если это попросят\n\nP.s. Ответ должен быть просто название файла без всяких возврат: название файла и так далее просто название файла + папка в которой он находится и все. Формат ответа должен быть такой: папка\\файл|(команда. Если открой то: open, если прочитай то: read) или папка\\папка|(команда. Если открой то: open, если прочитай то: read). Также если запрос будет не по теме или не будет файл найден который запрашевается или папка ответ должен быть: Answ0x01. Учти название файла должно быть точ в точ даже такое Text-wqe12dsa.pdf даже такое может быть. ЕСЛИ НА ЭКРАНЕ НЕТУ ПАПКИ ТО ТЫ ДОЛЖЕН ИГНОРИРОВАТЬ ЛЮБЫЕ ДЕЙСТВИЕ И ЗАПРОСЫ ПРОЧИТАТЬ ПОТОМУ ЧТО ПАПКИ НА ЭКРАНЕ НЕТУ. если нету папки то не читать экран\n\n. Запрос сейчас: {getInfo}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 4096
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    end_time = time.time()
    execution_time = end_time - start_time
    info = response.json()['choices'][0]['message']['content']
    print(logWindow+f'получена информация о экране {info}'+" | время ответа", execution_time, "секунд"+stopColor)

    return response.json()['choices'][0]['message']['content']
    # print("Response:", response.json()['choices'][0]['message']['content'])
    # print("Execution time:", execution_time, "seconds")

def save_chat_history(chat_history, history_file_path):
    try:
        with open(history_file_path, 'w', encoding='utf-8') as file:
            json.dump(chat_history, file, ensure_ascii=False, indent=4)
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в сохранение истории chatGPT :: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в сохранение истории chatGPT :: {e}"+stopColor+show_current_datetime())

def load_chat_history(history_file_path):
    try:
        with open(history_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def ask_gpt(question, system_context, history_file_path):
    try:
        chat_history = load_chat_history(history_file_path)
        if not chat_history:
            chat_history.append({"role": "system", "content": system_context})
        chat_history.append({"role": "user", "content": question})
        
        response = openai.ChatCompletion.create(
            model=f"{chatgptCFG}",
            messages=chat_history
        )
        answer = response.choices[0].message['content']
        chat_history.append({"role": "assistant", "content": answer})
        save_chat_history(chat_history, history_file_path) 
        return answer
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в модуле chatgpt при отправке сообщения/чата :: {e}"+show_current_datetime(), True)
        print(logError+f"ошибка в модуле chatgpt при отправке сообщения/чата :: {e}"+stopColor)

chat_history = 'chat_history.json'
time_history = 'time_history.json'
telegram_history = 'telegram_history.json'
weather_history = 'weather_history.json'
weatherA_history = 'weatherA_history.json'
discussion_history = 'discussion_history.json'
translition_history = 'translition_history.json'
read_history = 'read_history.json'

def ask_main(question):
    questionN = getConfigInfo("settings_chat", "ask_main")
    return ask_gpt(question, f"Ты умный голосовой помощник {nameConfig}. {questionN}", chat_history)

def ask_time(question):
    questionN = getConfigInfo("settings_chat", "ask_time")
    return ask_gpt(question, f"Ты умный голосовой помощник {nameConfig}. {questionN}", time_history)

def ask_telegram(question):
    questionN = getConfigInfo("settings_chat", "ask_telegram")
    return ask_gpt(question, f"Ты умный голосовой помощник {nameConfig}. {questionN}", telegram_history)

def ask_weather(question):
    questionN = getConfigInfo("settings_chat", "ask_weather")
    return ask_gpt(question, f"Ты умный голосовой помощник {nameConfig}. {questionN}", weather_history)

def ask_weatherA(question):
    questionN = getConfigInfo("settings_chat", "ask_weatherA")
    return ask_gpt(question, f"Ты умный голосовой помощник {nameConfig}. {questionN}", weatherA_history)    

def ask_discussion(question):
    questionN = getConfigInfo("settings_chat", "ask_discussion")
    return ask_gpt(question, f"Ты умный голосовой помощник {nameConfig}. {questionN}", discussion_history)

def ask_translition(question):
    questionN = getConfigInfo("settings_chat", "ask_translition")
    return ask_gpt(question, f"Ты умный голосовой помощник {nameConfig}. {questionN}", translition_history)

def ask_read(question):
    questionN = getConfigInfo("settings_chat", "ask_main")
    return ask_gpt(question, f"Ты умный голосовой помощник {nameConfig}. {questionN}", read_history)