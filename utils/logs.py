from colorist import ColorRGB

gray = ColorRGB(120, 120, 120)
pink = ColorRGB(255, 204, 255)
purple = ColorRGB(178, 102, 255)
white = ColorRGB(255, 255, 255)
red = ColorRGB(255, 102, 102)
green = ColorRGB(51, 255, 51)
yellow = ColorRGB(255, 255, 102)
orange = ColorRGB(255, 128, 0)
orange_light = ColorRGB(255, 204, 153)
yellow_light = ColorRGB(255, 255, 0)
cyan = ColorRGB(102, 255, 255)

logNews = f"{gray}[{gray.OFF}{yellow_light}NEWS{yellow_light.OFF}{gray}]{gray.OFF} {yellow_light}"
logServer = f"{gray}[{gray.OFF}{orange}SERVER{orange.OFF}{gray}]{gray.OFF} {orange}"
logWindow = f"{gray}[{gray.OFF}{yellow}SCREEN{yellow.OFF}{gray}]{gray.OFF} {yellow}"
logUser = f"{gray}[{gray.OFF}{purple}USER{purple.OFF}{gray}]{gray.OFF} {purple}"
logDiscussion = f"{gray}[{gray.OFF}{cyan}DISCUSSION{cyan.OFF}{gray}]{gray.OFF} {cyan}"
logtranslate = f"{gray}[{gray.OFF}{orange_light}TRANSLATE{orange_light.OFF}{gray}]{gray.OFF} {orange_light}"
logSystem = f"{gray}[{gray.OFF}{pink}SYSTEM{pink.OFF}{gray}]{gray.OFF} {pink}"
logError = f"{gray}[{gray.OFF}{red}ERROR{red.OFF}{gray}]{gray.OFF} {red}"
logInfo = f"{gray}[{gray.OFF}{green}CONFIG{green.OFF}{gray}]{gray.OFF} {green}"
success = '\x1b[6;30;42m' + 'Success launch!' + '\x1b[0m'
stopColor = f"{white}"


successApp = 'Success launch!'
logInfoApp = f"[CONFIG] "
logSystemApp = f"[SYSTEM] "
logUserApp = "[USER] "