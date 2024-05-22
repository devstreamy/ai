import os, pygame, hashlib, requests
from modules.other import (show_current_datetime,
                           saveTextfile)
from utils.logs import stopColor, logError
from utils.config import (mic_indexConfig)
import speech_recognition as sr
recognized_phrases = []

recognizer = sr.Recognizer()
mic_index = mic_indexConfig

voice = "yH99koDmpZDuNhZsd2QD"
audio_dir = "audio"

CHUNK_SIZE = 1024
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"

def speach(text):
    try:
        pygame.mixer.init()

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": "ad3245856bf4144cf4ec64044f3e9870"
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "use_speaker_boost": True
            }
        }

        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)

        hash_object = hashlib.md5(text.encode())
        audio_file_name = hash_object.hexdigest() + ".mp3"
        audio_file_path = os.path.join(audio_dir, audio_file_name)

        if not os.path.exists(audio_file_path):
            response = requests.post(url, json=data, headers=headers)
            with open(audio_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)

        pygame.mixer.music.load(audio_file_path) 
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # pygame.mixer.music.unload()
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в генерации голоса :: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в генерации голоса :: {e}"+stopColor+show_current_datetime())