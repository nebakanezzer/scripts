#!/usr/bin/env python3
import subprocess
import time
import pyautogui
import urllib.request
import urllib.error
import os

# Frigate URLs
BASE_URL = "http://192.168.1.12:5000"
URL_VIVALDI = "http://192.168.1.12:5000/cameras/Living_room"
URL_FIREFOX = "http://192.168.1.12:5000/cameras/Living_room_2?toolbar=0"

LOAD_DELAY = 20 # Give the hardware more time to breathe on initial startup
SWITCH_INTERVAL = 10 

def kill_browsers():
    """Wipes the slate clean for both browsers."""
    print("Cleaning up browser processes...")
    os.system("killall -9 vivaldi-bin firefox firefox-bin > /dev/null 2>&1")
    time.sleep(2)

def apply_frigate_layout(browser_type="vivaldi"):
    """
    Applies the layout lock, with an extra focus-break for Firefox.
    """
    print(f"Applying layout formatting for {browser_type}...")
    
    # 1. Initial click to ensure the window has focus
    pyautogui.click(100, 100)
    time.sleep(1)

    # 2. Toggle Fullscreen
    pyautogui.press('f')
    
    # IMPORTANT: Wait for the fullscreen animation to finish
    # If this is too fast, the next click won't register correctly.
    time.sleep(6) 

    sw, sh = pyautogui.size()

    # 3. THE FIX: Click a neutral "Empty" space to drop the camera focus.
    # In the Frigate dashboard, clicking the very top edge usually clears selection.
    print("Clearing single-camera focus...")
    pyautogui.click(sw / 2, 10) 
    time.sleep(1)

    # The Nudge
    start_x = sw - 20
    start_y = sh / 5
    target_y = start_y - 20 
    
    pyautogui.moveTo(start_x, start_y)
    pyautogui.mouseDown(button='left')
    pyautogui.moveTo(start_x, target_y, duration=1.2)
    pyautogui.moveTo(start_x, target_y + 1, duration=0.1)
    
    time.sleep(0.8)
    pyautogui.mouseUp(button='left')
    
    # Move mouse out of the way
    pyautogui.moveTo(sw - 5, sh - 5)
    print(f"{browser_type} layout locked and focus cleared.")

def launch_and_setup():
    kill_browsers()

    # 1. Vivaldi
    v_flags = ["vivaldi", URL_VIVALDI, "--new-window", "--start-fullscreen", "--disable-dev-shm-usage"]
    subprocess.Popen(v_flags)
    time.sleep(LOAD_DELAY)
    apply_frigate_layout(browser_type="vivaldi")

    # 2. Firefox
    # We use --kiosk to hide the URL bar, then F11 in the script to ensure the canvas fills the TV
    f_flags = ["firefox", "--kiosk", URL_FIREFOX]
    subprocess.Popen(f_flags)
    time.sleep(LOAD_DELAY)
    apply_frigate_layout(browser_type="firefox")

def is_ui_crashed(sw, sh):
    """Tolerant check for gray/black screens."""
    points = [(int(sw/2), int(sh/4)), (int(sw/4), int(sh/2)), (int(sw*0.75), int(sh*0.75))]
    for x, y in points:
        r, g, b = pyautogui.pixel(x, y)
        if r == 0 and g == 0 and b == 0: return True # Black
        diff = max(abs(r-g), abs(r-b), abs(g-b))
        if diff <= 10 and 115 <= r <= 140: return True # Gray Dead Bird
    return False

def main():
    # 1. Initial Launch
    launch_and_setup()
    
    sw, sh = pyautogui.size()
    print(f"\nStarting cycle loop. Switching every {SWITCH_INTERVAL}s...")
    
    while True:
        # 2. Wait for the camera to be viewed
        time.sleep(SWITCH_INTERVAL)

        # 3. Switch to the other browser
        pyautogui.hotkey('alt', 'tab')

        # 4. CRITICAL: Wait for the page to render before checking for a crash
        # This prevents the script from thinking a loading screen is a crash
        time.sleep(4) 

        # 5. Check health
        if not is_network_up():
            print("Network down. Waiting...")
            while not is_network_up():
                time.sleep(5)
            launch_and_setup() # Recover after network return

        elif is_ui_crashed(sw, sh):
            # We only trigger a full relaunch if we are CERTAIN it's the dead bird/black screen
            print("Confirmed UI Crash detected. Relaunching...")
            launch_and_setup()

if __name__ == "__main__":
    main()

