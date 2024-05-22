from cryptography.fernet import Fernet
from modules.database import updateCrypt
import os

def generateKey(file_path):
    try:
        with open(file_path, "rb") as key_file:
            key = key_file.read()  # Пытаемся прочитать существующий ключ
    except FileNotFoundError:
        key = Fernet.generate_key()  # Ключа нет, генерируем новый
        with open(file_path, "wb") as key_file:
            key_file.write(key)  # Сохраняем новый ключ в файл
    return key

def encrypt(message, key):
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

def decrypt(encrypted_message, key):
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message).decode()
    return decrypted_message

def decryptTXT(encrypted_message, key):
    f = Fernet(key)
    try:
        decrypted_message = f.decrypt(encrypted_message).decode()
        return decrypted_message
    except Exception as e:
        return f"Ошибка дешифрования: {str(e)}"

def encryptTXT(message, key):
    f = Fernet(key)
    try:
        encrypted_message = f.encrypt(message.encode())
        return encrypted_message.decode()  # Преобразование в строку перед возвратом
    except Exception as e:
        return f"Ошибка шифрования: {str(e)}"

def decryptLogs(filename, key):
    try:
        updateCrypt(1)
        temp_filename = filename + '.tmp'
        with open(filename, 'r', encoding='utf-8') as file, open(temp_filename, 'w', encoding='utf-8') as temp_file:
            for line in file:
                line = line.strip()
                if line:
                    line_bytes = bytes(line[2:-1], 'utf-8')
                    decrypted_line = decrypt(line_bytes, key)
                    temp_file.write(decrypted_line + '\n')
        
        os.replace(temp_filename, filename)
    except Exception as e:
        pass

def encryptLogs(filename, key):
    try:
        updateCrypt(0)
        temp_filename = filename + '.tmp'
        with open(filename, 'r', encoding='utf-8') as file, open(temp_filename, 'w', encoding='utf-8') as temp_file:
            for line in file:
                line = line.strip()
                if line:
                    encrypted_line = encryptTXT(line, key)
                    temp_file.write("b'"+encrypted_line+"'" + '\n')

        os.replace(temp_filename, filename)
    except Exception as e:
        pass

key_file_path = "modules/keys/encryption.key"
key = generateKey(key_file_path)