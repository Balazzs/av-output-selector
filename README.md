# av-output-selector

A small tool to select a proper AudioVisual setup, correct displays (with correct layout possibly) + proper Default audio playback device for various scenarios (e.g. watching movie on TV vs 2 monir programming + youtube on TV, etc.).

My problem is that i have 2 monitors and a TV for displays and a speaker, a monitor speaker, a TV speaker, and a headset for audio outputs.
Unfortunately Windows isn't always on the top when I'm selecting various device combinations.
Extended and PC Screen Only mode are good for 2 monitor (monitor + TV) setups, but not really what I need for my problem, I usually want 2 monitors on and the TV off, except when I'm watching TV, then I want the TV on with sound. But sometimes I want the TV on with speaker sounds.

I can define various scenarios, e.g. Movie mode, when I definitely know what I want, but I have to set display settings, select default audio devices and so on, what I want is a single click solution that is always available on my system tray.
This project is meant to be that.

## DisplayConfig

Enables / Disables displays by name. Uses windows API. Made by a large amount of copy-paste, google searches and a lot of documentation reading. PhysicalMonitor and HMONITOR solutions were also considered but this is the easiest solution, looping through all the possible DISPLAYCONFIG_PATH_INFO-s from QueryDisplayConfig and getting devicve info with DisplayConfigGetDeviceInfo then calling a SetDisplayConfig on the modified paths.

Requires Windows SDK (and maybe WDK ?).

## Default output device setter

Get https://github.com/frgnca/AudioDeviceCmdlets.

```PowerShell
Install-Module -Name AudioDeviceCmdlets
```

Just get your (enabled) device's ID from
```PowerShell
Get-AudioDevice -List
```

And set it as default with:
```PowerShell
Set-AudioDevice -ID "{0.0.0.00000000}.{876a2076-43a6-4e0d-92a9-49fcfa580025}"
```

## Tray icon python script

```
pip3 install pystray
```
Also build the DisplayConfig project and copy displayconfig.exe next to the script.

Edit the script, displays are dictionaries of monitor name - "on"/"off", the default audio device ID can be determined from [Default output device setter](#default-output-device-setter) by Listing.
