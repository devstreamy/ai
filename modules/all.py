import psutil, time, pyautogui, keyboard, os, subprocess, datetime
from utils.logs import logSystem, stopColor, logError
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from modules.other import (show_current_datetime,
                           saveTextfile)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

def toggle_application(app_name, command, executable_name):
    is_running = False
    try:
        # Проверка запущенных процессов
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == executable_name.lower():
                print(f"{logSystem}{app_name} уже запущен. Завершаем процесс{stopColor}{show_current_datetime()}")
                try:
                    # Завершение процесса
                    subprocess.run(["taskkill", "/IM", executable_name, "/F"], check=True)
                    is_running = True
                except subprocess.CalledProcessError as e:
                    # Логирование ошибки при завершении процесса
                    error_message = f"Не удалось завершить процесс {executable_name}: {e}"
                    saveTextfile('logs.txt', f"ошибка в модуле запуска приложений: {error_message}{show_current_datetime()}", True)
                    print(f"{logError}ошибка в модуле запуска приложений: {error_message}{stopColor}{show_current_datetime()}")
                break

        if not is_running:
            # Запуск приложения
            print(f"{logSystem}Запускаем {app_name}...{stopColor}{show_current_datetime()}")
            subprocess.Popen(command)
    except Exception as e:
        # Логирование общих ошибок
        error_message = f"ошибка в модуле запуска приложений: {e}"
        saveTextfile('logs.txt', f"{error_message}{show_current_datetime()}", True)
        print(f"{logError}{error_message}{stopColor}{show_current_datetime()}")


def type_text(text):
    try:
        time.sleep(1)
        keyboard.write(text, delay=0.05)
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в модуле печатания текста: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в модуле печатания текста: {e}"+stopColor+show_current_datetime())

def launch_game_mode(): 
    try:
        os.system("taskkill /f /im steam.exe")
        steam_path = "C:\\Program Files (x86)\\Steam\\steam.exe"
        time.sleep(2)
        subprocess.Popen([steam_path, "-bigpicture"])
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в модуле запуска игрового режима: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в модуле запуска игрового режима: {e}"+stopColor+show_current_datetime())

def toggle_steam_game(game_name, app_id, executable_name):
    is_running = False
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == executable_name.lower():
                print(logSystem+f"{game_name} уже запущена. Завершаем процесс"+stopColor+show_current_datetime())
                subprocess.run(["taskkill", "/IM", executable_name, "/F"], check=True)
                is_running = True
                break

        if not is_running:
            print(logSystem+f"Запускаем {game_name} через Steam..."+stopColor+show_current_datetime())
            steam_command = f"steam://run/{app_id}"
            subprocess.Popen(["start", steam_command], shell=True)
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в модуле запуска игр: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в модуле запуска игр: {e}"+stopColor+show_current_datetime())

def empty_recycle_bin_powershell():
    command = "Invoke-Expression 'Clear-RecycleBin -Confirm:$false'"

    try:
        subprocess.run(["powershell", "-Command", command], check=True, stdout=subprocess.DEVNULL)
        print(logSystem + "Корзина была успешно очищена." + stopColor + show_current_datetime())
    except subprocess.CalledProcessError as e:
        print(logError + f"Ошибка при очистке корзины: {e}" + stopColor + show_current_datetime())

def open_settings():
    subprocess.run(["start", "ms-settings:"], shell=True)

def wifi():
    pass

def bluetooth():
    pass

def increase_volume():
    try:
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = min(1.0, current_volume + 0.15)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        print(logSystem+f"звук увеличен, теперь он {new_volume * 100}%"+stopColor+show_current_datetime())
    except Exception as e:
        print(logError+"Ошибка увелечения звука"+stopColor+show_current_datetime()())

def decrease_volume():
    try:
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = max(0.0, current_volume - 0.15)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        print(logSystem+f"звук уменьшен, теперь он {new_volume * 100}%"+stopColor+show_current_datetime())
    except Exception as e:
        print(logError+"Ошибка уменьшения звука"+stopColor+show_current_datetime())

def mute_volume():
    try:
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = max(0.0, current_volume - 1)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        print(logSystem+"Звук выключен"+stopColor)
    except Exception as e:
        print(logError+"Ошибка выключения звука"+stopColor+show_current_datetime()())

def max_volume():
    try:
        volume.SetMasterVolumeLevelScalar(1.0, None)
        print(logSystem+"Звук был включен на всю"+stopColor+show_current_datetime()())
    except Exception as e:
        print(logError+"Ошибка включения звука на всю"+stopColor+show_current_datetime()())

def change_language():
    try:
        pyautogui.keyDown('alt')
        pyautogui.press('shift')
        pyautogui.keyUp('alt')
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в модуле смены языка: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в модуле смены языка: {e}"+stopColor+show_current_datetime())

def dateRightNow():
    try:
        now = datetime.datetime.now()

        months = [
            "Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
            "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"
        ]

        formatted_date = f"Сейчас {now.year} год, {now.day} {months[now.month - 1]}"
        return formatted_date
    except Exception as e:
        saveTextfile('logs.txt',f"[ERROR] ошибка в получении даты: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в получении даты: {e}"+stopColor+show_current_datetime())

def open_program(program_path):
    try:
        os.startfile(program_path)
        print(logSystem+ "программа успешно запущена."+stopColor)
    except Exception as e:
        saveTextfile('logs.txt',f"[ERROR] ошибка при запуске программы: {e}"+show_current_datetime(), True)
        print(logError+f"ошибка при запуске программы: {e}"+stopColor+show_current_datetime())