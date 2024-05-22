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
import os
import tempfile
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
from modules.msg import (send_message_telegram, telegram_contacts_thread)
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
                           answerPathIMAGE)
from modules.world import (get_weather)
from modules.window import (recordScreen_thread,)
from modules.protocols import (Protocol21Thread)
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

q = queue.Queue()

def q_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


show_mic = show_micConfig
check_screen = check_screenConfig
voiceLoging = voiceLogingConfig
FullLogs = FullLogsConfig

recognizer = sr.Recognizer()
recognized_phrases = []
installed = None
if getConfigInfo('main', "chatgpt") == 'gpt-4o':
    all_paths = list_all_folders()

def process_command(command_text):
    from utils.commands import commands
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

    for keywords, action in commands.items():
        if all(keyword in command_text.lower() for keyword in keywords):
            threading.Thread(target=action).start()
            play_random_phrase(25)
            return

LIGHT_SEED_COLOR = colors.DEEP_ORANGE
DARK_SEED_COLOR = colors.DEEP_PURPLE_200

cmd = TextField(
            label="CMD",
            multiline=True,
            min_lines=1,
            max_lines=10)

def main(page: Page):

    infoComputer = flet.Text('info lol', size=15)
    page.title = "Voice assistant"
    page.theme_mode = "light"
    page.theme = theme.Theme(color_scheme_seed=LIGHT_SEED_COLOR, use_material3=True)
    page.dark_theme = theme.Theme(color_scheme_seed=DARK_SEED_COLOR, use_material3=True)
    page.window_maximizable = False
    page.window_max_width = 1520
    page.window_max_height = 720
    page.update()

    def toggle_theme_mode(e):
        try:
            page.theme_mode = "dark" if page.theme_mode == "light" else "light"
            lightMode.icon = (
                icons.WB_SUNNY_OUTLINED if page.theme_mode == "light" else icons.WB_SUNNY
            )
        
            page.update()
        except Exception as e:
            erorrBanner(e)

    lightMode = IconButton(
        icons.WB_SUNNY_OUTLINED if page.theme_mode == "light" else icons.WB_SUNNY,
        on_click=toggle_theme_mode,
    )

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
                updateConfigname("utils/config.json", 0, "mic_index", "other")
                updateConfigname("utils/config.json", 'True', "mic_id", "other")
                updateConfigname("utils/config.json", 1, "timeout", "other")
            if e.control.selected == False:
                updateConfigname("utils/config.json", 2, "mic_index", "other")
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
                    color=flet.colors.PURPLE_200, 
                    size=25
                ), 
                flet.Text(
                    "All protocols", 
                    size=25
                )
            ]
        ),
        content=flet.Text(
            "• Protocol 21 (Make backup on server)\n• Protocol 10 (delete all from computer)",
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
                    color=flet.colors.PURPLE_200, 
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
        thread.start()

    settingsShow = IconButton(icon=icons.ADD_MODERATOR, on_click=open_dlg)
    page.padding = 30

    page.appbar = AppBar(
        leading=Icon(icons.ACCOUNT_CIRCLE),
        leading_width=60,
        title=Text(f"Voice assistant"),
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
            style=flet.ButtonStyle(color={"selected": flet.colors.PURPLE_200, "": flet.colors.PURPLE_200}),
            disabled=True,
            tooltip="Disabled, function not maked right now"),
        IconButton(
            icon=flet.icons.MIC,
            selected_icon=flet.icons.MIC_OFF,
            icon_size=40,
            on_click=mic_use,
            selected=getConfigInfo('other', 'mic_id'),
            style=flet.ButtonStyle(color={"selected": flet.colors.PURPLE_200, "": flet.colors.PURPLE_200})),

            ], alignment=flet.MainAxisAlignment.CENTER )

    def startWorkAI(e):
        from modules.other import show_current_datetime
        
        startWorkButton.disabled = True
        show_banner(1)
        cmd.value = cmd.value+successApp+show_current_datetime()
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
        print(logInfo+f"Configuration.\n"+logInfo+f"Version app :: {versionConfig}     | Name voice support :: {getConfigInfo('main', 'name')}\n"+logInfo+f"CheckScreen :: {check_screenConfig}    | CheckCamera :: {check_cameraConfig}\n"+logInfo+f"Microphone index :: {mic_indexConfig}  | Microphones show :: {show_micConfig}\n"+logInfo+f"Voice loging :: {voiceLogingConfig}   | FullLogs :: {FullLogsConfig}\n\n"+logInfo+f"Protocol 21 :: {protocols21}    | :: ")
        cmd.value = cmd.value+'\n'+logInfoApp+f"Configuration.\n"+logInfoApp+f"Version app :: {versionConfig}     | Name voice support :: {getConfigInfo('main', 'name')}\n"+logInfoApp+f"CheckScreen :: {check_screenConfig}    | CheckCamera :: {check_cameraConfig}\n"+logInfoApp+f"Microphone index :: {mic_indexConfig}  | Microphones show :: {show_micConfig}\n"+logInfoApp+f"Voice loging :: {voiceLogingConfig}   | FullLogs :: {FullLogsConfig}\n\n"+logInfoApp+f"Protocol 21 :: {protocols21}    | :: "
        page.update()
        if protocols21 == "True":
            print(logSystem+'протокол 21 был успешно запущен'+stopColor+show_current_datetime())
            Protocol21Thread()
        telegram_contacts_thread()
        cmd.value = cmd.value+'\n'+logSystemApp+'протокол 21 был успешно запущен'+show_current_datetime()
        page.update()

        # if getConfigInfo('main', 'recogniz') == "vosk":
        #     def Vosklisten():
        #         if getConfigInfo('vosk', 'model') == 'small_ru':
        #             model = vosk.Model(lang="ru")
        #         elif getConfigInfo('vosk', 'model') == 'big_ru':
        #             model = vosk.Model('modules/voice/vosk-model-ru-0.42')
        #         samplerate = 16000
        #         device = getConfigInfo('other', 'mic_index')
        #         with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device, dtype='int16', channels=1, callback=q_callback):
        #             try:
        #                 print(logUser+"прослушиваю микрофон"+stopColor)
        #                 rec = vosk.KaldiRecognizer(model, samplerate)
        #                 while True:
        #                     #cmd.value = cmd.value+'\n'+logUserApp+"прослушиваю микрофон"
        #                     data = q.get()
        #                     if rec.AcceptWaveform(data):
        #                         if getConfigInfo('other', 'mic_index') == 2:
        #                             text = json.loads(rec.Result())["text"]
        #                             if text == "":
        #                                 pass
                                        
        #                             else:
        #                                 saveTextfile('logs.txt', text, True)
        #                                 print(logUser+f"вы сказали :: {text}"+stopColor) ; recognized_phrases.append(text)
        #                                 cmd.value = cmd.value+'\n'+logUserApp+"вы сказали :: " + text
        #                                 page.update()
        #                                 process_command(text)

        #             except Exception as e:
        #                 print(e)
        #     Vosklisten()
        if getConfigInfo('main', 'recogniz') == "speach_recognize":
            def recognize_speech():
                from modules.chatgpt import chatWithImage
                recognizer = sr.Recognizer()
                while True:
                    with sr.Microphone(device_index=getConfigInfo('other', 'mic_index')) as source:
                        try:
                            print(logSystem+"прослушиваю микрофон" + show_current_datetime())
                            recognizer.adjust_for_ambient_noise(source)
                            audio = recognizer.listen(source, timeout=getConfigInfo('other', 'timeout'))

                            # Создание временного WAV файла
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
                                temp_wav_file.write(audio.get_wav_data())
                                temp_wav_file_name = temp_wav_file.name

                            try:
                                with sr.AudioFile(temp_wav_file_name) as source:
                                    audio_data = recognizer.record(source)
                                    text = recognizer.recognize_google(audio_data, language="ru-RU")

                                saveTextfile('logs.txt', text, True)
                                print(logSystem+"вы сказали :: " + text + show_current_datetime())
                                recognized_phrases.append(text)

                                def get():
                                    answer = chatWithImage(text)
                                    if answer != "Answ0x01":
                                        answerPathIMAGE(answer, all_paths)
                                if getConfigInfo('main', "chatgpt") == 'gpt-4o':
                                    thread = threading.Thread(target=get, args=())
                                    thread.start()

                                process_command(text)
                            finally:
                                os.remove(temp_wav_file_name)

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

            recognize_speech()
        
    page.fonts = {
            "Crushed": "https://github.com/google/fonts/raw/main/apache/crushed/Crushed-Regular.ttf"
        }
    def changedName(e):
        updateConfigname("utils/config.json", e.control.value, "name", "main")
        page.update()

    def changedGPT(e):
        updateConfigname("utils/config.json", e.control.value, "chatgpt", "main")
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

    settingsBar1 = flet.Row(
        controls=[
            Icon(
                name=flet.icons.SETTINGS, 
                color=flet.colors.PURPLE_200, 
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
        alignment=flet.MainAxisAlignment.CENTER)

    settingsBar3 = flet.Row(
        controls=[
            nameConfig, 
            chatGPT_Version
        ], 
        alignment=flet.MainAxisAlignment.CENTER) 
       
    startWorkButton = ElevatedButton(
        "Start work", 
        disabled=False, 
        on_click=startWorkAI)

    def change_content(e):

        page.controls.clear()
        nav_dest = e.control.selected_index 

        if nav_dest == 0:
            page.padding = 30
            page.add(
                Text(
                    "Welcome to voice assistant", 
                    style="displayLarge"
                ),
                Text(
                    "  This voice assistant can help you with any of your actions. Answer any question and maintain a dialogue", 
                    style="titleMedium"
                ))
            page.add(startWorkButton)
            page.add(flet.Text())
            page.add(cmd)

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
                        color=flet.colors.PURPLE_200, 
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
                        color=flet.colors.PURPLE_200, 
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
                        color=flet.colors.PURPLE_200, 
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
                        color=flet.colors.PURPLE_200, 
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
                        color=flet.colors.PURPLE_200, 
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
                        color=flet.colors.PURPLE_200, 
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
                        color=flet.colors.PURPLE_200, 
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
                        color=flet.colors.PURPLE_200, 
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
                    width=1000,
                    color=ft.colors.BLACK87),
                    border=ft.border.all(1, ft.colors.AMBER),
                    bgcolor=ft.colors.WHITE,
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
                        width=1000,
                        color=ft.colors.BLACK87),
                        border=ft.border.all(1, ft.colors.AMBER),
                        bgcolor=ft.colors.WHITE,
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
    page.add(
        Text(
            "Welcome to voice assistant", 
            style="displayLarge"
        ),
        Text(
            "  This voice assistant can help you with any of your actions. Answer any question and maintain a dialogue", 
            style="titleMedium"
            )
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

    page.add(startWorkButton)

    page.add(flet.Text())
    page.add(cmd)

flet.app(target=main)