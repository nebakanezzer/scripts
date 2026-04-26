#!/usr/bin/env python3
"""
camera_cycle.py — single-browser Frigate camera cycling script.

Approach: one Vivaldi window, cycling between cameras by:
  1. Press 'f' to de-maximize (shows Frigate sidebar)
  2. Click the sidebar icon for the next camera
  3. Press 'f' to re-maximize
  4. Wait CYCLE_WAIT seconds, then repeat

No window switching, no focus juggling, no second browser.

SETUP:
  Run find_coords.py once to get ICON_CAM1 and ICON_CAM2 coordinates,
  then paste them below.
"""

import subprocess
import time
import os
import pyautogui

os.environ.setdefault("DISPLAY", ":0")
os.environ.setdefault("XAUTHORITY", os.path.expanduser("~/.Xauthority"))

pyautogui.FAILSAFE = False

# ── Config ───────────────────────────────────────────────────────────────────────

# Starting URL — first camera, shown on launch
URL_START = "http://192.168.1.12:5000/cameras/Living_room"

# Pixel coordinates of each camera's icon in the Frigate left sidebar.
# Run find_coords.py to get these values.
ICON_CAM1 = (24, 265)   # Living_room      ← replace with find_coords.py output
ICON_CAM2 = (25, 291)   # Living_room_2    ← replace with find_coords.py output

LOAD_WAIT    = 25   # seconds to wait for Vivaldi + stream to load on launch
FRIGATE_WAIT = 2    # seconds to wait after pressing 'f' for Frigate animation
SIDEBAR_WAIT = 1    # seconds to wait after sidebar appears before clicking
CYCLE_WAIT   = 20   # seconds each camera is shown in fullscreen


# ── Helpers ──────────────────────────────────────────────────────────────────────

def press(key):
    pyautogui.press(key)
    time.sleep(0.5)


def click_center():
    """Click centre of screen to ensure the page has JS keyboard focus."""
    w, h = pyautogui.size()
    pyautogui.click(w // 2, h // 2)
    time.sleep(0.5)


def click_icon(coords):
    """Click a sidebar icon at the given (x, y) screen coordinates."""
    pyautogui.moveTo(coords[0], coords[1], duration=0.3)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(0.5)


def park_mouse():
    """Park cursor in corner so it doesn't hover over sidebar icons."""
    w, h = pyautogui.size()
    pyautogui.moveTo(w - 1, h - 1)


def kill_browsers():
    print("Killing browsers...")
    os.system("killall -9 vivaldi-bin firefox firefox-bin 2>/dev/null")
    time.sleep(3)


# ── Startup ───────────────────────────────────────────────────────────────────────

def launch_and_setup():
    kill_browsers()

    print(f"Launching Vivaldi, waiting {LOAD_WAIT}s for stream to load...")
    subprocess.Popen([
        "vivaldi",
        "--new-window",
        "--no-first-run",
        "--password-store=basic",
        "--disable-default-browser-check",
        "--user-data-dir=/home/warmachine/.config/vivaldi-kiosk",
        URL_START,
    ])
    time.sleep(LOAD_WAIT)

    # Get OS-level fullscreen first
    print("Pressing f11 for OS fullscreen...")
    press('f11')
    time.sleep(3.5)

    # Give JS focus to the page
    print("Clicking page for JS focus...")
    click_center()

    # Maximize the Frigate stream view
    print("Pressing 'f' for Frigate expand...")
    press('f')
    time.sleep(FRIGATE_WAIT)

    # Scroll down to centre the Vivaldi camera view
    print("Scrolling down to centre view...")
    click_center()
    for _ in range(4):
        pyautogui.scroll(-1)
        time.sleep(0.2)

    park_mouse()
    print("Setup complete. Starting cycle loop.\n")


# ── Cycle ─────────────────────────────────────────────────────────────────────────

def switch_to(icon_coords, cam_name):
    """
    De-maximize → click sidebar icon → re-maximize → scroll into place.
    """
    print(f"[Cycle] Switching to {cam_name}...")

    # De-maximize to reveal the sidebar
    press('f')
    time.sleep(FRIGATE_WAIT + SIDEBAR_WAIT)

    # Click the camera icon in the sidebar
    click_icon(icon_coords)
    time.sleep(1.5)   # wait for Frigate to load the new camera stream

    # Re-maximize
    click_center()    # ensure page focus before pressing 'f'
    press('f')
    time.sleep(FRIGATE_WAIT)

    # Scroll back into position
    click_center()
    for _ in range(4):
        pyautogui.scroll(-1)
        time.sleep(0.2)

    park_mouse()
    print(f"[Cycle] Now showing {cam_name}.")


def main():
    launch_and_setup()

    # Alternate: CAM1 is already showing after setup
    cameras = [
        ("Living_room_2", ICON_CAM2),
        ("Living_room",   ICON_CAM1),
    ]
    idx = 0

    while True:
        print(f"[Loop] Showing current camera — waiting {CYCLE_WAIT}s...")
        time.sleep(CYCLE_WAIT)

        name, icon = cameras[idx]
        switch_to(icon, name)
        idx = (idx + 1) % len(cameras)


if __name__ == "__main__":
    main()
