#!/usr/bin/env python3
import subprocess
import time
import pyautogui
import os

# Titles from your wmctrl -l output
TITLE_VIVALDI = "with camera"
TITLE_FIREFOX = "mozilla firefox"

URL_VIVALDI = "http://192.168.1.12:5000/cameras/Living_room"
URL_FIREFOX = "http://192.168.1.12:5000/cameras/Living_room_2"

# TIMING - Higher delays for 4K stability
LOAD_WAIT = 20
SETTLE_WAIT = 8 

def kill_browsers():
    print("Force cleaning environment...")
    os.system("killall -9 vivaldi-bin firefox firefox-bin > /dev/null 2>&1")
    time.sleep(3)

def switch_windows(target_title):
    """Uses the exact title substrings from your wmctrl output."""
    print(f"OS: Focusing window containing '{target_title}'...")
    os.system(f"wmctrl -a '{target_title}'")

def apply_frigate_layout(browser_name):
    sw, sh = pyautogui.size()
    print(f"Applying layout to {browser_name}...")
    
    # 1. Click to gain focus (Top edge, center)
    pyautogui.click(sw / 2, 10)
    time.sleep(2)

    # 2. Toggle Fullscreen
    if "firefox" in browser_name.lower():
        print("Sending F11 to Firefox...")
        pyautogui.press('f11')
        time.sleep(3)
    
    print(f"Sending 'f' to {browser_name}...")
    pyautogui.press('f')
    
    # 3. CRITICAL: Wait for the zoom animation to finish completely
    print(f"Waiting {SETTLE_WAIT}s for animation to settle...")
    time.sleep(SETTLE_WAIT)

    # 4. The Nudge (Extreme right edge)
    print(f"Executing nudge for {browser_name}...")
    pyautogui.moveTo(sw - 2, sh / 4)
    pyautogui.mouseDown(button='left')
    pyautogui.moveTo(sw - 2, (sh / 4) - 60, duration=1.5)
    pyautogui.mouseUp(button='left')
    pyautogui.moveTo(sw - 1, sh - 1)

def launch_and_setup():
    kill_browsers()
    
    # --- VIVALDI ---
    print("\n--- Initializing Vivaldi ---")
    v_flags = ["vivaldi", f"--app={URL_VIVALDI}", "--start-fullscreen", "--no-first-run"]
    subprocess.Popen(v_flags)
    time.sleep(LOAD_WAIT)
    apply_frigate_layout("Vivaldi")

    # --- FIREFOX ---
    print("\n--- Initializing Firefox ---")
    # Launching normally to allow wmctrl to see 'mozilla firefox' in title
    subprocess.Popen(["firefox", "--new-window", URL_FIREFOX])
    time.sleep(LOAD_WAIT)
    apply_frigate_layout("Firefox")
    
    print("\n--- All setups complete. Entering Loop. ---")

def main():
    launch_and_setup()
    
    # Start the loop
    current_in_front = "Firefox"
    
    while True:
        print(f"Displaying {current_in_front}. Waiting 10s...")
        time.sleep(10)
        
        # Toggle and Switch
        if current_in_front == "Firefox":
            switch_windows(TITLE_VIVALDI)
            current_in_front = "Vivaldi"
        else:
            switch_windows(TITLE_FIREFOX)
            current_in_front = "Firefox"
        
        # Give the OS a moment to bring the window forward before the next loop
        time.sleep(2)

if __name__ == "__main__":
    main()