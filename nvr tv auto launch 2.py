#!/usr/bin/env python3
import subprocess
import time
import pyautogui
import os

# Deep-link URL
URL = "http://192.168.1.12:5000/cameras/living_room"
LOAD_DELAY = 12 # Slightly longer to allow profile loading

def main():
    print("Stopping existing Vivaldi instances...")
    os.system("pkill -f vivaldi")
    time.sleep(2)

    screen_width, screen_height = pyautogui.size()

    # We use a custom profile directory that IS NOT in /tmp.
    # This ensures the browser RETAINS its settings/view between reboots.
    profile_path = os.path.expanduser("~/.config/vivaldi_frigate_kiosk")

    print(f"Launching Vivaldi with permanent profile at {profile_path}...")
    subprocess.Popen([
        "vivaldi", 
        URL,
        "--new-window",
        "--kiosk", 
        f"--window-size={screen_width},{screen_height}",
        "--window-position=0,0",
        f"--user-data-dir={profile_path}"
    ])

    print(f"Waiting {LOAD_DELAY}s for profile and page load...")
    time.sleep(LOAD_DELAY)

    # 1. INITIAL FOCUS (Safe Zone)
    pyautogui.click(screen_width // 2, 20)
    time.sleep(1)

    # 2. FULLSCREEN TRIGGER
    # Since we aren't in incognito, once these are triggered, 
    # the profile will likely remember them for next time.
    pyautogui.press('f11')
    time.sleep(1)
    pyautogui.press('f')
    
    # 3. MINOR SCROLL
    print("Adjusting view...")
    for _ in range(2):
        pyautogui.press('down')
        time.sleep(0.2)

    # 4. PARK MOUSE (Far right, middle height)
    pyautogui.moveTo(screen_width - 10, screen_height // 2)

    print("Done. Settings saved to permanent profile.")

if __name__ == "__main__":
    main()