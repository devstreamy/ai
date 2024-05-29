import flet 
import flet as ft 
from modules.other import updateConfigname
from addon.info import countModules, countFunctions, countJson
from addon.checkbox import (accessToScreenCheckbox, 
                            autoloadCheckbox, 
                            accessToCameraCheckbox, 
                            voiceLogsCheckbox,
                            ShowMicIndexCheckbox,
                            timeoutLogsCheckbox,
                            getConfigInfo)
import os, asyncio, vosk, keyboard, requests, datetime
from modules.protocols import protocol_11
from flet import ( 
    Banner, 
    ElevatedButton, 
    Icon, 
    Text, 
    colors, 
    icons,
    AppBar,
    Icon,
    IconButton,
    Page,
    PopupMenuButton,
    PopupMenuItem,
    Row,
    Text,
    colors,
    icons,
    theme,
    TextField)
from utils.logs import successApp
import speech_recognition as sr
from modules.DALL_E import generate_image
from modules.speach import (speach)
from modules.browser import chrome_openUrl
from modules.chatgpt import (ask_main,
                             ask_time,
                             ask_telegram,
                             ask_weather,
                             ask_weatherA)
from modules.msg import (send_message_telegram, 
                         telegram_contacts_thread)
from modules.other import (play_random_phrase,
                           timer_thread,
                           format_data_from_file,
                           file_path_telegram,
                           speach_recognized_thread,
                           saveTextfile,
                           moveDeleteFile_thread,
                           recognizeDiscussion_thread,
                           system_info,
                           list_all_folders,
                           answerPathIMAGE,
                           game_install)
from modules.world import get_weather
from modules.window import recordScreen_thread
from modules.protocols import Protocol21Thread
import threading, time, re
from utils.logs import logUser, logSystem, success, stopColor, logError, logInfo, logInfoApp, logSystemApp, logUserApp
from utils.config import (versionConfig, 
                          nameConfig, 
                          check_screenConfig, 
                          check_cameraConfig, 
                          mic_indexConfig, 
                          show_micConfig,
                          voiceLogingConfig,
                          FullLogsConfig, 
                          protocols21,
                          phrases,
                          image_keywords,
                          print_commands,
                          weather_patterns)
from utils.commands import count_commands
from modules.all import open_program
import sounddevice as sd
import queue, json, sys
from addon.checkbox import getConfigInfo
from utils.logs import logUser, stopColor
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import pyautogui

q = queue.Queue()
API_TOKEN = getConfigInfo('telegram', "API_TOKEN")
ALLOWED_USER = getConfigInfo('telegram', "ALLOWED_USER")

def q_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))
class Protocol11States(StatesGroup):
    waiting_for_code = State()

show_mic = show_micConfig
check_screen = check_screenConfig
voiceLoging = voiceLogingConfig
FullLogs = FullLogsConfig

recognizer = sr.Recognizer()
recognized_phrases = []
installed = None
if getConfigInfo('main', "chatgpt") == 'gpt-4oa':
    all_paths = list_all_folders()

def process_command(command_text):
    from utils.commands import commands
    download_install_patterns = [
        r"(скачай|установи) (.+)"
    ]
    name_pattern = fr"^({nameConfig}[, ]+)(.*)"
    name_match = re.match(name_pattern, command_text, re.IGNORECASE)
    message_match = re.match(r"(напиши|отпиши) ([^ ]+) (.+)", command_text, re.IGNORECASE)
    timer_match = re.search(r"(включи|запусти|сделай|поставь) таймер на (.+)", command_text, re.IGNORECASE)
    match = re.search(r"(пожалуйста )?расскажи( пожалуйста)?( про)? (.+)", command_text, re.IGNORECASE)

    def contains_all(command, words_tuple):
        return all(word in command for word in words_tuple)
    
    if any(contains_all(command_text, pattern) for pattern in weather_patterns):
        answer = ask_weather(command_text)
        cities = []
        cities.append(answer) 
        weather_info = get_weather(cities)
        for info in weather_info:
            answer = ask_weatherA(info)
            print(logSystem+str(answer)+stopColor)
            speach(answer)  

    elif message_match:
        formatted_data = format_data_from_file(file_path_telegram)
        answer = ask_telegram(formatted_data+"\n\n"+command_text).split(" ")
        if len(answer) > 1:
            send_message_telegram(answer[1], answer[0].replace("_", " "))
            print(logSystem+f"сообщение в telegram успешно отправлено к {answer[2]}"+stopColor)
        else:
            answer[0] = answer[0].replace("_", " ")
            speach(answer[0])
            print(logSystem+"контакт telegram не найдет"+stopColor)
    
    elif timer_match:
        try:
            answer = ask_time(command_text)
            play_random_phrase(100)
            answer = answer.split(" ")
            print(logSystem+str(answer)+stopColor)
            timer_thread(int(answer[0]), answer[1], answer[2])
        except Exception as e:
            print(logError+f"ошибка в таймере: {e}"+stopColor)

    # Проверка на запрос информации или генерацию изображений
    elif any(keyword in command_text.lower() for keyword in image_keywords):
        threading.Thread(target=generate_image, args=(command_text,)).start()
        return

    elif match:
        topic = match.group(4)
        print(logSystem+f"ищем информацию о '{topic}'"+stopColor)
        answer = ask_main(topic)
        print(logSystem+str(answer)+stopColor)
        speach(answer)
        return
    
    elif re.search(r"(найди информацию|информацию найди|найти|найти о|найди) (.+)", command_text, re.IGNORECASE):
        match = re.search(r"(найди информацию|информацию найди|найти|найти о|найди) (.+)", command_text, re.IGNORECASE)
        topic = match.group(2)
        print(logSystem + f"поиск в браузере по запросу '{topic}'" + stopColor)
        chrome_openUrl(getConfigInfo('main', 'searchSite')+str(topic.replace(' ', '+')))

    elif name_match:
        command_text = name_match.group(2)
        answer = ask_main(command_text)
        print(logSystem+str(answer)+stopColor)
        speach(answer)
        recognizeDiscussion_thread()

    # elif any(re.search(pattern, command_text, re.IGNORECASE) for pattern in download_install_patterns):
    #     match = re.search(r"(скачай|установи) (.+)", command_text, re.IGNORECASE)
    #     if match:
    #         action = match.group(1)
    #         game = match.group(2)
    #         print(logSystem + f"начинаем процесс '{action}' игры '{game}'" + stopColor)
    #         game_install(command_text)
    #         #speach(f"начинаем процесс {action} игры {game}")
    #         return

    for keywords, action in commands.items():
        if all(keyword in command_text.lower() for keyword in keywords):
            thread = threading.Thread(target=action)
            thread.daemon = True
            thread.start()
            play_random_phrase(25)
            return

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

async def telegram_bot():
    print(logSystem + "✓ telegram bot успешно запущен" + stopColor)
    dp.middleware.setup(LoggingMiddleware())

    button_screenshot = KeyboardButton('💻 Скриншот экрана')
    button_lock_pc = KeyboardButton('⚙️ Заблокировать компьютер')
    button_off_mic = KeyboardButton('🎙 Выключить микрофон')
    button_on_mic = KeyboardButton('🎙 Включить микрофон')
    button_reboot_pc = KeyboardButton('🔄 Перезагрузить компьютер')
    button_shutdown_pc = KeyboardButton('🔌 Выключить компьютер')
    button_help = KeyboardButton('☁️ Помощь')

    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(button_screenshot).add(button_off_mic, button_on_mic).add(button_reboot_pc, button_lock_pc, button_shutdown_pc).add(button_help)

    async def check_user(message: types.Message):
        if str(message.from_user.id) != ALLOWED_USER:
            await message.answer("У вас нет доступа к этому боту.")
            return False
        return True

    @dp.message_handler(commands=['start'])
    async def send_welcome(message: types.Message):
        if not await check_user(message):
            return
        with open('assets/banner.png', 'rb') as photo:
            await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=f"<b>☁️ Добро пожаловать.</b>\n\n<i><b>🌐 Я - умный голосовой помощник {nameConfig}</b>, чтобы отправить мне команду просто напишите в чат, то что вы мне отправите будет считываться также, как будто вы сказали это в микрофон.</i>\n\n<b>⏳ Выбирите действие:</b>", reply_markup=markup, parse_mode=types.ParseMode.HTML)

    @dp.message_handler(lambda message: message.text == '💻 Скриншот экрана')
    async def screenshot_handler(message: types.Message):
        if not await check_user(message):
            return
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        await message.answer_photo(photo=open("screenshot.png", 'rb'))
        os.remove("screenshot.png")


    @dp.message_handler(lambda message: message.text == '⚙️ Заблокировать компьютер')
    async def lock_pc_handler(message: types.Message):
        if not await check_user(message):
            return
        if os.name == 'nt':
            os.system('rundll32.exe user32.dll,LockWorkStation')
            await message.answer("<b>☁️ Компьютер успешно заблокирован.</b>",  parse_mode=types.ParseMode.HTML)
        else:
            os.system('gnome-screensaver-command -l')

    @dp.message_handler(lambda message: message.text == '🎙 Выключить микрофон')
    async def off_mic_handler(message: types.Message):
        if not await check_user(message):
            return
        updateConfigname("utils/config.json", getConfigInfo('microphone', 'disabled'), "mic_index", "other")
        updateConfigname("utils/config.json", 'True', "mic_id", "other")
        updateConfigname("utils/config.json", 1, "timeout", "other")
        await message.answer("<b>🎙 Микрофон был выключен</b>",  parse_mode=types.ParseMode.HTML)

    @dp.message_handler(lambda message: message.text == '🎙 Включить микрофон')
    async def on_mic_handler(message: types.Message):
        if not await check_user(message):
            return
        updateConfigname("utils/config.json", getConfigInfo('microphone', 'active'), "mic_index", "other")
        updateConfigname("utils/config.json", 'False', "mic_id", "other")
        updateConfigname("utils/config.json", 30, "timeout", "other")
        await message.answer("<b>🎙 Микрофон был включен</b>",  parse_mode=types.ParseMode.HTML)

    @dp.message_handler(lambda message: message.text == '🔄 Перезагрузить компьютер')
    async def reboot_pc_handler(message: types.Message):
        if not await check_user(message):
            return
        if os.name == 'nt':
            os.system('shutdown /r /t 0')
        else:
            os.system('sudo reboot')
        await message.answer("<b>🔄 Компьютер перезагружается.</b>", parse_mode=types.ParseMode.HTML)

    @dp.message_handler(lambda message: message.text == '🔌 Выключить компьютер')
    async def shutdown_pc_handler(message: types.Message):
        if not await check_user(message):
            return
        if os.name == 'nt':
            os.system('shutdown /s /t 0')
        else:
            os.system('sudo shutdown now')
        await message.answer("<b>🔌 Компьютер выключается.</b>", parse_mode=types.ParseMode.HTML)

    @dp.message_handler(lambda message: message.text == 'протокол 11')
    async def protocol_11_handler(message: types.Message, state: FSMContext):
        if not await check_user(message):
            return
        await message.answer("Пожалуйста, введите код доступа:")
        await Protocol11States.waiting_for_code.set()

    @dp.message_handler(state=Protocol11States.waiting_for_code, content_types=types.ContentTypes.TEXT)
    async def access_code_handler(message: types.Message, state: FSMContext):
        if message.text == getConfigInfo('protocols', 'code_protocol_11'):
            await message.answer("<b>☁️ Код доступа принят.</b> <i>Выполняется команда по уничтожению компьютера.\n\n<b>🔌 Надеюсь вы успели сохранить свои данные :)</b></i>", parse_mode=types.ParseMode.HTML)
            code = getConfigInfo('protocols', 'code_protocol_11')
            protocol_11(code)
            await message.answer("<b>☁️ Команда выполнена.</b>", parse_mode=types.ParseMode.HTML)
            await state.finish()
        else:
            await message.answer("<b>☁️ Неверный код доступа. Попробуйте снова.</b>", parse_mode=types.ParseMode.HTML)
    
    @dp.message_handler(lambda message: message.text == '☁️ Помощь')
    async def off_mic_handler(message: types.Message):
        if not await check_user(message):
            return
        with open('assets/help.png', 'rb') as photo:
            await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=f"<b>☁️ Помощь</b>\n\n⚙️ Тут вы можете понять как начать управлять ассистентом и увидеть примеры команд\n\n<b>🔌 Список того что я умею:</b>\n<i>— очистка корзины\n— октрытие 150+ программ\n— открытие вк, ютуба, лолза, яндекса, гугла, твиттера, фейсбука, инстаграм\n— включение музыки на фон\n— игровой режим\n— включение игр\n— создание картинок\n— поставить таймер\n— ответ на любой вопрос\n— погода\n— последние новости\n— управление звуком\n— управление браузером\n— управление wireguard\n— заметки\n— переключение расскладки компьютера\n— написание контактам в телеграм\n— конструктор команд\n— управление компьютером\n\n</i><b>🔌 Протоколы:</b><i>\n— протокол 11 (полное удаление всех файлов с компьютера)</i>\n\n<b>🔌 Примеры команд:\n</b><i>— (найди информацию|информацию найди|найти|найти о|найди) (.+) - поиск в браузере\n— (напиши|отпиши) ([^ ]+) (.+) - отправка сообщений в телеграм\n— (включи|запусти|сделай|поставь) таймер на (.+) - таймер на определенное время (секунд, минут, дней, часов)</i>", reply_markup=markup, parse_mode=types.ParseMode.HTML)
        #await message.answer("<b>☁️ Помощь</b>\n\n<b>🔌 Список того что я умею:</b>\n<i>— очистка корзины\n— октрытие 150+ программ\n— открытие вк, ютуба, лолза, яндекса, гугла, твиттера, фейсбука, инстаграм\n— включение музыки на фон\n— игровой режим\n— включение игр\n— создание картинок\n— поставить таймер\n— ответ на любой вопрос\n— погода\n— последние новости\n— управление звуком\n— управление браузером\n— управление wireguard\n— заметки\n— переключение расскладки компьютера\n— написание контактам в телеграм\n— конструктор команд\n— управление компьютером\n\n</i><b>🔌 Протаколы:</b><i>\n— протокол 11 (полное удаление всех файлов с компьютера)</i>",  parse_mode=types.ParseMode.HTML)

    @dp.message_handler()
    async def echo(message: types.Message):
        if not await check_user(message):
            return
        await message.answer(f"<b>☁️ Команда успешно выполнена.</b>", parse_mode=types.ParseMode.HTML)
        process_command(message.text)

    await dp.start_polling()

def run_telegram_bot():
    asyncio.run(telegram_bot())

LIGHT_SEED_COLOR = colors.DEEP_ORANGE
DARK_SEED_COLOR = colors.DEEP_PURPLE_200

cmd = TextField(
    label="CMD",
    multiline=True,
    min_lines=1,
    max_lines=10,
    read_only=True
)

def main(page: Page):

    def erorrBanner(erorr):
        page.banner = Banner(
            bgcolor=colors.AMBER_100,
            leading=Icon(
                icons.WARNING_AMBER_ROUNDED, 
                color=colors.AMBER, 
                size=55
            ),
            content=Text(
                f"Oops, there were some errors {erorr}", 
                size=20, 
                color=flet.colors.BLACK26
            ),
            actions=[
                ElevatedButton(
                    "Retry", 
                    on_click=close_banner, 
                    bgcolor=flet.colors.AMBER_100,
                    color=flet.colors.BLACK26
                ),
                ElevatedButton(
                    "Ignore", 
                    on_click=close_banner, 
                    bgcolor=flet.colors.AMBER_100,
                    color=flet.colors.BLACK26
                ),
                ElevatedButton(
                    "Cancel", 
                    on_click=close_banner, 
                    bgcolor=flet.colors.AMBER_100,
                    color=flet.colors.BLACK26
                ),
            ],
        )
        page.banner.open = True
        page.update()
        #print(erorr)

    API_KEY_WEATHER = 'db986886bc22744d4dbb14d5af5308f3'

    def get_weather_data(city, lang='ru'):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY_WEATHER}&units=metric&lang={lang}"
        response = requests.get(url)
        return response.json()

    
    def get_temperature(city):
        try:
            data = get_weather_data(city)
            return data['main']['temp']
        except Exception as e:
            erorrBanner('Введите ваш город в настройках или в конфиге')
            print(logError+f'Ошибка в модуле виджета температур :: {e}')

    def get_precipitation_probability(city):
        try:
            data = get_weather_data(city)
            if 'rain' in data:
                return data['rain']['1h'] if '1h' in data['rain'] else data['rain']['3h']
            elif 'snow' in data:
                return data['snow']['1h'] if '1h' in data['snow'] else data['snow']['3h']
            else:
                return 0 
        except Exception as e:
            erorrBanner('Введите ваш город в настройках или в конфиге')
            print(logError+f'Ошибка в модуле виджета температур :: {e}')

    def get_humidity(city):
        try:
            data = get_weather_data(city)
            return data['main']['humidity']
        except Exception as e:
            erorrBanner('Введите ваш город в настройках или в конфиге')
            print(logError+f'Ошибка в модуле виджета температур :: {e}')

    def get_wind(city):
        try:
            data = get_weather_data(city)
            return data['wind']['speed']
        except Exception as e:
            erorrBanner('Введите ваш город в настройках или в конфиге')
            print(logError+f'Ошибка в модуле виджета температур :: {e}')

    def get_precipitation(city):
        try:     
            data = get_weather_data(city)
            if 'rain' in data:
                return data['rain']['1h'] if '1h' in data['rain'] else data['rain']['3h']
            elif 'snow' in data:
                return data['snow']['1h'] if '1h' in data['snow'] else data['snow']['3h']
            else:
                return 0 
        except Exception as e:
            erorrBanner('Введите ваш город в настройках или в конфиге')
            print(logError+f'Ошибка в модуле виджета температур :: {e}')

    def on_close(e):
        keyboard.press('win+alt+break')
    
    page.on_window_close = on_close
    city = getConfigInfo('main', 'city')

    infoComputer = flet.Text('info lol', size=15)

    page.title = "Voice assistant"

    page.theme_mode = "dark"
    page.theme = theme.Theme(color_scheme_seed=LIGHT_SEED_COLOR, use_material3=True)
    page.dark_theme = theme.Theme(color_scheme_seed=DARK_SEED_COLOR, use_material3=True)

    page.window_maximizable = False

    page.window_width = 1350
    page.window_height = 700

    page.window_max_width = 1520 ; page.window_min_width = 1350
    page.window_max_height = 720 ; page.window_min_height = 700
    page.update()

    temperature_text = ft.Text(
        value=f'{get_temperature(city)}°C',
        size=50,
        weight=ft.FontWeight.BOLD
    )
    precipitation_text = ft.Text(
            value=f'вероятность осадков: {get_precipitation_probability(city)}%',
            size=14,
            weight=ft.FontWeight.W_500
        )

    humidity_text = ft.Text(
            value=f'влажность: {get_humidity(city)}%',
            size=14,
            weight=ft.FontWeight.W_500
        )

    wind_text = ft.Text(
            value=f'ветер: {get_wind(city)} м/с',
            size=14,
            weight=ft.FontWeight.W_500
        )

    divider_text = ft.Text(
            value='―――――',
            size=14,
            weight=ft.FontWeight.W_500
        )

    falling_text = ft.Text(
            value='осадки',
            size=14,
            weight=ft.FontWeight.W_500
        )

    def update_color():
        if page.theme_mode == 'dark':
            temperature_text.color = ft.colors.WHITE
            precipitation_text.color = ft.colors.WHITE
            humidity_text.color = ft.colors.WHITE
            wind_text.color = ft.colors.WHITE
            divider_text.color = ft.colors.WHITE
            falling_text.color = ft.colors.WHITE
        else:
            temperature_text.color = ft.colors.BLUE_900
            precipitation_text.color = ft.colors.BLUE_900
            humidity_text.color = ft.colors.BLUE_900
            wind_text.color = ft.colors.BLUE_900
            divider_text.color = ft.colors.BLUE_900
            falling_text.color = ft.colors.BLUE_900
        page.update()

    def toggle_theme_mode(e):
        try:
            page.theme_mode = "dark" if page.theme_mode == "light" else "light"
            lightMode.icon = (
                icons.WB_SUNNY_OUTLINED if page.theme_mode == "light" else icons.WB_SUNNY
            )
            update_color()
            page.update()
        except Exception as e:
            erorrBanner(e)

    def get_exchange_rate_data():
        url = "https://api.coingecko.com/api/v3/coins/tether/market_chart"
        params = {
            "vs_currency": "rub",
            "days": "30", 
            "interval": "daily"
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        exchange_rate_data = []
        for item in data["prices"]:
            date = datetime.datetime.fromtimestamp(item[0] / 1000).strftime('%Y-%m-%d')
            rate = round(item[1], 2)
            exchange_rate_data.append({"date": date, "rate": rate})
        
        return exchange_rate_data
    
    exchange_rate_data = get_exchange_rate_data()

    dates = [datetime.datetime.strptime(item["date"], "%Y-%m-%d").date() for item in exchange_rate_data]
    rates = [item["rate"] for item in exchange_rate_data]

    data_series = [
        ft.LineChartData(
            data_points=[ft.LineChartDataPoint(x, y) for x, y in enumerate(rates)],
            stroke_width=4,
            color=ft.colors.LIGHT_GREEN,
            curved=True,
            stroke_cap_round=True,
        )
    ]

    chart = ft.LineChart(
        data_series=data_series,
        border=ft.Border(
            bottom=ft.BorderSide(4, ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))
        ),
        left_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=i,
                    label=ft.Text(str(round(rate, 2)), size=14, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400),
                ) for i, rate in enumerate(rates[::len(rates)//6])
            ],
            labels_size=40,
        ),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=i,
                    label=ft.Container(
                        ft.Text(
                            dates[i].strftime("%b %d"),
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                        ),
                        margin=ft.margin.only(top=10),
                    ),
                ) for i in range(0, len(dates), len(dates)//6)
            ],
            labels_size=32,
        ),
        tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
        min_y=min(rates) - 1,
        max_y=max(rates) + 1,
        min_x=0,
        max_x=len(rates) - 1,
        expand=True,
    )

    info_row = ft.Row(
        controls=[
            ft.Icon(
                name=ft.icons.STAR_BORDER,
                size=40
            ),
            ft.Text(
                value=f'CONSOLE LOGS',
                weight=ft.FontWeight.BOLD,
                size=18
            ),
        ]
    )

    cmd_info = ft.ListView(
        controls=[
            info_row
        ],
        padding=ft.padding.all(15),
        spacing=10,
        auto_scroll=True
    )

    def add_cmd_info(who, values):
        if who == 'user':
            cmd_info.controls.append(
                ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.CIRCLE,
                            size=10,
                            color=ft.colors.GREEN_400
                        ),
                        ft.Text(
                            value=f'{values}',
                            weight=ft.FontWeight.W_500,
                            size=15,
                            color=ft.colors.GREEN_400
                        )
                    ],
                    spacing=10
                )
            )
        else:
            cmd_info.controls.append(
                ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.CIRCLE,
                            size=10,
                            color=ft.colors.PURPLE_400
                        ),
                        ft.Text(
                            value=f'{values}',
                            weight=ft.FontWeight.W_500,
                            size=15,
                            color=ft.colors.PURPLE_400
                        )
                    ],
                    spacing=10
                )
            )

    cmd = ft.Container(
        cmd_info,
        expand=True,
        border=ft.border.all(1),
        border_radius=30
    )

    command_list = ft.ListView(
        controls=[
            ft.Container(
                ft.ExpansionPanelList(
                    expand_icon_color=ft.colors.GREEN_300,
                    elevation=8,
                    controls=[
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='очистка корзины',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам: (о/по/от)чисти, корзину',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                            expanded=True
                        ),
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='открытие программ',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам: (открой/включи), <назавание программы>',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_ACCENT_700
                                                ),
                                                ft.Text(
                                                    value='Информация: команда может быть любой сделаной вами',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                        ),
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='открытие вебсайтов',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам: (открой), <назавание сайта>',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_ACCENT_700
                                                ),
                                                ft.Text(
                                                    value='Информация: команда может быть любой сделаной вами',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                        ),
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='включение музыки на фон',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам: включи, музыку, на, фон',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_ACCENT_700
                                                ),
                                                ft.Text(
                                                    value='Информация: команда может быть любой сделаной вами',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                        ),
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='игровой режим',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам: (запусти/включи) игровой режим',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                        ),
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='включение игр',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам: (октрой/запусти) <название>',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_ACCENT_700
                                                ),
                                                ft.Text(
                                                    value='Информация: команда может быть любой сделаной вами',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                        ),
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='таймер',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам:\n(включи|запусти|сделай|поставь) таймер на (.+)',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                        ),
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='ответ на любой вопрос',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам: <Имя асситента> вопрос\nдальше будет диалог, его можно завершить,\nпопросив об этом ассистента',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_ACCENT_700
                                                ),
                                                ft.Text(
                                                    value='Информация: Завершить диалог можно\nлюбой понятной фразой завершения',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                        ),
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='погода',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам: какая сейчас\nпогода в <город>',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                        ),
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='последние новости',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам: новости, сейчас, последние',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                        ),
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='управление звуком',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам: громкость, на, максимум\nсделай, звук, тише, громче, снизь, понизь, увеличь\nгромкость, на, всю',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                        ),
                        ft.ExpansionPanel(
                            header=ft.Container(
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.BOLT_OUTLINED,
                                            size=20,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='написание контактам в телеграм',
                                            weight=ft.FontWeight.W_500,
                                            size=15,
                                        ),
                                    ]
                                ),
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=15)
                            ),
                            content=ft.Container(
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_300
                                                ),
                                                ft.Text(
                                                    value='активация команды по словам: (от)напиши <имя> <фраза>',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    name=ft.icons.CIRCLE,
                                                    size=10,
                                                    color=ft.colors.GREEN_ACCENT_700
                                                ),
                                                ft.Text(
                                                    value='Информация: Важно нужен telegram.session\nфайл в папке /session чтобы функция работала',
                                                    weight=ft.FontWeight.W_500,
                                                    size=12,
                                                ),
                                            ],
                                            spacing=10
                                        )
                                    ]
                                ),
                                padding=ft.padding.all(15)
                            ),
                        ),
                    ]
                ),
                border_radius=30,
                width=350,
                border=ft.border.all(2, color=ft.colors.WHITE24)
            )
        ]
    )

    def weather_info(city):
        temperature_text = ft.Text(
            value=f'{get_temperature(city)}°C',
            size=50,
            weight=ft.FontWeight.BOLD
        )
        precipitation_text = ft.Text(
            value=f'вероятность осадков: {get_precipitation_probability(city)}%',
            size=14,
            weight=ft.FontWeight.W_500
        )

        humidity_text = ft.Text(
            value=f'влажность: {get_humidity(city)}%',
            size=14,
            weight=ft.FontWeight.W_500
        )

        wind_text = ft.Text(
            value=f'ветер: {get_wind(city)} м/с',
            size=14,
            weight=ft.FontWeight.W_500
        )

        divider_text = ft.Text(
            value='―――――',
            size=14,
            weight=ft.FontWeight.W_500
        )

        falling_text = ft.Text(
            value='осадки',
            size=14,
            weight=ft.FontWeight.W_500
        )
        return ft.Stack(
            [
                ft.Container(
                    content=ft.Icon(
                        name=ft.icons.TERRAIN,
                        size=280,
                        color=ft.colors.BLUE_300,
                        opacity=0.3
                    ),
                    alignment=ft.alignment.bottom_left,
                    padding=ft.padding.only(left=10)
                ),
                ft.Container(
                    content=ft.Text(
                        value=f'{city}',
                        weight=ft.FontWeight.BOLD,
                        size=18
                    ),
                    alignment=ft.alignment.bottom_left,
                    padding=ft.padding.all(10)
                ),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Container(
                                    temperature_text,
                                    padding=ft.padding.only(left=10)
                                ),
                            ],
                        ),
                        ft.Column(
                            controls=[
                                ft.Container(
                                    precipitation_text,
                                    padding=ft.padding.only(top=20)
                                ),
                                ft.Container(
                                    humidity_text
                                ),
                                ft.Container(
                                    wind_text
                                ),
                                ft.Divider(),
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Container(
                                                divider_text
                                            ),
                                            ft.Container(
                                                ft.Icon(
                                                    name=icons.WATER_DROP_OUTLINED,
                                                    color=ft.colors.BLUE_300,
                                                    scale=4
                                                ),
                                                padding=ft.padding.only(left=30)
                                            )
                                        ]
                                    )
                                ),
                                ft.Container(
                                    falling_text,
                                    padding=ft.padding.only(left=10, bottom=10)
                                ),
                            ],
                            spacing=10
                        ),
                    ],
                    spacing=40
                ),
            ]
    )

    widgets = ft.Row(
        controls=[
            ft.Container(
                content=weather_info(city),
                expand=True,
                border=ft.border.all(1, color=ft.colors.BLUE_900),
                border_radius=30,
            ),
            ft.Container(
                content=command_list,
                expand=True,
                border=ft.border.all(1, color=ft.colors.GREEN_300),
                border_radius=30
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    name=ft.icons.ATTACH_MONEY,
                                    size=15,
                                    color=ft.colors.GREEN_300
                                ),
                                ft.Text(
                                    value='USD TO RUB',
                                    weight=ft.FontWeight.W_500,
                                    size=12,
                                ),
                            ],
                            spacing=10,
                        ),
                        chart
                    ]
                ),
                expand=True,
                border=ft.border.all(1, color=ft.colors.GREEN_300),
                border_radius=30,
                padding=ft.padding.all(15)
            ),
        ],
        spacing=10,
        height=200
    )

    lightMode = IconButton(
        icons.WB_SUNNY_OUTLINED if page.theme_mode == "light" else icons.WB_SUNNY,
        on_click=toggle_theme_mode,
    )

    def check_item_clicked(e):
        e.control.checked = not e.control.checked
        if e.control.checked == True:
            updateConfigname("utils/config.json", 'True', "FullLogs", "settings")
            page.update()
        elif e.control.checked == False:
            updateConfigname("utils/config.json", 'False', "FullLogs", "settings")
            page.update()
    def mic_use(e):
        try:
            e.control.selected = not e.control.selected
            if e.control.selected == True:
                updateConfigname("utils/config.json", getConfigInfo('microphone', 'disabled'), "mic_index", "other")
                updateConfigname("utils/config.json", 'True', "mic_id", "other")
                updateConfigname("utils/config.json", 1, "timeout", "other")
            if e.control.selected == False:
                updateConfigname("utils/config.json", getConfigInfo('microphone', 'active'), "mic_index", "other")
                updateConfigname("utils/config.json", 'False', "mic_id", "other")
                updateConfigname("utils/config.json", 30, "timeout", "other")
            e.control.update()
        except Exception as e:
            erorrBanner(e)
        

    def close_dlg(e):
        try:
            DialogProtocols.open = False
            page.update()
        except Exception as e:
            erorrBanner(e)

    def close_dlgInfo(e):
        try:
            DialogInfo.open = False
            page.update()
        except Exception as e:
            erorrBanner(e)

    def close_dlgReboot(e):
        DLGrebootAssistant.open = False
        page.update()
        
    DLGrebootAssistant = flet.AlertDialog(
        modal=True,
        title=flet.Text("Please confirm"),
        content=flet.Text("Do you really want to reboot assistant?"),
        actions=[
            flet.TextButton(
                "Yes", 
                on_click=close_dlgReboot
            ),
            flet.TextButton(
                "No", 
                on_click=close_dlgReboot
            ),
        ],
        actions_alignment=flet.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )

    def open_dlgReboot(e):
        page.dialog = DLGrebootAssistant
        DLGrebootAssistant.open = True
        page.update()

    DialogProtocols = flet.AlertDialog(
        modal=True,
        title=flet.Row(
            controls=[
                Icon(
                    name=flet.icons.SETTINGS, 
                    
                    size=25
                ), 
                flet.Text(
                    "All protocols", 
                    size=25
                )
            ]
        ),
        content=flet.Text(
            "• Protocol 21 (Make backup on server)\n• Protocol 11 (delete all from computer)",
            size=20
        ),
        actions=[
            flet.TextButton(
                "Close", 
                on_click=close_dlg
            ),
        ],
        actions_alignment=flet.MainAxisAlignment.END,
    )

    DialogInfo = flet.AlertDialog(
        modal=True,
        title=flet.Row(
            controls=[
                Icon(
                    name=flet.icons.SETTINGS, 
                    
                    size=20
                ), 
                flet.Text(
                    "Main info", 
                    size=25
                )
            ]
        ),
        content=infoComputer,
        actions=[
            flet.TextButton(
                "Close", 
                on_click=close_dlgInfo
            ),
        ],
        actions_alignment=flet.MainAxisAlignment.END,
    )

    def open_dlg(e):
        try:
            page.dialog = DialogProtocols
            DialogProtocols.open = True
            page.update()
        except Exception as e:
            erorrBanner(e)

    def open_dlgInfo():
        try:
            page.dialog = DialogInfo
            DialogInfo.open = True
            while True:
                infoComputer.value = system_info()
                page.update()
                time.sleep(1)
        except Exception as e:
            erorrBanner(e)

    def open_dlgInfo_thread():
        thread = threading.Thread(target=open_dlgInfo, args=())
        thread.daemon = True
        thread.start()

    settingsShow = IconButton(icon=icons.ADD_MODERATOR, on_click=open_dlg)
    page.padding = 30

    def switchwork(e):
        startWorkSwitch.disabled = True
        startWorkAI(1)

    startWorkSwitch = ft.Switch(
        value=False,
        inactive_thumb_color=ft.colors.GREEN_400,
        inactive_track_color=ft.colors.GREEN_100,
        active_color=ft.colors.GREEN_400,
        active_track_color=ft.colors.GREEN_100,
        on_change=switchwork
    )

    page.appbar = AppBar(
        leading=Icon(icons.ACCOUNT_CIRCLE),
        leading_width=60,
        title=ft.Container(
            ft.Row(
                controls=[
                    Text(f"Voice assistant"),
                    ft.Container(
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    name=ft.icons.HELP,
                                    size=25,
                                    color=ft.colors.GREEN_300
                                ),
                                ft.Text(
                                    value='Start assistant',
                                    weight=ft.FontWeight.W_500,
                                    size=20,
                                ),
                                startWorkSwitch 
                            ]
                        ),
                        padding=ft.padding.only(left=350)
                    )
                ],
                spacing=10
            ),
            expand=True
        ),
        center_title=False,
        actions=[
            lightMode,
            settingsShow,
            PopupMenuButton(
                items=[
                    PopupMenuItem(
                        icon=icons.INFO, 
                        text="Show config", 
                        on_click=lambda _:open_program('utils\\config.json')
                    ),
                    PopupMenuItem(
                        content=Row(
                            [
                                Icon(icons.HOURGLASS_TOP_OUTLINED),
                                Text("System info"),
                            ]
                        ),
                        on_click=lambda _: open_dlgInfo_thread(),
                    ),
                    PopupMenuItem(),
                    PopupMenuItem(
                        text="Show logs", 
                        checked=getConfigInfo("settings", 'FullLogs'), 
                        on_click=check_item_clicked
                    ),
                ]
            ),
        ],
    )

    lastSettings = flet.Row(controls=[
        IconButton(
            icon=icons.AUTORENEW,
            icon_size=40,
            #on_click=open_dlgReboot,
            selected=False,
            disabled=True,
            tooltip="Disabled, function not maked right now"),
        IconButton(
            icon=flet.icons.MIC,
            selected_icon=flet.icons.MIC_OFF,
            icon_size=40,
            on_click=mic_use,
            selected=getConfigInfo('other', 'mic_id'),
        ),

        ],
        alignment=flet.MainAxisAlignment.CENTER
    )

    def startWorkAI(e):
        from modules.other import show_current_datetime
        
        startWorkButton.disabled = True
        show_banner(1)
        cmd_info.controls.append(
            ft.Text(successApp+show_current_datetime())
        )
        if show_mic == "True":
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(logSystem+f"Микрофон с индексом {index}: {name}"+stopColor)
        if voiceLoging == "True":
            speach_recognized_thread(recognized_phrases)
        if check_screen == "True":
            recordScreen_thread()
        page.update()

        moveDeleteFile_thread("telegram_history.json", 1800)
        moveDeleteFile_thread("chat_history.json", 86400)

        print(success+show_current_datetime())
        print(logInfo+f"✓ Configuration.\n"+logInfo+f"Version app :: {versionConfig}     | Name voice support :: {getConfigInfo('main', 'name')}\n"+logInfo+f"CheckScreen :: {check_screenConfig}    | CheckCamera :: {check_cameraConfig}\n"+logInfo+f"Microphone index :: {mic_indexConfig}  | Microphones show :: {show_micConfig}\n"+logInfo+f"Voice loging :: {voiceLogingConfig}   | FullLogs :: {FullLogsConfig}\n\n"+logInfo+f"Protocol 21 :: {protocols21}    | :: ")
        cmd_info.controls.append(
            ft.Text(logInfoApp+f"Configuration.\n"+logInfoApp+f"Version app :: {versionConfig}     | Name voice support :: {getConfigInfo('main', 'name')}\n"+logInfoApp+f"CheckScreen :: {check_screenConfig}    | CheckCamera :: {check_cameraConfig}\n"+logInfoApp+f"Microphone index :: {mic_indexConfig}  | Microphones show :: {show_micConfig}\n"+logInfoApp+f"Voice loging :: {voiceLogingConfig}   | FullLogs :: {FullLogsConfig}\n\n"+logInfoApp+f"Protocol 21 :: {protocols21}    | :: ")
        )
        page.update()
        if protocols21 == "True":
            print(logSystem+'✓ протокол 21 был успешно запущен'+stopColor+show_current_datetime())
            Protocol21Thread()
        telegram_contacts_thread()
        bot_thread = threading.Thread(target=run_telegram_bot)
        bot_thread.daemon = True
        bot_thread.start()
        cmd_info.controls.append(
            ft.Text('✓ протокол 21 был успешно запущен'+show_current_datetime())
        )
        page.update()

        if getConfigInfo('main', 'recogniz') == "vosk":
            def Vosklisten():
                if getConfigInfo('vosk', 'model') == 'small_ru':
                    model = vosk.Model(lang="ru")
                elif getConfigInfo('vosk', 'model') == 'big_ru':
                    model = vosk.Model('modules/voice/vosk-model-ru-0.42')
                samplerate = 16000
                device = getConfigInfo('other', 'mic_index')
                with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device, dtype='int16', channels=1, callback=q_callback):
                    try:
                        print(logUser+"прослушиваю микрофон"+stopColor)
                        rec = vosk.KaldiRecognizer(model, samplerate)
                        while True:
                            #cmd.value = cmd.value+'\n'+logUserApp+"прослушиваю микрофон"
                            data = q.get()
                            if rec.AcceptWaveform(data):
                                if getConfigInfo('other', 'mic_index') == 2:
                                    text = json.loads(rec.Result())["text"]
                                    if text == "":
                                        pass
                                        
                                    else:
                                        saveTextfile('logs.txt', text, True)
                                        print(logUser+f"вы сказали :: {text}"+stopColor) ; recognized_phrases.append(text)
                                        cmd_info.controls.append(
                                            ft.Text(f'{logUserApp}+"вы сказали :: " + {text}'+show_current_datetime())
                                        )
                                        page.update()
                                        process_command(text)

                    except Exception as e:
                        print(e)
            Vosklisten()
        if getConfigInfo('main', 'recogniz') == "speach_recognize":
            async def recognize_speech():
                from modules.chatgpt import chatWithImage
                recognizer = sr.Recognizer()
                while True:
                    with sr.Microphone(device_index=getConfigInfo('other', 'mic_index')) as source:
                        try:
                            cmd_info.controls.append(
                                ft.Text(logSystemApp+'прослушиваю микрофон' + show_current_datetime())
                            )
                            print(logSystem+"прослушиваю микрофон" + show_current_datetime())
                            page.update()
                            recognizer.adjust_for_ambient_noise(source)
                            audio = recognizer.listen(source, timeout=getConfigInfo('other', 'timeout'))

                            text = recognizer.recognize_google(audio, language="ru-RU")

                            try:

                                saveTextfile('logs.txt', text, True)
                                print(logSystem+"вы сказали :: " + text + show_current_datetime())
                                recognized_phrases.append(text)
                                cmd_info.controls.append(
                                    ft.Text(f'{logUserApp}+"вы сказали :: " + {text}'+show_current_datetime())
                                )
                                page.update()

                                def get():
                                    answer = chatWithImage(text)
                                    if answer != "Answ0x01":
                                        answerPathIMAGE(answer, all_paths)
                                if getConfigInfo('main', "chatgpt") == 'gpt-4o':
                                    thread = threading.Thread(target=get, args=())
                                    thread.daemon = True
                                    thread.start()

                                process_command(text)
                            except Exception as e:
                                pass

                        except sr.UnknownValueError:
                            if FullLogsConfig == "True":
                                print(logError+"извините, не удалось распознать речь" + show_current_datetime())
                            else:
                                pass
                        except sr.RequestError as e:
                            print(logError+f"ошибка сервиса распознавания речи: {e}" + show_current_datetime())
                        except sr.WaitTimeoutError:
                            if getConfigInfo('other', 'timeoutLogs') == "False":
                                pass
                            else:
                                print(logError+f"прошла 1 секунда, но звук не обнаружен." + show_current_datetime())

            asyncio.run(recognize_speech())
        
    page.fonts = {
            "Crushed": "https://github.com/google/fonts/raw/main/apache/crushed/Crushed-Regular.ttf"
        }
    def changedName(e):
        updateConfigname("utils/config.json", e.control.value, "name", "main")
        page.update()

    def changedGPT(e):
        updateConfigname("utils/config.json", e.control.value, "chatgpt", "main")
        page.update()

    def changedCity(e):
        updateConfigname("utils/config.json", e.control.value, "city", "main")
        page.update()

    def changedTelegramToken(e):
        updateConfigname("utils/config.json", e.control.value, "API_TOKEN", "telegram")
        page.update()

    def changedTelegramId(e):
        updateConfigname("utils/config.json", e.control.value, "ALLOWED_USER", "telegram")
        page.update()

    nameConfig = TextField(
        label="Name assistant", 
        value=getConfigInfo('main', 'name'), 
        width=250, 
        height=90, 
        hint_text="Type assistante name please", 
        on_change=changedName)
    chatGPT_Version = TextField(
        label="Chat gpt version", 
        value=getConfigInfo('main', 'chatgpt'), 
        width=250, 
        height=90, 
        hint_text="Type chatgpt version", 
        on_change=changedGPT)
    
    CityChange = TextField(
        label="Your City", 
        value=getConfigInfo('main', 'city'), 
        width=250, 
        height=90, 
        hint_text="Type your city", 
        on_change=changedCity)
    
    TelegramTokenChange = TextField(
        label="Your bot token telegram", 
        value=getConfigInfo('telegram', 'API_TOKEN'), 
        width=250, 
        height=90, 
        hint_text="Type your bot token telegram", 
        on_change=changedTelegramToken)
    
    TelegramUserChange = TextField(
        label="Your telegram id", 
        value=getConfigInfo('telegram', 'ALLOWED_USER'), 
        width=250, 
        height=90, 
        hint_text="Type your id telegram", 
        on_change=changedCity)

    settingsBar1 = flet.Row(
        controls=[
            Icon(
                name=flet.icons.SETTINGS, 
                
                size=30
            ), 
            Text(
                "Settings",
                font_family="RobotoSlab", 
                style="displayLarge", 
                size=30
            )
        ], 
        alignment=flet.MainAxisAlignment.CENTER)

    settingsBar2 = flet.Row(
        controls=[
            autoloadCheckbox,
            accessToScreenCheckbox,
            accessToCameraCheckbox,
            voiceLogsCheckbox,
            timeoutLogsCheckbox,
            ShowMicIndexCheckbox
        ], 
        spacing=10,
        alignment=flet.MainAxisAlignment.CENTER,
    )

    settingsBar3 = flet.Row(
        controls=[
            nameConfig, 
            chatGPT_Version,
            CityChange,
            TelegramTokenChange,
            TelegramUserChange
        ],
        spacing=10, 
        alignment=flet.MainAxisAlignment.CENTER) 
       
    startWorkButton = ElevatedButton(
        "Start work", 
        disabled=False, 
        on_click=startWorkAI)

    def change_content(e):

        page.controls.clear()
        nav_dest = e.control.selected_index 

        if nav_dest == 0:
            city = getConfigInfo('main', 'city')

            widgets = ft.Row(
                controls=[
                    ft.Container(
                        content=weather_info(city),
                        expand=True,
                        border=ft.border.all(1, color=ft.colors.BLUE_900),
                        border_radius=30,
                    ),
                    ft.Container(
                        content=command_list,
                        expand=True,
                        border=ft.border.all(1, color=ft.colors.GREEN_300),
                        border_radius=30
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(
                                            name=ft.icons.ATTACH_MONEY,
                                            size=15,
                                            color=ft.colors.GREEN_300
                                        ),
                                        ft.Text(
                                            value='USD TO RUB',
                                            weight=ft.FontWeight.W_500,
                                            size=12,
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                chart
                            ]
                        ),
                        expand=True,
                        border=ft.border.all(1),
                        border_radius=30,
                        padding=ft.padding.all(15)
                    ),
                ],
                spacing=10,
                height=200
            )
            page.add(cmd)
            page.add(widgets)
            update_color()

        if nav_dest == 2:
            page.add(settingsBar1)
            page.add(settingsBar2)
            page.add(settingsBar3)
            page.add(flet.Text(), flet.Text(), flet.Text(), flet.Text(), flet.Text(), flet.Text(), flet.Text(), flet.Text())
            page.add(lastSettings)
            page.update()
        
        if nav_dest == 3:
            infoBar1 = flet.Row(
                controls=[
                    Icon(
                        name=flet.icons.INFO, 
                        
                        scale=1.2
                    ), 
                    flet.Text(
                        f"Count all downloaded modules: {countModules()}", 
                        scale=1.2
                    )
                ], 
                spacing=40
            )
            infoBar2 = flet.Row(
                controls=[
                    Icon(
                        name=flet.icons.INFO, 
                        
                        scale=1.2
                    ), 
                    flet.Text(
                        f"Count all functions in modules: {countFunctions()}", 
                        scale=1.2
                    )
                ], 
                spacing=40
            )
            infoBar3 = flet.Row(
                controls=[
                    Icon(
                        name=flet.icons.INFO, 
                        
                        scale=1.2
                    ), 
                    flet.Text(
                        f"Count all active commands: {count_commands()}", 
                        scale=1.2
                    )
                ], 
                spacing=40
            )
            infoBar4 = flet.Row(
                controls=[
                    Icon(
                        name=flet.icons.INFO, 
                        
                        scale=1.2
                    ), 
                    flet.Text(
                        f"Count all diologs with ai: {countJson('chat_history.json')}", 
                        scale=1.2
                    )
                ], 
                spacing=40
            )
            infoBar5 = flet.Row(
                controls=[
                    Icon(
                        name=flet.icons.INFO, 
                        
                        scale=1.2
                    ), 
                    flet.Text(
                        f"Count all diologs with ai (time history): {countJson('time_history.json')}", 
                        scale=1.2
                    )
                ], 
                spacing=50
            )
            infoBar6 = flet.Row(
                controls=[
                    Icon(
                        name=flet.icons.INFO, 
                        
                        scale=1.2
                    ), 
                    flet.Text(
                        f"Count all diologs with ai (discussion history): {countJson('discussion_history.json')}", 
                        scale=1.2
                    )
                ], 
                spacing=50
            )
            infoBar7 = flet.Row(
                controls=[
                    Icon(
                        name=flet.icons.INFO, 
                        
                        scale=1.2
                    ), 
                    flet.Text(
                        f"Count all diologs with ai (weather history): {countJson('weather_history.json')}", 
                        scale=1.2
                    )
                ], 
                spacing=50
            )
            infoBar8 = flet.Row(
                controls=[
                    Icon(
                        name=flet.icons.INFO, 
                        
                        scale=1.2
                    ), 
                    flet.Text(
                        f"Count all diologs with ai (weatherA history): {countJson('weatherA_history.json')}", 
                        scale=1.2
                    )
                ], 
                spacing=50
            )
            page.add(infoBar1, infoBar2, infoBar3, infoBar4, infoBar5, infoBar6, infoBar7, infoBar8)
            def makeCode(arg):
                if arg == 'open':
                    code = ft.Container(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        value='example.exe'
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value='[',
                                                            color=ft.colors.BLUE_300,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                                ft.Text(),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value='''    open''',
                                                            color=ft.colors.PINK_ACCENT,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''(''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''"C:\\Projects\\python\\AI\\test.json"''',
                                                            color=ft.colors.ORANGE_200,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value=''', ''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''"тест"''',
                                                            color=ft.colors.ORANGE_200,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value=''')''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                                ft.Text(),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value=']',
                                                            color=ft.colors.BLUE_300,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                            ]
                                        ),
                                        border=ft.border.all(1, ft.colors.PINK_ACCENT),
                                        bgcolor=ft.colors.BLACK38,
                                        border_radius=20,
                                        padding=ft.padding.all(10),
                                        margin=ft.margin.all(15),
                                        alignment=ft.alignment.top_left,
                                        width=350,
                                        height=180
                                        
                                    )
                                ]
                            ),
                            border=ft.border.all(1, ft.colors.BLACK26),
                            bgcolor=ft.colors.BLACK26,
                            border_radius=10,
                            padding=15,
                            width=410,
                            height=270,
                        ),
                        #alignment=ft.alignment.top_center
                    )
                    return code
                elif arg == 'close':
                    code = ft.Container(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        value='example.exe'
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value='[',
                                                            color=ft.colors.BLUE_300,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                                ft.Text(),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value='''    close''',
                                                            color=ft.colors.PINK_ACCENT,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''(''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''"C:\\Projects\\python\\AI\\test.exe"''',
                                                            color=ft.colors.ORANGE_200,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value=''', ''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''"тест"''',
                                                            color=ft.colors.ORANGE_200,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value=''')''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                                ft.Text(),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value=']',
                                                            color=ft.colors.BLUE_300,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                            ]
                                        ),
                                        border=ft.border.all(1, ft.colors.PINK_ACCENT),
                                        bgcolor=ft.colors.BLACK38,
                                        border_radius=20,
                                        padding=ft.padding.all(10),
                                        margin=ft.margin.all(15),
                                        alignment=ft.alignment.top_left,
                                        width=350,
                                        height=180
                                        
                                    )
                                ]
                            ),
                            border=ft.border.all(1, ft.colors.BLACK26),
                            bgcolor=ft.colors.BLACK26,
                            border_radius=10,
                            padding=15,
                            width=410,
                            height=270,
                        ),
                        #alignment=ft.alignment.top_center
                    )
                    return code
                elif arg == 'time':
                    code = ft.Container(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        value='example.exe'
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value='[',
                                                            color=ft.colors.BLUE_300,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                                ft.Text(),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value='''    time''',
                                                            color=ft.colors.PINK_ACCENT,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''(''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''30''',
                                                            color=ft.colors.ORANGE_200,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value=''')''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                                ft.Text(),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value=']',
                                                            color=ft.colors.BLUE_300,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                            ]
                                        ),
                                        border=ft.border.all(1, ft.colors.PINK_ACCENT),
                                        bgcolor=ft.colors.BLACK38,
                                        border_radius=20,
                                        padding=ft.padding.all(10),
                                        margin=ft.margin.all(15),
                                        alignment=ft.alignment.top_left,
                                        width=350,
                                        height=180
                                        
                                    )
                                ]
                            ),
                            border=ft.border.all(1, ft.colors.BLACK26),
                            bgcolor=ft.colors.BLACK26,
                            border_radius=10,
                            padding=15,
                            width=410,
                            height=270,
                        ),
                        #alignment=ft.alignment.top_center
                    )
                    return code
                elif arg == 'open_url':
                    code = ft.Container(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        value='example.exe'
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value='[',
                                                            color=ft.colors.BLUE_300,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                                ft.Text(),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value='''    open_url''',
                                                            color=ft.colors.PINK_ACCENT,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''(''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''"https://www.youtube.com/"''',
                                                            color=ft.colors.ORANGE_200,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value=''', ''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''"ютуб"''',
                                                            color=ft.colors.ORANGE_200,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value=''')''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                                ft.Text(),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value=']',
                                                            color=ft.colors.BLUE_300,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                            ]
                                        ),
                                        border=ft.border.all(1, ft.colors.PINK_ACCENT),
                                        bgcolor=ft.colors.BLACK38,
                                        border_radius=20,
                                        padding=ft.padding.all(10),
                                        margin=ft.margin.all(15),
                                        alignment=ft.alignment.top_left,
                                        width=350,
                                        height=180
                                        
                                    )
                                ]
                            ),
                            border=ft.border.all(1, ft.colors.BLACK26),
                            bgcolor=ft.colors.BLACK26,
                            border_radius=10,
                            padding=15,
                            width=410,
                            height=270,
                        ),
                        #alignment=ft.alignment.top_center
                    )
                    return code
                elif arg == 'voice':
                    code = ft.Container(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        value='example.exe'
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value='[',
                                                            color=ft.colors.BLUE_300,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                                ft.Text(),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value='''    voice''',
                                                            color=ft.colors.PINK_ACCENT,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''(''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value='''"у меня все отлично"''',
                                                            color=ft.colors.ORANGE_200,
                                                            selectable=True
                                                        ),
                                                        ft.Text(
                                                            value=''')''',
                                                            color=ft.colors.WHITE,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                                ft.Text(),
                                                ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            value=']',
                                                            color=ft.colors.BLUE_300,
                                                            selectable=True
                                                        ),
                                                    ],
                                                    spacing=0
                                                ),
                                            ]
                                        ),
                                        border=ft.border.all(1, ft.colors.PINK_ACCENT),
                                        bgcolor=ft.colors.BLACK38,
                                        border_radius=20,
                                        padding=ft.padding.all(10),
                                        margin=ft.margin.all(15),
                                        alignment=ft.alignment.top_left,
                                        width=350,
                                        height=180
                                        
                                    )
                                ]
                            ),
                            border=ft.border.all(1, ft.colors.BLACK26),
                            bgcolor=ft.colors.BLACK26,
                            border_radius=10,
                            padding=15,
                            width=410,
                            height=270,
                        ),
                        #alignment=ft.alignment.top_center
                    )
                    return code
            page.add(
                ft.ListView(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Container(
                                        ft.Text(
                                            value='~ example ~',
                                            size=15,
                                            italic=True,
                                            selectable=True
                                        ),
                                        border=ft.border.all(1, ft.colors.BLACK26),
                                        bgcolor=ft.colors.BLACK26,
                                        border_radius=5,
                                    ),
                                    ft.Text(
                                            value='open("C:\\Projects\\python\\ApiV2\\api.py", "api")|time(2)|open_url("https://www.microsoft.com/", "microsoft")|voice("ура победа")',
                                            size=15,
                                            selectable=True
                                    ),
                                    ft.Divider(
                                        color=ft.colors.PINK_ACCENT
                                    ),
                                    ft.Container(
                                        ft.Text(
                                            value='~ open ~',
                                            size=15,
                                            italic=True,
                                            selectable=True
                                        ),
                                        border=ft.border.all(1, ft.colors.BLACK26),
                                        bgcolor=ft.colors.BLACK26,
                                        border_radius=5,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                value='open команда для открытие программ и файлов. Имеет 2 аргумента для ввода: ',
                                                size=15,
                                                italic=True,
                                                selectable=True
                                            ),
                                            ft.Container(
                                                ft.Text(
                                                    value='path_to_folder',
                                                    size=15,
                                                    italic=True,
                                                    selectable=True
                                                ),
                                                border=ft.border.all(1, ft.colors.BLACK26),
                                                bgcolor=ft.colors.BLACK26,
                                                border_radius=5,
                                            ),
                                            ft.Text(
                                                value=' и',
                                                size=15,
                                                italic=True,
                                                selectable=True
                                            ),
                                            ft.Container(
                                                ft.Text(
                                                    value='name_app',
                                                    size=15,
                                                    italic=True,
                                                    selectable=True
                                                ),
                                                border=ft.border.all(1, ft.colors.BLACK26),
                                                bgcolor=ft.colors.BLACK26,
                                                border_radius=5,
                                            ),
                                        ],
                                        spacing=0
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.ListTile(
                                                leading=ft.Icon(ft.icons.CHECK_CIRCLE),
                                                title=ft.Row(
                                                    controls=[
                                                        ft.Container(
                                                            ft.Text(
                                                                value='name_app',
                                                                size=15,
                                                                italic=True,
                                                                selectable=True
                                                            ),
                                                            border=ft.border.all(1, ft.colors.BLACK26),
                                                            bgcolor=ft.colors.BLACK26,
                                                            border_radius=5,
                                                        ),
                                                        ft.Text(
                                                            value=' example: best app',
                                                            size=15,
                                                            italic=True,
                                                            selectable=True
                                                        )
                                                    ],
                                                    spacing=0
                                                )
                                            ),
                                            ft.ListTile(
                                                leading=ft.Icon(ft.icons.CHECK_CIRCLE),
                                                title=ft.Row(
                                                    controls=[
                                                        ft.Container(
                                                            ft.Text(
                                                                value='path_to_folder',
                                                                size=15,
                                                                italic=True,
                                                                selectable=True
                                                            ),
                                                            border=ft.border.all(1, ft.colors.BLACK26),
                                                            bgcolor=ft.colors.BLACK26,
                                                            border_radius=5,
                                                        ),
                                                        ft.Text(
                                                            value=' example: C:\\test\\pop.exe',
                                                            size=15,
                                                            italic=True,
                                                            selectable=True
                                                        )
                                                    ],
                                                    spacing=0
                                                )
                                            ),
                                        ],
                                        spacing=3
                                    ),
                                    makeCode('open'),
                                    ft.Divider(
                                        color=ft.colors.PINK_ACCENT
                                    ),
                                    ft.Container(
                                        ft.Text(
                                            value='~ time ~',
                                            size=15,
                                            italic=True,
                                            selectable=True
                                        ),
                                        border=ft.border.all(1, ft.colors.BLACK26),
                                        bgcolor=ft.colors.BLACK26,
                                        border_radius=5,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                value='time команда для задержки между исполнениями других команд. Имеет 1 аргумент для ввода: ',
                                                size=15,
                                                italic=True,
                                                selectable=True
                                            ),
                                            ft.Container(
                                                ft.Text(
                                                    value='time_int',
                                                    size=15,
                                                    italic=True,
                                                    selectable=True
                                                ),
                                                border=ft.border.all(1, ft.colors.BLACK26),
                                                bgcolor=ft.colors.BLACK26,
                                                border_radius=5,
                                            )
                                        ],
                                        spacing=0
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.ListTile(
                                                leading=ft.Icon(ft.icons.CHECK_CIRCLE),
                                                title=ft.Row(
                                                    controls=[
                                                        ft.Container(
                                                            ft.Text(
                                                                value='time_int',
                                                                size=15,
                                                                italic=True,
                                                                selectable=True
                                                            ),
                                                            border=ft.border.all(1, ft.colors.BLACK26),
                                                            bgcolor=ft.colors.BLACK26,
                                                            border_radius=5,
                                                        ),
                                                        ft.Text(
                                                            value=' example: 15',
                                                            size=15,
                                                            italic=True,
                                                            selectable=True
                                                        )
                                                    ],
                                                    spacing=0
                                                )
                                            )
                                        ],
                                        spacing=3
                                    ),
                                    makeCode('time'),
                                    ft.Divider(
                                        color=ft.colors.PINK_ACCENT
                                    ),
                                    ft.Container(
                                        ft.Text(
                                            value='~ close ~',
                                            size=15,
                                            italic=True,
                                            selectable=True
                                        ),
                                        border=ft.border.all(1, ft.colors.BLACK26),
                                        bgcolor=ft.colors.BLACK26,
                                        border_radius=5,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                value='close команда для закрытие программ (ТОЛЬКО EXE). Имеет 2 аргумента для ввода: ',
                                                size=15,
                                                italic=True,
                                                selectable=True
                                            ),
                                            ft.Container(
                                                ft.Text(
                                                    value='path_to_folder',
                                                    size=15,
                                                    italic=True,
                                                    selectable=True
                                                ),
                                                border=ft.border.all(1, ft.colors.BLACK26),
                                                bgcolor=ft.colors.BLACK26,
                                                border_radius=5,
                                            ),
                                            ft.Text(
                                                value=' и',
                                                size=15,
                                                italic=True,
                                                selectable=True
                                            ),
                                            ft.Container(
                                                ft.Text(
                                                    value='name_app',
                                                    size=15,
                                                    italic=True,
                                                    selectable=True
                                                ),
                                                border=ft.border.all(1, ft.colors.BLACK26),
                                                bgcolor=ft.colors.BLACK26,
                                                border_radius=5,
                                            ),
                                        ],
                                        spacing=0
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.ListTile(
                                                leading=ft.Icon(ft.icons.CHECK_CIRCLE),
                                                title=ft.Row(
                                                    controls=[
                                                        ft.Container(
                                                            ft.Text(
                                                                value='name_app',
                                                                size=15,
                                                                italic=True,
                                                                selectable=True
                                                            ),
                                                            border=ft.border.all(1, ft.colors.BLACK26),
                                                            bgcolor=ft.colors.BLACK26,
                                                            border_radius=5,
                                                        ),
                                                        ft.Text(
                                                            value=' example: best app',
                                                            size=15,
                                                            italic=True,
                                                            selectable=True
                                                        )
                                                    ],
                                                    spacing=0
                                                )
                                            ),
                                            ft.ListTile(
                                                leading=ft.Icon(ft.icons.CHECK_CIRCLE),
                                                title=ft.Row(
                                                    controls=[
                                                        ft.Container(
                                                            ft.Text(
                                                                value='path_to_folder',
                                                                size=15,
                                                                italic=True,
                                                                selectable=True
                                                            ),
                                                            border=ft.border.all(1, ft.colors.BLACK26),
                                                            bgcolor=ft.colors.BLACK26,
                                                            border_radius=5,
                                                        ),
                                                        ft.Text(
                                                            value=' example: C:\\test\\pop.exe',
                                                            size=15,
                                                            italic=True,
                                                            selectable=True
                                                        )
                                                    ],
                                                    spacing=0
                                                )
                                            ),
                                        ],
                                        spacing=3
                                    ),
                                    makeCode('close'),
                                    ft.Divider(
                                        color=ft.colors.PINK_ACCENT
                                    ),
                                    ft.Container(
                                        ft.Text(
                                            value='~ open_url ~',
                                            size=15,
                                            italic=True,
                                            selectable=True
                                        ),
                                        border=ft.border.all(1, ft.colors.BLACK26),
                                        bgcolor=ft.colors.BLACK26,
                                        border_radius=5,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                value='open_url команда для открытия сайтов. Имеет 2 аргумента для ввода: ',
                                                size=15,
                                                italic=True,
                                                selectable=True
                                            ),
                                            ft.Container(
                                                ft.Text(
                                                    value='url_to_site',
                                                    size=15,
                                                    italic=True,
                                                    selectable=True
                                                ),
                                                border=ft.border.all(1, ft.colors.BLACK26),
                                                bgcolor=ft.colors.BLACK26,
                                                border_radius=5,
                                            ),
                                            ft.Text(
                                                value=' и',
                                                size=15,
                                                italic=True,
                                                selectable=True
                                            ),
                                            ft.Container(
                                                ft.Text(
                                                    value='name_app',
                                                    size=15,
                                                    italic=True,
                                                    selectable=True
                                                ),
                                                border=ft.border.all(1, ft.colors.BLACK26),
                                                bgcolor=ft.colors.BLACK26,
                                                border_radius=5,
                                            ),
                                        ],
                                        spacing=0
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.ListTile(
                                                leading=ft.Icon(ft.icons.CHECK_CIRCLE),
                                                title=ft.Row(
                                                    controls=[
                                                        ft.Container(
                                                            ft.Text(
                                                                value='name_app',
                                                                size=15,
                                                                italic=True,
                                                                selectable=True
                                                            ),
                                                            border=ft.border.all(1, ft.colors.BLACK26),
                                                            bgcolor=ft.colors.BLACK26,
                                                            border_radius=5,
                                                        ),
                                                        ft.Text(
                                                            value=' example: youtube',
                                                            size=15,
                                                            italic=True,
                                                            selectable=True
                                                        )
                                                    ],
                                                    spacing=0
                                                )
                                            ),
                                            ft.ListTile(
                                                leading=ft.Icon(ft.icons.CHECK_CIRCLE),
                                                title=ft.Row(
                                                    controls=[
                                                        ft.Container(
                                                            ft.Text(
                                                                value='url_to_site',
                                                                size=15,
                                                                italic=True,
                                                                selectable=True
                                                            ),
                                                            border=ft.border.all(1, ft.colors.BLACK26),
                                                            bgcolor=ft.colors.BLACK26,
                                                            border_radius=5,
                                                        ),
                                                        ft.Text(
                                                            value=' example: https://www.youtube.com/',
                                                            size=15,
                                                            italic=True,
                                                            selectable=True
                                                        )
                                                    ],
                                                    spacing=0
                                                )
                                            ),
                                        ],
                                        spacing=3
                                    ),
                                    makeCode('open_url'),
                                    ft.Divider(
                                        color=ft.colors.PINK_ACCENT
                                    ),
                                    ft.Container(
                                        ft.Text(
                                            value='~ voice ~',
                                            size=15,
                                            italic=True,
                                            selectable=True
                                        ),
                                        border=ft.border.all(1, ft.colors.BLACK26),
                                        bgcolor=ft.colors.BLACK26,
                                        border_radius=5,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                value='voice команда для генерации голоса и его воспроизведения. Имеет 1  для ввода: ',
                                                size=15,
                                                italic=True,
                                                selectable=True
                                            ),
                                            ft.Container(
                                                ft.Text(
                                                    value='text',
                                                    size=15,
                                                    italic=True,
                                                    selectable=True
                                                ),
                                                border=ft.border.all(1, ft.colors.BLACK26),
                                                bgcolor=ft.colors.BLACK26,
                                                border_radius=5,
                                            )
                                        ],
                                        spacing=0
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.ListTile(
                                                leading=ft.Icon(ft.icons.CHECK_CIRCLE),
                                                title=ft.Row(
                                                    controls=[
                                                        ft.Container(
                                                            ft.Text(
                                                                value='text',
                                                                size=15,
                                                                italic=True,
                                                                selectable=True
                                                            ),
                                                            border=ft.border.all(1, ft.colors.BLACK26),
                                                            bgcolor=ft.colors.BLACK26,
                                                            border_radius=5,
                                                        ),
                                                        ft.Text(
                                                            value=' example: какой чудесный день',
                                                            size=15,
                                                            italic=True,
                                                            selectable=True
                                                        )
                                                    ],
                                                    spacing=0
                                                )
                                            )
                                        ],
                                        spacing=3
                                    ),
                                    makeCode('voice'),
                                ],
                                spacing=30
                            ),
                            padding=ft.padding.all(10),
                            margin=ft.margin.all(10)
                        ),
                    ],
                    auto_scroll=False,
                    expand=True,
                    spacing=10
                )
            )
            page.update()

        if nav_dest == 1:
            def extract_dialogs_from_json(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                dialogs = []
                
                for entry in data:
                    role = entry['role']
                    content = entry['content']
                    dialogs.append(f"{role}:{content}")
                
                return dialogs
            
            file_path = 'chat_history.json'
            dialogs = extract_dialogs_from_json(file_path)

            chat = ft.ListView(
                controls=[],
                expand=True,
                spacing=10,
                auto_scroll=True,
            )

            for dialog in dialogs:
                dialog = dialog.split(':', 1)
                if dialog[0] == 'assistant':
                    circle = ft.CircleAvatar(
                        content=ft.Text("A"),
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.RED_100,
                    )
                    text = ft.Container(
                        ft.Text(
                            dialog[1], 
                            width=1000
                        ),
                        border=ft.border.all(
                            1, 
                            ft.colors.PURPLE_200
                        ),
                        border_radius=30,
                        padding=15
                    )
                elif dialog[0] == 'user':
                    circle = ft.CircleAvatar(
                        content=ft.Text("U"),
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.AMBER,
                    )
                    text = ft.Container(
                        ft.Text(
                            dialog[1], 
                            width=1000
                        ),
                        border=ft.border.all(
                            1, 
                            ft.colors.PURPLE_200
                        ),
                        border_radius=30,
                        padding=15
                    )
                elif dialog[0] == 'system':
                    circle = ft.CircleAvatar(
                        content=ft.Text("S"),
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.PINK_200,
                    )
                    text = ft.Container(
                        ft.Text(
                            dialog[1], 
                            width=1000
                        ),
                        border=ft.border.all(
                            1, 
                            ft.colors.PURPLE_200
                        ),
                        border_radius=30,
                        padding=15
                    )

                message = ft.Row(
                    controls=[circle, text], 
                    spacing=15,
                    tight=True
                )
                chat.controls.append(message)
            def send_click(e):
                circle = ft.CircleAvatar(
                        content=ft.Text("U"),
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.AMBER,
                    )
                text = ft.Container(ft.Text(new_message.value, 
                    width=1000),
                    border=ft.border.all(1, ft.colors.AMBER),
                    border_radius=30,
                    padding=15)
                message = ft.Row(
                    controls=[circle, text], 
                    spacing=15,
                    )
                
                text = new_message.value
                new_message.value = ""
                chat.controls.append(message)
                page.update()

                process_command(text)
                answer = ask_main(text)

                page.update()
                circle = ft.CircleAvatar(
                        content=ft.Text("A"),
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.RED_100,
                    )
                text = ft.Container(
                    ft.Text(
                        answer, 
                        width=1000
                        ),
                        border=ft.border.all(1, ft.colors.AMBER),
                        border_radius=30,
                        padding=15
                )
                message = ft.Row(
                    controls=[circle, text], 
                    spacing=15,
                )
                chat.controls.append(message)
                page.update()

            new_message = ft.TextField(
                hint_text="Напишите сообщение...",
                autofocus=True,
                shift_enter=True,
                min_lines=1,
                max_lines=5,
                filled=True,
                expand=True,
                content_padding=15,
                on_submit=send_click
            )

            page.add(
                ft.Container(
                    content=chat,
                    border_radius=40,
                    padding=10,
                    expand=True,
                ),
                ft.Row(
                    [
                        new_message,
                        ft.IconButton(
                            icon=ft.icons.SEND_ROUNDED,
                            tooltip="Отправить сообщение",
                            on_click=send_click
                        ),
                    ]
                ),
            )
        if nav_dest == 4:
            cmdConstruct = ft.Dropdown(
                options=[
                    ft.dropdown.Option("Открыть"),
                    ft.dropdown.Option("Закрыть"),
                    ft.dropdown.Option("Своя команда cmd"),
                    ft.dropdown.Option("Открыть ссылку"),
                    ft.dropdown.Option("Несколько команд"),
                ],
                border_radius=30,
                scale=0.9,
            )

            cmdReturnFirst = ft.TextField(
                label="введите raw выражение команды",
                border_radius=30,
                scale=0.9
            )

            icon = ft.Icon(
                ft.icons.INFO,
                scale=1.3
            )
            

            control = ft.Row(
                controls=[
                    icon,
                    cmdConstruct
                ],
                spacing=4,
                tight=True
            )

            control1 = ft.Row(
                controls=[],
                spacing=4,
                tight=True
            )

            def close_banner(e):
                page.banner.open = False
                page.update()
            
            cmdPathToFolder = ft.TextField(
                label="путь до файла",
                border_radius=30,
                scale=0.9
            )

            cmdUrl = ft.TextField(
                label="укажите ссылку",
                border_radius=30,
                scale=0.9
            )

            cmdNameUrl = ft.TextField(
                label="введите название для ссылки",
                border_radius=30,
                scale=0.9
            )

            cmdCommand = ft.TextField(
                label="команда для консоли",
                border_radius=30,
                scale=0.9
            )

            cmdNameCommand = ft.TextField(
                label="введите название для команды",
                border_radius=30,
                scale=0.9
            )

            cmdNameApp = ft.TextField(
                label="введите название приложения",
                border_radius=30,
                scale=0.9
            )
            
            cmdVoice = ft.TextField(
                label="фраза для исполнения",
                border_radius=30,
                scale=0.9,
            )
            

            def add_commands(e):
                if (cmdConstruct.value == 'Открыть' or cmdConstruct.value == 'Закрыть'):
                    if cmdConstruct.disabled == False:
                        cmdConstruct.disabled = True

                        control.controls.append(
                            cmdPathToFolder
                        )

                        print(control.controls)

                        add.disabled = True
                        control.controls.append(add1)
                        page.update()
                    elif cmdPathToFolder.disabled == False:
                        if (cmdPathToFolder.value == '') or ('\\' not in cmdPathToFolder.value):
                            def erorrBanner(erorr):
                                    page.banner = Banner(
                                        bgcolor=colors.AMBER_100,
                                        leading=Icon(
                                            icons.WARNING_AMBER_ROUNDED, 
                                            color=colors.AMBER, 
                                            size=55
                                        ),
                                        content=Text(
                                            f"Oops, there were some errors {erorr}", 
                                            size=20, 
                                            color=flet.colors.BLACK26
                                        ),
                                        actions=[
                                            ElevatedButton(
                                                "Ignore", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                            ),
                                            ElevatedButton(
                                                "Cancel", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                            ),
                                        ],    
                                    )
                                    page.banner.open = True
                                    page.update()

                            erorrBanner('please write path to folder')
                        else:
                            if add1.disabled == False:
                                cmdPathToFolder.disabled = True

                                control.controls.append(
                                    cmdNameApp
                                )

                                print(control.controls)

                                add1.disabled = True

                                control.controls.append(add2)
                                page.update()
                    elif cmdNameApp.disabled == False:
                        if (cmdNameApp.value == ''):
                            def erorrBanner(erorr):
                                    page.banner = Banner(
                                        bgcolor=colors.AMBER_100,
                                        leading=Icon(
                                            icons.WARNING_AMBER_ROUNDED, 
                                            color=colors.AMBER, 
                                            size=55
                                        ),
                                        content=Text(
                                            f"Oops, there were some errors {erorr}", 
                                            size=20, 
                                            color=flet.colors.BLACK26
                                        ),
                                        actions=[
                                            ElevatedButton(
                                                "Ignore", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                            ),
                                            ElevatedButton(
                                                "Cancel", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                        ),
                                        ],  
                                    )
                                    page.banner.open = True
                                    page.update()

                            erorrBanner('please write name app')
                        else:
                            if add2.disabled == False:
                                cmdNameApp.disabled = True

                                control.controls.append(
                                    cmdVoice
                                )

                                add2.disabled = True
                                page.update()

                elif (cmdConstruct.value == 'Своя команда cmd'):
                    if cmdConstruct.disabled == False:
                        cmdConstruct.disabled = True

                        control.controls.append(
                            cmdCommand
                        )

                        print(control.controls)

                        add.disabled = True
                        control.controls.append(add1)
                        page.update()
                    elif cmdCommand.disabled == False:
                        if (cmdCommand.value == ' '):
                            def erorrBanner(erorr):
                                    page.banner = Banner(
                                        bgcolor=colors.AMBER_100,
                                        leading=Icon(
                                            icons.WARNING_AMBER_ROUNDED, 
                                            color=colors.AMBER, 
                                            size=55
                                        ),
                                        content=Text(
                                            f"Oops, there were some errors {erorr}", 
                                            size=20, 
                                            color=flet.colors.BLACK26
                                        ),
                                        actions=[
                                            ElevatedButton(
                                                "Ignore", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                            ),
                                            ElevatedButton(
                                                "Cancel", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                            ),
                                        ],    
                                    )
                                    page.banner.open = True
                                    page.update()

                            erorrBanner('please write command')
                        else:
                            if add1.disabled == False:
                                cmdCommand.disabled = True

                                control.controls.append(
                                    cmdNameCommand
                                )

                                print(control.controls)

                                add1.disabled = True

                                control.controls.append(add2)
                                page.update()
                    elif cmdNameCommand.disabled == False:
                        if (cmdNameCommand.value == ' '):
                            def erorrBanner(erorr):
                                    page.banner = Banner(
                                        bgcolor=colors.AMBER_100,
                                        leading=Icon(
                                            icons.WARNING_AMBER_ROUNDED, 
                                            color=colors.AMBER, 
                                            size=55
                                        ),
                                        content=Text(
                                            f"Oops, there were some errors {erorr}", 
                                            size=20, 
                                            color=flet.colors.BLACK26
                                        ),
                                        actions=[
                                            ElevatedButton(
                                                "Ignore", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                            ),
                                            ElevatedButton(
                                                "Cancel", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                        ),
                                        ],  
                                    )
                                    page.banner.open = True
                                    page.update()

                            erorrBanner('please write name command')
                        else:
                            if add2.disabled == False:
                                cmdNameCommand.disabled = True

                                control.controls.append(
                                    cmdVoice
                                )

                                add2.disabled = True
                                page.update()
                elif (cmdConstruct.value == 'Открыть ссылку'):
                    if cmdConstruct.disabled == False:
                        cmdConstruct.disabled = True

                        control.controls.append(
                            cmdUrl
                        )

                        print(control.controls)

                        add.disabled = True
                        control.controls.append(add1)
                        page.update()
                    elif cmdUrl.disabled == False:
                        if (cmdUrl.value == ' '):
                            def erorrBanner(erorr):
                                    page.banner = Banner(
                                        bgcolor=colors.AMBER_100,
                                        leading=Icon(
                                            icons.WARNING_AMBER_ROUNDED, 
                                            color=colors.AMBER, 
                                            size=55
                                        ),
                                        content=Text(
                                            f"Oops, there were some errors {erorr}", 
                                            size=20, 
                                            color=flet.colors.BLACK26
                                        ),
                                        actions=[
                                            ElevatedButton(
                                                "Ignore", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                            ),
                                            ElevatedButton(
                                                "Cancel", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                            ),
                                        ],    
                                    )
                                    page.banner.open = True
                                    page.update()

                            erorrBanner('please write cmdUrl')
                        else:
                            if add1.disabled == False:
                                cmdUrl.disabled = True

                                control.controls.append(
                                    cmdNameUrl
                                )

                                print(control.controls)

                                add1.disabled = True

                                control.controls.append(add2)
                                page.update()
                    elif cmdNameUrl.disabled == False:
                        if (cmdNameUrl.value == ' '):
                            def erorrBanner(erorr):
                                    page.banner = Banner(
                                        bgcolor=colors.AMBER_100,
                                        leading=Icon(
                                            icons.WARNING_AMBER_ROUNDED, 
                                            color=colors.AMBER, 
                                            size=55
                                        ),
                                        content=Text(
                                            f"Oops, there were some errors {erorr}", 
                                            size=20, 
                                            color=flet.colors.BLACK26
                                        ),
                                        actions=[
                                            ElevatedButton(
                                                "Ignore", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                            ),
                                            ElevatedButton(
                                                "Cancel", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                        ),
                                        ],  
                                    )
                                    page.banner.open = True
                                    page.update()

                            erorrBanner('please write name url')
                        else:
                            if add2.disabled == False:
                                cmdNameUrl.disabled = True

                                control.controls.append(
                                    cmdVoice
                                )

                                add2.disabled = True
                                page.update()
                elif (cmdConstruct.value == 'Несколько команд'):
                    if cmdConstruct.disabled == False:
                        cmdConstruct.disabled = True

                        control.controls.append(
                            cmdReturnFirst
                        )

                        print(control.controls)

                        add.disabled = True
                        control.controls.append(add1)
                        page.update()
                    elif cmdReturnFirst.disabled == False:
                        if ('|' not in cmdReturnFirst.value):
                            def erorrBanner(erorr):
                                    page.banner = Banner(
                                        bgcolor=colors.AMBER_100,
                                        leading=Icon(
                                            icons.WARNING_AMBER_ROUNDED, 
                                            color=colors.AMBER, 
                                            size=55
                                        ),
                                        content=Text(
                                            f"Oops, there were some errors {erorr}", 
                                            size=20, 
                                            color=flet.colors.BLACK26
                                        ),
                                        actions=[
                                            ElevatedButton(
                                                "Ignore", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                            ),
                                            ElevatedButton(
                                                "Cancel", 
                                                on_click=close_banner, 
                                                bgcolor=flet.colors.AMBER_100,
                                                color=flet.colors.BLACK26
                                        ),
                                        ],  
                                    )
                                    page.banner.open = True
                                    page.update()

                            erorrBanner('please write normal raw command, you can see example in page info')
                        else:
                            cmdReturnFirst.disabled = True

                            control.controls.append(
                                cmdVoice
                            )

                            print(control.controls)

                            add1.disabled = True
                            page.update()

            
            add1 = ft.IconButton(
                icon=ft.icons.ADD_CIRCLE,
                scale=1.1,
                padding=10,
                on_click=add_commands
            )

            add2 = ft.IconButton(
                icon=ft.icons.ADD_CIRCLE,
                scale=1.1,
                padding=10,
                on_click=add_commands  
            )
            
            add2 = ft.IconButton(
                icon=ft.icons.ADD_CIRCLE,
                scale=1.1,
                padding=10,
                on_click=add_commands
            )   

            add3 = ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.IconButton(
                                    icon=ft.icons.ADD_CIRCLE,
                                    scale=1.2,
                                    padding=1,
                                    on_click=add_commands
                                ),
                            ft.IconButton(
                                icon=ft.icons.DATA_SAVER_ON,
                                scale=1.2,
                                padding=1,
                                on_click=add_commands
                            ),
                        ]
                    )
                ],
            )

                        
            add = ft.IconButton(
                icon=ft.icons.ADD_CIRCLE,
                scale=1.1,
                padding=10,
                on_click=add_commands
            )
            control.controls.append(add)

            commands = ft.ListView(
                controls=[control],
                spacing=10,
                auto_scroll=True,
            )

            commands1 = ft.ListView(
                controls=[control1],
                spacing=10,
                auto_scroll=True,
            )
            
    
            def clear_all(e):
                cmdConstruct.disabled = False
                cmdPathToFolder.disabled = False
                cmdNameApp.disabled = False
                cmdVoice.disabled = False
                cmdNameCommand.disabled = False
                cmdCommand.disabled = False
                cmdUrl.disabled = False
                cmdNameUrl.disabled = False
                add.disabled = False
                add1.disabled = False
                add2.disabled = False
                cmdReturnFirst.disabled = False

                cmdConstruct.value = ''
                cmdPathToFolder.value = ''
                cmdNameApp.value = ''
                cmdVoice.value = ''
                cmdCommand.value = ''
                cmdNameCommand.value = ''
                cmdUrl.value = ''
                cmdNameUrl.value = ''
                cmdReturnFirst.value = ''

                control.controls = [
                    icon,
                    cmdConstruct,
                    add
                ]
                page.update()

            def add_command(e):
                from addon.construct import add_command_to_file

                if (cmdConstruct.value == 'Своя команда cmd') and (cmdNameCommand.disabled == True):
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(""),
                        action="",
                    )
                    words = cmdVoice.value.split()
                    quoted_words = [f'"{word}"' for word in words]
                    output_string = ", ".join(quoted_words)
                    cmd_config = f'({output_string}): lambda: execute_cmd_command("{cmdCommand.value}", "{cmdNameCommand.value}")'
                    add_command_to_file('utils\\commands.py', cmd_config)

                    page.snack_bar = ft.SnackBar(
                        ft.Text(
                            f"Command succsesful added to command list",
                            size=10,
                            weight=ft.FontWeight.BOLD
                        )
                    )
                    page.snack_bar.open = True
                    page.update()

                    cmdConstruct.disabled = False
                    cmdPathToFolder.disabled = False
                    cmdNameApp.disabled = False
                    cmdVoice.disabled = False
                    cmdNameCommand.disabled = False
                    cmdCommand.disabled = False
                    cmdUrl.disabled = False
                    cmdNameUrl.disabled = False
                    cmdCommand.value = ''
                    cmdNameCommand.value = ''
                    cmdUrl.value = ''
                    cmdNameUrl.value = ''
                    add.disabled = False
                    add1.disabled = False
                    add2.disabled = False

                    cmdConstruct.value = ''
                    cmdPathToFolder.value = ''
                    cmdNameApp.value = ''
                    cmdVoice.value = ''

                    control.controls = [
                        icon,
                        cmdConstruct,
                        add
                    ]
                    page.update()
                
                elif (cmdConstruct.value == 'Открыть ссылку') and (cmdNameUrl.disabled == True):
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(""),
                        action="",
                    )
                    words = cmdVoice.value.split()
                    quoted_words = [f'"{word}"' for word in words]
                    output_string = ", ".join(quoted_words)
                    cmd_config = f'({output_string}): lambda: open_url("{cmdUrl.value}", "{cmdNameUrl.value}")'
                    add_command_to_file('utils\\commands.py', cmd_config)

                    page.snack_bar = ft.SnackBar(
                        ft.Text(
                            f"Command succsesful added to command list",
                            size=10,
                            weight=ft.FontWeight.BOLD
                        )
                    )
                    page.snack_bar.open = True
                    page.update()

                    cmdConstruct.disabled = False
                    cmdPathToFolder.disabled = False
                    cmdNameApp.disabled = False
                    cmdVoice.disabled = False
                    cmdNameCommand.disabled = False
                    cmdCommand.disabled = False
                    cmdUrl.disabled = False
                    cmdNameUrl.disabled = False
                    cmdCommand.value = ''
                    cmdNameCommand.value = ''
                    cmdUrl.value = ''
                    cmdNameUrl.value = ''
                    add.disabled = False
                    add1.disabled = False
                    add2.disabled = False

                    cmdConstruct.value = ''
                    cmdPathToFolder.value = ''
                    cmdNameApp.value = ''
                    cmdVoice.value = ''

                    control.controls = [
                        icon,
                        cmdConstruct,
                        add
                    ]
                    page.update()

                elif (cmdConstruct.value == 'Несколько команд') and (cmdReturnFirst.disabled == True):
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(""),
                        action="",
                    )
                    words = cmdVoice.value.split()
                    quoted_words = [f'"{word}"' for word in words]
                    output_string = ", ".join(quoted_words)
                    cmd_config = f'''({output_string}): lambda: construct_some('{cmdReturnFirst.value}')'''
                    add_command_to_file('utils\\commands.py', cmd_config)

                    page.snack_bar = ft.SnackBar(
                        ft.Text(
                            f"Command succsesful added to command list",
                            size=10,
                            weight=ft.FontWeight.BOLD
                        )
                    )
                    page.snack_bar.open = True
                    page.update()

                    cmdConstruct.disabled = False
                    cmdPathToFolder.disabled = False
                    cmdNameApp.disabled = False
                    cmdVoice.disabled = False
                    cmdNameCommand.disabled = False
                    cmdCommand.disabled = False
                    cmdUrl.disabled = False
                    cmdNameUrl.disabled = False
                    cmdCommand.value = ''
                    cmdNameCommand.value = ''
                    cmdUrl.value = ''
                    cmdNameUrl.value = ''
                    add.disabled = False
                    add1.disabled = False
                    add2.disabled = False
                    cmdReturnFirst.disabled = False

                    cmdConstruct.value = ''
                    cmdPathToFolder.value = ''
                    cmdNameApp.value = ''
                    cmdVoice.value = ''
                    cmdReturnFirst.value = ''

                    control.controls = [
                        icon,
                        cmdConstruct,
                        add
                    ]
                    page.update()

                elif (cmdConstruct.value == 'Открыть' or cmdConstruct.value == 'Закрыть') and (cmdNameApp.disabled == True):
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(""),
                        action="",
                    )
                    words = cmdVoice.value.split()
                    quoted_words = [f'"{word}"' for word in words]
                    output_string = ", ".join(quoted_words)
                    cmd_config = f'({output_string}): lambda:open_app("{cmdNameApp.value}", "{cmdPathToFolder.value}")'
                    add_command_to_file('utils\\commands.py', cmd_config)

                    page.snack_bar = ft.SnackBar(
                        ft.Text(
                            f"Command succsesful added to command list",
                            size=10,
                            weight=ft.FontWeight.BOLD
                        )
                    )
                    page.snack_bar.open = True
                    page.update()

                    cmdConstruct.disabled = False
                    cmdPathToFolder.disabled = False
                    cmdNameApp.disabled = False
                    cmdVoice.disabled = False
                    cmdNameCommand.disabled = False
                    cmdCommand.disabled = False
                    cmdUrl.disabled = False
                    cmdNameUrl.disabled = False
                    cmdCommand.value = ''
                    cmdNameCommand.value = ''
                    cmdUrl.value = ''
                    cmdNameUrl.value = ''
                    add.disabled = False
                    add1.disabled = False
                    add2.disabled = False

                    cmdConstruct.value = ''
                    cmdPathToFolder.value = ''
                    cmdNameApp.value = ''
                    cmdVoice.value = ''

                    control.controls = [
                        icon,
                        cmdConstruct,
                        add
                    ]
                    page.update()
            page.add(
                ft.Container(
                    content=ft.Text(
                        "Command constructor",
                        size=30,
                        weight=ft.FontWeight.BOLD
                    ),
                    padding=10,
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    content=commands,
                    padding=10,
                    expand=True,
                ),
                ft.Container(
                    content=commands1,
                    padding=10,
                    expand=True,
                ),
                ft.Row(
                    [
                        ft.Text(expand=True),
                        ft.IconButton(
                            icon=ft.icons.ADD_BOX,
                            tooltip="add cmd",
                            scale=1.5,
                            padding=15,
                            on_click=add_command
                        ),
                        ft.IconButton(
                            icon=ft.icons.CLEAR,
                            tooltip="clear",
                            scale=1.5,
                            padding=15,
                            on_click=clear_all
                        ),
                        ft.Text(expand=True)
                    ]
                )
            )

    page.navigation_bar = flet.NavigationBar(
        animation_duration=300,
        destinations=[
            flet.NavigationDestination(
                icon=flet.icons.HOME, 
                label="Home"
            ),
            flet.NavigationDestination(
                icon=flet.icons.VOICE_CHAT, 
                label="Chat"
            ),
            flet.NavigationDestination(
                icon=flet.icons.SETTINGS, 
                label="Settings"
            ),
            flet.NavigationDestination(
                icon=flet.icons.BOOKMARK_BORDER,
                selected_icon=flet.icons.BOOKMARK,
                label="Info",
            ),
            flet.NavigationDestination(
                icon=flet.icons.TERMINAL, 
                label="Commands"
            ),
        ],
        on_change=change_content
    )
    
    def close_banner(e):
        page.banner.open = False
        page.update()

    def show_banner(e):
        page.banner = Banner(
            bgcolor=colors.GREEN_200,
            leading=Icon(
                icons.GPP_GOOD, 
                color=colors.GREEN_100, 
                size=35
            ),
            content=Text(
                "The assistant has been succesfully launched. Have a nice time!", 
                size=20, 
                color=flet.colors.BLACK45
            ),
            actions=[
                ElevatedButton(
                    "Close", 
                    on_click=close_banner, 
                    bgcolor=flet.colors.GREEN_200,
                    color=flet.colors.BLACK45
                ),
            ],
        )
        page.banner.open = True
        page.update()

    #page.add(startWorkButton)
    #page.add(flet.Text())
    #page.add(cmd)

    page.add(cmd)
    page.add(widgets)
    update_color()
    if getConfigInfo('main', 'start') == 0:
        def open_dlg(e):
            try:
                page.dialog = DialogFirst
                DialogFirst.open = True
                page.update()
            except Exception as e:
                erorrBanner(e)

        def close_dlgf(e):
            try:
                DialogFirst.open = False
                page.update()
                open_program('utils\\config.json')
                open_program('utils\\config_info.txt')
            except Exception as e:
                erorrBanner(e)
        DialogFirst = flet.AlertDialog(
            modal=True,
            title=flet.Row(
                controls=[
                    Icon(
                        name=flet.icons.SETTINGS, 
                        
                        size=25
                    ), 
                    flet.Text(
                        "Complete your config.json file", 
                        size=25
                    )
                ]
            ),
            content=flet.Text(
                "• Please open config file and put all your data in\n• If you need add app for any actions use constructor",
                size=15
            ),
            actions=[
                flet.TextButton(
                    "open", 
                    on_click=close_dlgf
                ),
            ],
            actions_alignment=flet.MainAxisAlignment.END,
        )

        open_dlg(1)
        updateConfigname("utils/config.json", getConfigInfo('main', 'start')+1, "start", "main")

    if getConfigInfo('settings', 'Autoload') == 'True':
        startWorkSwitch.disabled = True
        startWorkSwitch.value = True
        page.update()
        startWorkAI(1)

flet.app(target=main)