#!/usr/bin/env python3

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from pathlib import Path
import json
import webbrowser
import subprocess
import re
from fnmatch import fnmatch
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

def close ():
    global exit, icon
    exit = True
    icon.stop ()

def set_display (displays):
    params = [x for display, on_off in displays.items() for x in [display, on_off]]
    completedProcess = subprocess.run ([displayExePath] + params)
    if completedProcess.returncode != 0:
        icon.notify ("Error while setting displays")

def parse_audio_config():
    completedProcess = subprocess.run(["PowerShell", "Get-AudioDevice", "-List"], capture_output=True, text=True)
    device_strings = completedProcess.stdout.strip().split ("\n\n")
    pattern = r"^(.*):(.*)$"

    devices = []

    for device_string in device_strings:
        devices.append ({k.strip() : v.strip() for k,v in re.findall (pattern, device_string, flags=re.MULTILINE)})

    return devices

def load_playback_menu ():
    devices = parse_audio_config ()
    set_audio_generator = lambda device_id: lambda: set_audio (device_id)
    return MenuItem ("Sound", Menu (*[MenuItem (device["Name"], set_audio_generator (device["ID"])) for device in devices if device["Type"] == "Playback"]))

def get_device_id (name):
    devices = parse_audio_config ()
    devices_with_name = [device for device in devices if fnmatch(device["Name"], name) and device["Type"] == "Playback"]
    if len(devices_with_name) == 0:
        icon.notify(f"Error: No device audio playback device found with name \"{name}\"")
        return None
    elif len(devices_with_name) > 1:
        icon.notify(f"Warning: Multiple audio playback devices found with name \"{name}\"\nPicking the first one")
    return devices_with_name[0]["ID"]

def set_audio (device_id):
    id_pattern = r"{[0-9a-fA-F.]*}.{[0-9a-fA-F\-]*}"
    if not re.match(id_pattern, device_id):
        device_id = get_device_id (device_id)
        if device_id is None:
            return

    completedProcess = subprocess.run (["PowerShell.exe", "Set-AudioDevice", "-ID", f'"{device_id}"'])
    if completedProcess.returncode != 0:
        icon.notify ("Error setting default audio playback device")

def set_mode (mode):
    icon.notify(f"Setting mode to {mode['name']}")
    set_display (mode["displays"])
    sleep (1)
    set_audio (mode["audio"])


def load_menuitems ():
    try:
        settings = json.loads(configPath.read_text ())
        
        set_mode_generator = lambda mode: lambda: set_mode (mode)
        
        return [MenuItem (mode["name"], set_mode_generator (mode)) for mode in settings["modes"]]
    except:
        global icon
        icon.notify ("Error loading config file")

def make_icon ():
    global icon
    icon = Icon ('test',
                create_image(),
                menu = Menu (*load_menuitems(),
                             Menu.SEPARATOR,
                             load_playback_menu (),
                             Menu.SEPARATOR,
                             MenuItem ("Edit config", lambda: webbrowser.open (configPath)),
                             MenuItem ("Info",        lambda: icon.notify ("AudioVisualConfigurator v0.0 by Balazzs")),
                             MenuItem ("Reload",      lambda: icon.stop ()),
                             MenuItem ("Exit",        close)))
    icon.run()

while not exit:
    make_icon ()
