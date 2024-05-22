import sqlite3

conn = sqlite3.connect('modules/database/database.db', check_same_thread=False)
cursor = conn.cursor()

def addTimeApp(app_name):
    cursor.execute('SELECT time FROM infoTime WHERE app = ?', (app_name,))
    result = cursor.fetchone()
    if result:
        new_time = result[0] + 1
        cursor.execute('UPDATE infoTime SET time = ? WHERE app = ?', (new_time, app_name))
    else:
        cursor.execute('INSERT INTO infoTime (app, time) VALUES (?, 1)', (app_name,))
    conn.commit()

def updateWireguard(new_country):
    try:
        update_query = "UPDATE other SET wireguard = ? WHERE rowid = 1;"
        cursor.execute(update_query, (new_country,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")

def getCountry():
    try:
        query = "SELECT wireguard FROM other WHERE rowid = 1;"
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return "Данные не найдены"
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")
        return None

def updateCrypt(crypt_style):
    try:
        update_query = "UPDATE other SET crypt = ? WHERE rowid = 1;"
        cursor.execute(update_query, (crypt_style,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")

def getCrypt():
    try:
        query = "SELECT crypt FROM other WHERE rowid = 1;"
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return "Данные не найдены"
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")
        return None
    
def updatePlaylist(playlist):
    try:
        update_query = "UPDATE other SET player = ? WHERE rowid = 1;"
        cursor.execute(update_query, (playlist,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")

def getPlaylist():
    try:
        query = "SELECT player FROM other WHERE rowid = 1;"
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return "Данные не найдены"
    except sqlite3.Error as e:
        print(f"Произошла ошибка: {e}")
        return None