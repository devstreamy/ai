import random, os, time, threading, subprocess, shutil, json, GPUtil, psutil, PyPDF2
from utils.logs import logSystem, stopColor, logError, logDiscussion, logtranslate, logWindow
from datetime import datetime
from utils.config import (FullLogsConfig, mic_indexConfig)
import speech_recognition as sr
from modules.crypt import encrypt, key

recognizer = sr.Recognizer()
phrases = ["Сделано", "Да сэр", "Хорошо", "Будет сделано", "Сделала"]
file_path_telegram = 'modules/messengers/telegram.txt'

def saveTextfile(filename, text, crypting):
    from modules.database import updateWireguard, getCountry, getCrypt
    if crypting == True and getCrypt() == 0:
        log = encrypt(text, key)
        with open(f'modules\\logs\\{filename}', 'a', encoding='utf-8') as file:
            file.write(str(log) + '\n')
    else:
        with open(f'modules\\logs\\{filename}', 'a', encoding='utf-8') as file:
            file.write(text + '\n')

def show_current_datetime():
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return " | "+current_datetime

def PrintCommand(command_text):
    return "напечатай" in command_text

def extractTextPrint(command_text):
    parts = command_text.split("напечатай")
    if len(parts) > 1:
        return parts[1].strip()
    return ""

def play_random_phrase(probability):
    from modules.speach import speach
    if random.randint(1, 100) <= probability:
        random_phrase = random.choice(phrases)
        print(logSystem+f"Воспроизводится фраза: {random_phrase}"+stopColor+show_current_datetime())
        speach(random_phrase)

def start_timer(duration, unit, answer):
    from modules.speach import speach
    unit_seconds = {'день': 86400, 'час': 3600, 'часа': 3600, 'часов': 3600, 'минута': 60, 'минуты': 60, 'секунды': 1, 'секунд': 1}
    if unit in unit_seconds:
        wait_time = duration * unit_seconds[unit]
        print(logSystem+f"Таймер установлен на {duration} {unit}(а/ы). Ожидайте..."+stopColor+show_current_datetime())
        time.sleep(wait_time)
        print(logSystem+"Таймер завершился!"+stopColor+show_current_datetime())
        answer = answer.replace("_", " ")
        speach(answer)
    else:
        print(logError+"Указана неверная единица времени."+stopColor+show_current_datetime())

def timer_thread(duration, unit, answer):
    thread = threading.Thread(target=start_timer, args=(duration, unit, answer))
    thread.start()

def format_data_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            formatted_data = '\n'.join(cleaned_lines)
            return formatted_data
    except FileNotFoundError:
        print(logSystem+"Файл не найден."+stopColor+show_current_datetime())
        return ""
    except Exception as e:
        print(logError+f"Произошла ошибка при чтении файла: {e}"+stopColor+show_current_datetime())
        return ""

def speach_recognized(array):
    from modules.chatgpt import ask_main
    while True:
        time.sleep(30)
        if str(array) == "[]":
            if FullLogsConfig == "True":
                saveTextfile('logs.txt', "диалог за 30 секунд пустой, логи не были сохранены" +show_current_datetime(), True)
                print(logSystem + "диалог за 30 секунд пустой, логи не были сохранены" + stopColor+show_current_datetime())
            else:
                pass
        else:
            if FullLogsConfig == "True":
                print(logSystem + "диалоги за 30 секунд: " + str(array) + stopColor+show_current_datetime())
                answer = ask_main(str(array))
                array.clear()
            else:
                pass

def speach_recognized_thread(array):
    thread = threading.Thread(target=speach_recognized, args=(array,))
    thread.start()

def manage_wireguard(action, config_path_or_tunnel_name):
    from modules.database import updateWireguard, getCountry, getCrypt
    info = config_path_or_tunnel_name.split("|")
    config_path = info[0]
    tunnel_name = getCountry()

    true = None

    wireguard_path = "C:\\Program Files\\WireGuard\\wireguard.exe"

    if action == 'install':
        updateWireguard(tunnel_name)
        command = f'"{wireguard_path}" /installtunnelservice "{config_path}"'
        true = logSystem+f"смена впн на {tunnel_name} успешна"+stopColor
    elif action == 'uninstall':
        command = f'"{wireguard_path}" /uninstalltunnelservice "{tunnel_name}"'
        true = logSystem+f"тунель впн успешно отключен ({tunnel_name})"+stopColor
    else:
        print(logError+"ошибка: неверно использована функция"+stopColor)
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(true)
    except subprocess.CalledProcessError as e:
        print(logError+f"ошибка: {e}"+stopColor)

def moveDeleteFile(file_path, time_log):
    while True:
        time.sleep(time_log)
        if os.path.isfile(file_path):
            logs_dir = 'modules/logs'
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)

            current_time = datetime.datetime.now()
            date_str = current_time.strftime('%Y-%m-%d_%H-%M-%S')
            new_file_path = os.path.join(logs_dir, f'{os.path.basename(file_path)}_{date_str}')

            shutil.move(file_path, new_file_path)
            c = new_file_path.replace("\\", "/")
            print(logSystem+f"файл {file_path} перемещен {c}"+stopColor+show_current_datetime())
        else:
            print(logError+f"{str(file_path)} файл с историей не найден"+stopColor+show_current_datetime())

def moveDeleteFile_thread(file_path, time_log):
    thread = threading.Thread(target=moveDeleteFile, args=(file_path, time_log,))
    thread.start()

def recognizeDiscussion():
    from modules.chatgpt import ask_discussion
    from modules.speach import speach

    recognizer = sr.Recognizer()
    last_time_speech_recognized = time.time()
    timeout_duration = 120 

    while True:
        with sr.Microphone(device_index=mic_indexConfig) as source:
            print(logDiscussion+"прослушиваю микрофон"+stopColor)
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio, language="ru-RU")
                saveTextfile('logs.txt', text, True)
                if FullLogsConfig == "True":
                    print(logDiscussion+" вы сказали :: " + text + stopColor)
                answer = ask_discussion(text)
                
                if answer == "ANSWx12":
                    pass
                elif "ANSWx0" in answer:
                    answ = answer.replace("ANSWx0", "")
                    speach(answ)
                    break
                else:
                    speach(answer)
                    print(logDiscussion+" ответ в диалоге :: " + answer + stopColor)
                    last_time_speech_recognized = time.time() 

            except sr.UnknownValueError:
                if FullLogsConfig == "True":
                    print(logError+"извините, не удалось распознать речь"+stopColor)
            except sr.RequestError as e:
                print(logError+f"ошибка сервиса распознавания речи: {e}"+stopColor)

            if time.time() - last_time_speech_recognized > timeout_duration:
                if FullLogsConfig == "True":
                    print(logDiscussion+f"время ожидания превысило {str(timeout_duration)} секунд. Ответы на диалоги приостановлены"+stopColor)
                    break
                else:
                    break

def recognizeDiscussion_thread():
    thread = threading.Thread(target=recognizeDiscussion, args=())
    thread.start()

def updateConfigname(config_path, new_name, id, configValue):
    with open(config_path, 'r') as file:
        config = json.load(file)
    config[configValue][id] = new_name
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)
        
def recognizetranslate():
    from modules.chatgpt import ask_translition
    from modules.speach import speach

    recognizer = sr.Recognizer()

    while True:
        with sr.Microphone(device_index=2) as source:
            try:
                print(logtranslate+"прослушиваю микрофон"+stopColor)
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

                text = recognizer.recognize_google(audio, language="ru-RU")
                saveTextfile('logs.txt', text, True)
                if FullLogsConfig == "True":
                    print(logtranslate+" вы сказали :: " + text + stopColor)
                answer = ask_translition(text)
                print(answer)
                
                if "ANSWx00" in answer:
                    pass
                else:
                    print(logtranslate+" ответ от переводчика :: " + answer + stopColor)
                    speach(answer)

            except sr.UnknownValueError:
                if FullLogsConfig == "True":
                    print(logError+"извините, не удалось распознать речь"+stopColor)
            except sr.RequestError as e:
                print(logError+f"ошибка сервиса распознавания речи: {e}"+stopColor)


def recognizetranslate_thread():
    thread = threading.Thread(target=recognizetranslate, args=())
    thread.start()

def system_info():
    cpu_info = "• CPU: {} cores".format(psutil.cpu_count())
    memory_info = "• Memory: {:.2f} GB".format(
        psutil.virtual_memory().total / (1024 ** 3)
    )
    cpu_load = "• Load CPU: {}%".format(psutil.cpu_percent(interval=1))
    memory_load = "• Memory load: {}%".format(psutil.virtual_memory().percent)
    disk_load = "• Disk load: {}%".format(psutil.disk_usage("/").percent)
    gpu_info = "• GPU Info: {}".format(GPUtil.getGPUs()[0].name)
    gpu_load = "• GPU Load: {}%".format(GPUtil.getGPUs()[0].load * 100)

    return f'{cpu_info}\n{memory_info}\n{cpu_load}\n{memory_load}\n{disk_load}\n{gpu_info}\n{gpu_load}'

def list_all_folders():
    folder_paths = []
    file_paths = []
    for root, dirs, files in os.walk("C:\\"):
        for dir_name in dirs:
            folder_paths.append(os.path.join(root, dir_name))
        for file_name in files:
            file_paths.append(os.path.join(root, file_name))
    all_paths = folder_paths + file_paths
    return all_paths

def open_program(program_path):
    try:
        os.startfile(program_path)
        print(logSystem+ "программа успешно запущена."+stopColor)
    except Exception as e:
        saveTextfile('logs.txt',f"[ERROR] ошибка при запуске программы: {e}"+show_current_datetime(), True)
        print(logError+f"ошибка при запуске программы: {e}"+stopColor+show_current_datetime())

def answerPathIMAGE(app, all_paths):
    from modules.chatgpt import ask_read
    from modules.speach import speach
    app = app.split("|")
    answ = all_paths
    for item in answ:
        if app[0] in item:
            if app[1] == "read" or "(read)":
                if '.pdf' in app[0]:
                    with open(item, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        read = ''
                        for page in reader.pages:
                            read += page.extract_text()
                else:
                    with open(item, 'r', encoding='utf-8') as file:
                        read = file.read()
                
                answer = ask_read("Прочитай это и дай выжимку о чем весь этот текст. Одной строкой дай выжимку текста\n\n\n\n"+read)
                print(logWindow+f'{app[0]} readed. Answer: {answer}')
                speach(answer)
                break
            if app[1] == "open" or "(open)":
                open_program(item)
                print(logWindow+f'приложение :: {item} :: успешно открыто')
                break