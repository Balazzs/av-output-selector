from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from pathlib import Path
import json
import webbrowser
import subprocess
from time import sleep

configPath     = Path (__file__).parent / "config.json"
displayExePath = Path (__file__).parent / "displayconfig.exe"

def create_image():
    # Generate an image and draw a pattern
    image = Image.new('RGBA', (32, 32), (0, 0, 0, 128))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 0, 32, 16), fill="red")
    dc.rectangle((0, 16, 16, 32), fill="blue")

    return image

exit = False
settings = {}

def close ():
    global exit, icon
    exit = True
    icon.stop ()

def set_display (displays):
    params = [x for display, on_off in displays.items() for x in [display, on_off]]
    completedProcess = subprocess.run ([displayExePath] + params)
    if completedProcess.returncode != 0:
        icon.notify ("Error while setting displays")

def set_audio (device_id):
    pass

def set_mode (mode):
    icon.notify(f"Setting mode to {mode['name']}")
    sleep (1)
    set_display (mode["displays"])
    sleep (2)
    set_audio (mode["audio"])
    

def load_menuitems ():
    global settings, icon
    try:
        settings = json.loads(configPath.read_text ())
        
        set_mode_generator = lambda mode: lambda: set_mode (mode)
        
        return [MenuItem (mode["name"], set_mode_generator (mode)) for mode in settings["modes"]]
    except:
        icon.notify ("Error loading config file")

def make_icon ():
    global icon
    icon = Icon ('test',
                create_image(),
                menu = Menu (*load_menuitems(),
                             Menu.SEPARATOR,
                             MenuItem ("Edit config", lambda: webbrowser.open (configPath)),
                             MenuItem ("Info",        lambda: icon.notify ("AudioVisualConfigurator v0.0 by Balazzs")),
                             MenuItem ("Reload",      lambda: icon.stop ()),
                             MenuItem ("Exit",        close)))
    icon.run()

while not exit:
    make_icon ()
