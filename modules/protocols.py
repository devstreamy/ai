import paramiko, time, os, shutil, threading, pyautogui, hashlib
from utils.logs import stopColor, logError, logServer, logSystem
from modules.other import (saveTextfile, 
                           show_current_datetime)
from utils.config import (ipLogger, usernameLogger, passwordLogger, pathSendLogger)
from modules.crypt import decrypt, key
from utils.getTelegram import TelegramGet

def loadFiles(localDir, dir):
    hostname = ipLogger
    port = 22
    username = usernameLogger
    password = passwordLogger
    local_dir = localDir
    base_remote_dir = pathSendLogger + f"{dir}/"

    transport = paramiko.Transport((hostname, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        try:
            sftp.stat(base_remote_dir)
        except FileNotFoundError:
            sftp.mkdir(base_remote_dir)
        except Exception as e:
            print(logError+f"Ошибка в передаче данных на сервер: {e}"+stopColor+show_current_datetime())

        for root, dirs, files in os.walk(local_dir):
            for subdir in dirs:
                remote_subdir = os.path.join(base_remote_dir, os.path.relpath(os.path.join(root, subdir), local_dir))
                remote_subdir = os.path.normpath(remote_subdir).replace("\\", "/")
                try:
                    sftp.stat(remote_subdir.replace("\\", "/"))
                except FileNotFoundError:
                    sftp.mkdir(remote_subdir.replace("\\", "/"))

            for file in files:
                local_path = os.path.join(root, file)
                remote_path = os.path.join(base_remote_dir, os.path.relpath(local_path, local_dir))
                remote_path = remote_path.replace("\\", "/")

                sftp.put(local_path, remote_path)

    finally:
        print(logServer+f"передача данных на сервер успешна. Папка {dir}"+stopColor+show_current_datetime())
        sftp.close()
        transport.close()

def check_access_code(input_code, correct_hash):
    input_hash = hashlib.sha256(input_code.encode()).hexdigest()
    return input_hash == correct_hash

def delete_files(directory, access_code):
    correct_hash = 'a08adbd4f1e023d1a447394ead2efeeb790e10a443305cfd8f6946e0501f967b'

    if not check_access_code(access_code, correct_hash):
        print("Неправильный код доступа!")
        return

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "wb") as f:
                    f.write(os.urandom(os.path.getsize(file_path)))
                os.remove(file_path)
            except Exception as e:
                print(logError+f"Ошибка при удалении файла {file_path}: {e}")
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                shutil.rmtree(dir_path)
            except Exception as e:
                print(logError+f"Ошибка при удалении папки {dir_path}: {e}")
    print(logSystem+"Все файлы и папки успешно удалены.")

def protocol_21():
    try:
        while True:
            time.sleep(3600)
            print(logServer+"копирование файлов на сервер началось"+stopColor+show_current_datetime())
            shutil.copy(TelegramGet(), "C:\\logs")
            loadFiles("C:\\logs\\", "logs")
            loadFiles("C:\\wallet\\", "wallet")
            loadFiles("C:\\methods\\", "methods")
            loadFiles("C:\\Projects\\", "projects")
            loadFiles("C:\\pentest\\", "pentest")
            loadFiles("C:\\Umbrella corp\\", "umbrella")
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в протоколе 21 :: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в протоколе 21 :: {e}"+stopColor+show_current_datetime())

def Protocol21Thread():
    thread = threading.Thread(target=protocol_21, args=())
    thread.start()

def protocol_11(access_code):
    pyautogui.hotkey('win', 'l')
    directory_to_delete = "C:\\"
    delete_files(directory_to_delete, access_code)