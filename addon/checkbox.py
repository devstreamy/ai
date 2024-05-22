import flet, json
from modules.other import updateConfigname

def getConfigInfo(configValue, value):
        def load_config(file_path):
            with open(file_path, "r", encoding='utf-8') as file:
                return json.load(file)

        config = load_config("utils/config.json")
        return config[configValue][value]
    
def checkboxAutoload(e):
    if str(autoloadCheckbox.value) == "True":
        updateConfigname("utils/config.json", "True", "Autoload", "settings")
    elif str(autoloadCheckbox.value) == "False":
        updateConfigname("utils/config.json", "False", "Autoload", "settings")

def checkboxAccessToScreen(e):
    if str(accessToScreenCheckbox.value) == "True":
        updateConfigname("utils/config.json", "True", "CheckScreen", "settings")
    elif str(accessToScreenCheckbox.value) == "False":
        updateConfigname("utils/config.json", "False", "CheckScreen", "settings")

def checkboxAccessToCamera(e):
    if str(accessToCameraCheckbox.value) == "True":
        updateConfigname("utils/config.json", "True", "CheckCamera", "settings")
    elif str(accessToCameraCheckbox.value) == "False":
        updateConfigname("utils/config.json", "False", "CheckCamera", "settings")

def checkboxShowMicIndex(e):
    if str(ShowMicIndexCheckbox.value) == "True":
        updateConfigname("utils/config.json", "True", "show_mic", "other")
    elif str(ShowMicIndexCheckbox.value) == "False":
        updateConfigname("utils/config.json", "False", "show_mic", "other")

def checkboxTimeoutLogs(e):
    if str(timeoutLogsCheckbox.value) == "True":
        updateConfigname("utils/config.json", "True", "timeoutLogs", "other")
    elif str(timeoutLogsCheckbox.value) == "False":
        updateConfigname("utils/config.json", "False", "timeoutLogs", "other")

autoloadCheckbox = flet.Checkbox(label="Autoload",
    fill_color={
        flet.MaterialState.SELECTED: flet.colors.PURPLE_200,
    },
    width=160,
    scale=1.3,
    value=getConfigInfo("settings", "Autoload"),
    on_change=checkboxAutoload
)

accessToScreenCheckbox = flet.Checkbox(label="Access to screen",
    fill_color={
        flet.MaterialState.SELECTED: flet.colors.PURPLE_200,
    },
    width=200,
    scale=1.3,
    value=getConfigInfo("settings", "CheckScreen"),
    on_change=checkboxAccessToScreen
)

accessToCameraCheckbox = flet.Checkbox(label="Access to camera",
    fill_color={
    flet.MaterialState.SELECTED: flet.colors.PURPLE_200,
    },
    width=200,
    scale=1.3,
    value=getConfigInfo("settings", "CheckCamera"),
    on_change=checkboxAccessToCamera
)

voiceLogsCheckbox = flet.Checkbox(label="Voice logs",
    fill_color={
        flet.MaterialState.SELECTED: flet.colors.PURPLE_200,
    },
    width=130,
    scale=1.3,
    value=True, 
    disabled=True
)

timeoutLogsCheckbox = flet.Checkbox(label="Microphone logs",
    fill_color={
        flet.MaterialState.SELECTED: flet.colors.PURPLE_200,
    },
    width=180,
    scale=1.3,
    value=getConfigInfo("other", "timeoutLogs"),
    on_change=checkboxTimeoutLogs
)

ShowMicIndexCheckbox = flet.Checkbox(label="Show microphone index",
    fill_color={
        flet.MaterialState.SELECTED: flet.colors.PURPLE_200,
    },
    width=150,
    scale=1.3,
    value=getConfigInfo("other", "show_mic"),
    on_change=checkboxShowMicIndex
)