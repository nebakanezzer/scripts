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

LOAD_TIMEOUT = 30 
SWITCH_INTERVAL = 10 
# How many times to see a "black/gray" screen before killing the browser
MAX_CRASH_SIGHTINGS = 3 

def kill_browsers():
    print("Cleaning up browser processes...")
    os.system("killall -9 vivaldi-bin firefox firefox-bin > /dev/null 2>&1")
    time.sleep(2)

def wait_for_page_ready(sw, sh):
    print("Waiting for video pixels to appear...")
    start_time = time.time()
    while time.time() - start_time < LOAD_TIMEOUT:
        r, g, b = pyautogui.pixel(int(sw/2), int(sh/2))
        # If it's NOT white, black, or dead-bird gray
        if not (r > 240 and g > 240 and b > 240) and \
           not (r == 0 and g == 0 and b == 0) and \
           not (115 <= r <= 140):
            return True
        time.sleep(2)
    return False

def apply_frigate_layout(browser_type="vivaldi"):
    sw, sh = pyautogui.size()
    wait_for_page_ready(sw, sh)
    
    print(f"Applying layout for {browser_type}...")
    pyautogui.click(100, 100)
    time.sleep(1)

    if browser_type == "vivaldi":
        pyautogui.press('f')
        time.sleep(5) 
    
    # The Nudge
    pyautogui.click(sw - 5, sh - 5)
    time.sleep(1) 
    pyautogui.moveTo(sw - 20, sh / 5)
    pyautogui.mouseDown(button='left')
    pyautogui.moveTo(sw - 20, (sh / 5) - 20, duration=1.5)
    pyautogui.mouseUp(button='left')
    pyautogui.moveTo(sw - 5, sh - 5)

def launch_and_setup():
    kill_browsers()
    
    # 1. Vivaldi
    subprocess.Popen(["vivaldi", URL_VIVALDI, "--new-window", "--start-fullscreen", "--disable-dev-shm-usage"])
    apply_frigate_layout(browser_type="vivaldi")

    # 2. Firefox - Added media.ffmpeg.vaapi.enabled for better Linux hardware video support
    subprocess.Popen(["firefox", "--kiosk", "--private-window", URL_FIREFOX])
    apply_frigate_layout(browser_type="firefox")
    
    print("System Online.")

def is_ui_crashed(sw, sh):
    """Checks for black screen or dead bird."""
    points = [(int(sw/2), int(sh/4)), (int(sw/4), int(sh/2)), (int(sw*0.75), int(sh*0.75))]
    for x, y in points:
        r, g, b = pyautogui.pixel(x, y)
        if r == 0 and g == 0 and b == 0: return True
        diff = max(abs(r-g), abs(r-b), abs(g-b))
        if diff <= 10 and 115 <= r <= 140: return True 
    return False

def main():
    launch_and_setup()
    sw, sh = pyautogui.size()
    
    crash_counter = 0
    
    while True:
        time.sleep(SWITCH_INTERVAL)
        pyautogui.hotkey('alt', 'tab')
        time.sleep(3) 
        
        if is_ui_crashed(sw, sh):
            crash_counter += 1
            print(f"Warning: Potential stale stream detected ({crash_counter}/{MAX_CRASH_SIGHTINGS})")
            
            # Soft Recovery: Just refresh the page instead of killing everything
            pyautogui.hotkey('ctrl', 'r') 
            time.sleep(5) 
            
            if crash_counter >= MAX_CRASH_SIGHTINGS:
                print("Hard Recovery: Browser is stuck. Relaunching...")
                launch_and_setup()
                crash_counter = 0
        else:
            # If we see a good frame, reset the counter completely
            if crash_counter > 0:
                print("Stream recovered. Resetting watchdog.")
            crash_counter = 0

if __name__ == "__main__":
    main()