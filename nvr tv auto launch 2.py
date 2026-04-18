#!/usr/bin/env python3
import subprocess
import time
import pyautogui
import os

# frigate non-auth addy
URL = "http://192.168.1.12:5000"
LOAD_DELAY = 10 

def main():
    print("Cleaning up old Vivaldi processes...")
    os.system("pkill -f vivaldi") 
    time.sleep(2) 

    # Get screen dimensions dynamically
    screen_width, screen_height = pyautogui.size()

    print("Launching Vivaldi with forced geometry and clean profile...")
    subprocess.Popen([
        "vivaldi", 
        "--incognito", 
        "--kiosk", 
        f"--window-size={screen_width},{screen_height}",
        "--window-position=0,0",
        "--user-data-dir=/tmp/frigate_kiosk", 
        URL
    ])

    print(f"Waiting {LOAD_DELAY}s for UI to render...")
    time.sleep(LOAD_DELAY)

    # 1. INITIAL FOCUS (Safe Zone)
    # We click the top-center of the screen (y=20 pixels down). 
    # This hits the Frigate top navigation bar, guaranteeing we don't accidentally click a camera feed.
    print("Clicking top navigation bar to ensure focus...")
    pyautogui.click(screen_width // 2, 20)
    time.sleep(1)

    # 2. THE FAILSAFE: FORCE BROWSER FULLSCREEN
    print("Pressing F11 failsafe...")
    pyautogui.press('f11')
    time.sleep(2)

    # 3. TRIGGER FRIGATE FULLSCREEN
    print("Sending 'f' for Frigate UI Fullscreen...")
    pyautogui.press('f')
    
    # 4. THE "STABILIZATION" PAUSE
    time.sleep(4) 

    # 5. SAFE SCROLLING (Replacing the Mouse Drag)
    print("Scrolling down slightly using safe keystrokes...")
    # Using the down arrow avoids clicking on cameras entirely. 
    # Increase or decrease the range(3) number to scroll more or less.
    for _ in range(3):
        pyautogui.press('down')
        time.sleep(0.2)

    # 6. PARK THE MOUSE (Safely away from the taskbar)
    # We park it on the far right edge, exactly halfway down the screen.
    safe_park_x = screen_width - 10
    safe_park_y = screen_height // 2
    pyautogui.moveTo(safe_park_x, safe_park_y)

    print("Done. Layout should be locked and safe.")

if __name__ == "__main__":
    main()