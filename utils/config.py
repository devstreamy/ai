import json

def load_config(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        return json.load(file)

config = load_config("utils/config.json")

versionConfig = config['main']['version']
nameConfig = config['main']['name']
chatgptCFG = config['main']['chatgpt']

check_screenConfig = config['settings']['CheckScreen']
check_cameraConfig = config['settings']['CheckCamera']
voiceLogingConfig = config['settings']['VoiceLoging']
FullLogsConfig = config['settings']['FullLogs']

mic_indexConfig = config['other']['mic_index']
show_micConfig = config['other']['show_mic']

ipLogger = config['SSH']['ip']
usernameLogger = config['SSH']['username']
passwordLogger = config['SSH']['password']
pathSendLogger = config['SSH']['path_send']

franceWireguard = config['wireguard']['france']
niderlandsWireguard = config['wireguard']['niderlands']
russiaWireguard = config['wireguard']['ru']

protocols21 = config['protocols']['21']

phrases = ["Сделано", "Да сэр", "Хорошо", "Будет сделано", "Сделала", 
           "Уже в процессе", "Без проблем", "Принято", "Конечно", "Так точно", "Поняла, приступаю",
             "Немедленно", "Ваше желание - закон", "Приступаю к выполнению", "Уже занимаюсь", "В процессе"]

image_keywords = ["фото", "картинк", "изображен"]
print_commands = ["напечатай", "напиши"]
weather_patterns = [
    ("какая", "погода", "сейчас"),
    ("сколько", "градусов", "на", "улице"),
    ("погода", "сейчас"),
    ("на", "улице", "сколько", "градусов")
]
