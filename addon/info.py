import os, ast, json
from modules.other import show_current_datetime, saveTextfile
from utils.logs import logError, stopColor

def countModules():
    folder_path = os.path.abspath('modules')
    if not os.path.isdir(folder_path):
        saveTextfile('logs.txt', f"[ERROR] указанный путь не является папкой (countModules). {show_current_datetime()}", True)
        print(logError+"указанный путь не является папкой."+stopColor+show_current_datetime())
        return None
    modulesCount = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                modulesCount += 1

    return modulesCount

def countFunctions():
    folder_path = os.path.abspath('modules')
    
    if not os.path.isdir(folder_path):
        saveTextfile('logs.txt', f"[ERROR] указанный путь не является папкой (countFunctions). {show_current_datetime()}", True)
        print(logError+"указанный путь не является папкой."+stopColor+show_current_datetime())
        return None

    total_functions = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                try:
                    parsed_code = ast.parse(code)
                except SyntaxError:
                    saveTextfile('logs.txt', f"[ERROR] ошибка анализа синтаксиса в файле :: {file_path}"+show_current_datetime(), True)
                    print(logError+f"ошибка анализа синтаксиса в файле :: {file_path}"+stopColor+show_current_datetime())
                    continue
                functions_in_file = sum(1 for node in ast.walk(parsed_code) if isinstance(node, ast.FunctionDef))
                total_functions += functions_in_file

    return total_functions

def countJson(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            chat_history = json.load(f)

        user_dialogs = 0
        assistant_dialogs = 0
        
        for item in chat_history:
            if item["role"] == "user":
                user_dialogs += 1
            elif item["role"] == "assistant":
                assistant_dialogs += 1
        
        return user_dialogs+assistant_dialogs
    except Exception as e:
        saveTextfile('logs.txt', f"[ERROR] произошла ошибка (countJson) при чтении файла JSON :: {e}"+show_current_datetime(), True)
        print(logError+f"произошла ошибка при чтении файла JSON :: {e}"+stopColor+show_current_datetime())
        return None, None 