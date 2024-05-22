import cv2
import numpy as np
from PIL import ImageGrab
import threading, time, sqlite3
from utils.logs import stopColor, logWindow, logError
from modules.other import show_current_datetime, saveTextfile
from utils.config import (FullLogsConfig)
from modules.database import addTimeApp

conn = sqlite3.connect('modules/database/database.db', check_same_thread=False)
cursor = conn.cursor()

def findOn(screen, images):
    for name, data in images.items():
        image = cv2.imread(data['path'], cv2.IMREAD_COLOR)
        if image is None:
            print(logError+f"Ошибка загрузки изображения: {data['path']}"+stopColor+show_current_datetime()())
            continue
        result = cv2.matchTemplate(screen, image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        if max_val > data.get('threshold', 0.8):
            return name
    return None


def recordScreen():
    try:
        images = {
            "dota 2": {"path": "modules/images/dota2.png", "threshold": 0.85},
            "dota 2": {"path": "modules/images/dota2_2.png", "threshold": 0.75},
            "youtube": {"path": "modules/images/youtube.png", "threshold": 0.75},
            "vk": {"path": "modules/images/vk1.png", "threshold": 0.75},
            "vk": {"path": "modules/images/vk2.png", "threshold": 0.75},
            "yandex": {"path": "modules/images/yandex.png", "threshold": 0.75},
            "gmail": {"path": "modules/images/gmail.png", "threshold": 0.75}
        }

        results = {}
        start_time = time.time()

        while True:
            screen = np.array(ImageGrab.grab())
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
            try:
                found = findOn(screen, images)
                if found:
                    results[found] = results.get(found, 0) + 1
                    addTimeApp(found)
                else:
                    results['Не обнаружено'] = results.get('Не обнаружено', 0) + 1

            except Exception as e:
                pass

            if time.time() - start_time > 15:
                if FullLogsConfig == "True":
                    output = ' | '.join(f"{key}: {value}" for key, value in results.items())
                    saveTextfile('logs.txt',"информация о экране (за 15 секунд) " + output + show_current_datetime(), True)
                    print(logWindow + "информация о экране (за 15 секунд) " + output + stopColor + show_current_datetime())
                    start_time = time.time()
                    results = {}
                else:
                    pass

            time.sleep(1)
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в получении инфорамции о экране :: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в получении инфорамции о экране :: {e}"+stopColor+show_current_datetime())
def recordScreen_thread():
    thread = threading.Thread(target=recordScreen, args=())
    thread.start()
