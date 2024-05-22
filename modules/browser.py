import os, pyautogui 

def edge_openUrl(url):
    os.system(f"start msedge {url}")

def chrome_openUrl(url):
    os.system(f"start chrome {url}")

def scroll_down():
    pyautogui.scroll(-320)

def scroll_up():
    pyautogui.scroll(320)

## Youtube ##
def stop_video():
    pyautogui.hotkey('k')

def next_video():
    pyautogui.hotkey('shift' + 'n')

def fullscreen_video():
    pyautogui.hotkey('f')
