#!/usr/bin/env python3
import subprocess
import time
import pyautogui
import os

# Frigate URLs
BASE_URL = "http://192.168.1.12:5000"
URL_VIVALDI = "http://192.168.1.12:5000/cameras/Living_room"
URL_FIREFOX = "http://192.168.1.12:5000/cameras/Living_room_2"

# TIMING ADJUSTMENTS
INITIAL_LOAD_WAIT = 15  
NUDGE_DELAY = 5         
SWITCH_INTERVAL = 10 

def kill_browsers():
    print("Cleaning up processes...")
    os.system("killall -9 vivaldi-bin firefox firefox-bin > /dev/null 2>&1")
    time.sleep(3)

def wait_for_video(sw, sh):
    """Wait for the screen to stop being white/black/gray."""
    print("Waiting for video feed to render...")
    start_time = time.time()
    while time.time() - start_time < 30:
        # Check slightly off-center to avoid the black grid lines between the 9 cameras
        r, g, b = pyautogui.pixel(int(sw/3), int(sh/3))
        if not (r > 240 and g > 240 and b > 240) and not (r == 0 and g == 0 and b == 0) and not (115 <= r <= 140):
            time.sleep(NUDGE_DELAY) 
            return True
        time.sleep(1)
    print("Video wait timed out, proceeding anyway...")
    return False

def apply_frigate_layout(browser_name):
    sw, sh = pyautogui.size()
    
    # 1. Wait for video
    wait_for_video(sw, sh)
    
    print(f"Applying layout to {browser_name}...")
    
    # 2. THE FIX: Force focus with a SAFE click (Bottom-Right Corner)
    # This ensures we click the background/margins, NOT a camera feed.
    pyautogui.click(sw - 5, sh - 5)
    time.sleep(1)

    # 3. Toggle Frigate Fullscreen
    pyautogui.press('f')
    time.sleep(5) 

    # 4. The Nudge
    pyautogui.click(sw - 5, sh - 5)
    time.sleep(1) 
    pyautogui.moveTo(sw - 20, sh / 5)
    pyautogui.mouseDown(button='left')
    pyautogui.moveTo(sw - 20, (sh / 5) - 20, duration=1.5)
    pyautogui.mouseUp(button='left')
    pyautogui.moveTo(sw - 1, sh - 1)
    print(f"{browser_name} ready.")

def launch_and_setup():
    kill_browsers()
    
    # --- VIVALDI PHASE ---
    print("\n--- Phase 1: Vivaldi ---")
    subprocess.Popen(["vivaldi", URL_VIVALDI, "--new-window", "--start-fullscreen", "--disable-dev-shm-usage"])
    time.sleep(INITIAL_LOAD_WAIT)
    apply_frigate_layout("Vivaldi")

    # --- FIREFOX PHASE ---
    print("\n--- Phase 2: Firefox ---")
    subprocess.Popen(["firefox", "--kiosk", URL_FIREFOX])
    time.sleep(INITIAL_LOAD_WAIT)
    apply_frigate_layout("Firefox")
    
    print("\n--- All Systems Ready. Entering Loop. ---")

def main():
    sw, sh = pyautogui.size()
    launch_and_setup()
    
    while True:
        print(f"Viewing current camera ({SWITCH_INTERVAL}s)...")
        time.sleep(SWITCH_INTERVAL)
        
        print("Switching windows...")
        pyautogui.hotkey('alt', 'tab')
        time.sleep(4) 
        
        # Health check: off-center check for the dead bird
        r, g, b = pyautogui.pixel(int(sw/3), int(sh/3))
        if 115 <= r <= 140 and 115 <= g <= 140:
            print("Crash detected! Restarting setup...")
            launch_and_setup()

if __name__ == "__main__":
    main()