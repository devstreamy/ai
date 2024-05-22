import psutil, subprocess, os, time, re
from utils.logs import logSystem, stopColor, logError
from modules.other import (show_current_datetime,
                           saveTextfile)
from modules.speach import speach

def add_command_to_file(filepath, cmd):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    start_index = None
    end_index = None
    for i, line in enumerate(lines):
        if 'commands = {' in line:
            start_index = i
        if start_index is not None and '}' in line:
            end_index = i
            break
    
    if start_index is not None and end_index is not None:
        lines.insert(end_index, f'    {cmd},\n')
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.writelines(lines)
    else:
        print(logError+"словарь commands не найден в файле."+stopColor+show_current_datetime())

def open_app(app_name, command):
    is_running = False
    executable_name = app_name.split('\\')[-1]
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == executable_name.lower():
                print(logSystem+f"{command} уже запущен. Завершаем процесс"+stopColor+show_current_datetime())
                subprocess.run(["taskkill", "/IM", executable_name, "/F"], check=True)
                is_running = True
                break

        if not is_running:
            print(logSystem+f"Запускаем {command}..."+stopColor+show_current_datetime())
            os.startfile(app_name)
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в модуле запуска приложений: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в модуле запуска приложений: {e}"+stopColor+show_current_datetime())

def execute_cmd_command(command, name):
    try:
        subprocess.run(command, shell=True, check=True)
        print(logSystem+f'команда :: {name} была успешно запущена'+stopColor)
    except subprocess.CalledProcessError as e:
        print(logError+ f"Команда завершилась с ошибкой: {e}"+stopColor+show_current_datetime())

def open_url(url, name):
    os.system(f"start chrome {url}")
    print(logSystem+f'открытие сайта :: {name} была успешно'+stopColor)

def construct_some(command):
        command = command.replace('\\', '/')
        commands = command.split('|')
        for cmd in commands:
            if cmd[:4] == 'open' and (cmd[:8] != 'open_url'):
                pattern = r'"([^"]*)"|(\d+)'
                matches = re.findall(pattern, cmd)
                results = [match[0] if match[0] else match[1] for match in matches]
                open_app(results[0], results[1])
            elif cmd[:4] == 'time':
                pattern = r'"([^"]*)"|(\d+)'
                matches = re.findall(pattern, cmd)
                results = [match[0] if match[0] else match[1] for match in matches]
                time.sleep(int(results[0]))
            elif cmd[:8] == 'open_url':
                pattern = r'"([^"]*)"|(\d+)'
                matches = re.findall(pattern, cmd)
                results = [match[0] if match[0] else match[1] for match in matches]
                open_url(results[0], results[1])

            elif cmd[:5] == 'voice':
                pattern = r'"([^"]*)"|(\d+)'
                matches = re.findall(pattern, cmd)
                results = [match[0] if match[0] else match[1] for match in matches]
                speach(results[0])