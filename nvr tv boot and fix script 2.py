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

# INCREASED DELAYS for 4K rendering
LOAD_TIMEOUT = 30  # Max time to wait for a page to load
SWITCH_INTERVAL = 10 

def kill_browsers():
    print("Cleaning up browser processes...")
    os.system("killall -9 vivaldi-bin firefox firefox-bin > /dev/null 2>&1")
    time.sleep(2)

def wait_for_page_ready(sw, sh):
    """Waits until the screen is no longer pure white, black, or 'Dead Bird' gray."""
    print("Waiting for page to render...")
    start_time = time.time()
    while time.time() - start_time < LOAD_TIMEOUT:
        r, g, b = pyautogui.pixel(int(sw/2), int(sh/2))
        
        # If it's NOT white (255,255,255), NOT black (0,0,0), and NOT dead bird gray (128ish)
        # we assume the camera feed has started rendering.
        if not (r > 240 and g > 240 and b > 240) and \
           not (r == 0 and g == 0 and b == 0) and \
           not (115 <= r <= 140):
            print(f"Page looks ready (RGB: {r},{g},{b}).")
            return True
        time.sleep(2)
    print("Load timeout reached. Proceeding anyway...")
    return False

def apply_frigate_layout(browser_type="vivaldi"):
    sw, sh = pyautogui.size()
    
    # Wait for the page to actually show video before clicking
    wait_for_page_ready(sw, sh)
    
    print(f"Applying layout formatting for {browser_type}...")
    pyautogui.click(100, 100)
    time.sleep(1)

    if browser_type == "vivaldi":
        pyautogui.press('f')
        time.sleep(5) # Animation buffer
    
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
    
    # 1. Launch Vivaldi
    print("\n--- Launching Vivaldi ---")
    v_flags = ["vivaldi", URL_VIVALDI, "--new-window", "--start-fullscreen", "--disable-dev-shm-usage"]
    subprocess.Popen(v_flags)
    # Wait for Vivaldi specifically
    apply_frigate_layout(browser_type="vivaldi")

    # 2. Launch Firefox
    print("\n--- Launching Firefox ---")
    f_flags = ["firefox", "--kiosk", "--private-window", URL_FIREFOX]
    subprocess.Popen(f_flags)
    # Wait for Firefox specifically
    apply_frigate_layout(browser_type="firefox")
    
    print("Setup complete. Entering loop...")

def is_ui_crashed(sw, sh):
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
    
    while True:
        # PING-PONG SWITCH
        print(f"Viewing current camera for {SWITCH_INTERVAL}s...")
        time.sleep(SWITCH_INTERVAL)
        
        print("Switching windows (Alt+Tab)...")
        pyautogui.hotkey('alt', 'tab')
        
        # Grace period for the OS to actually bring the other window forward
        time.sleep(3) 
        
        # Check health of the NOW ACTIVE window
        if is_ui_crashed(sw, sh):
            print("Crash detected on active window. Relaunching all...")
            launch_and_setup()
        else:
            print("View is healthy.")

if __name__ == "__main__":
    main()