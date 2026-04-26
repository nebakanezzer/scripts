#!/usr/bin/env python3
"""
camera_cycle.py — single-browser Frigate camera cycling script.

Cycles between two cameras by:
  1. Press 'f' to de-maximize (shows Frigate sidebar)
  2. Click the sidebar icon for the next camera
  3. [For Living_room only] Press Alt+Left to go back to the live stream view
  4. Press 'f' to re-maximize
  5. Wait CYCLE_WAIT seconds, then repeat

Run find_coords.py once to get ICON_CAM1 / ICON_CAM2 coordinates.
"""

import os

# Must be set BEFORE importing pyautogui
os.environ.setdefault("DISPLAY", ":0")
os.environ.setdefault("XAUTHORITY", os.path.expanduser("~/.Xauthority"))

import subprocess
import time
import sys
import pyautogui

pyautogui.FAILSAFE = False

# ── Config ───────────────────────────────────────────────────────────────────────

URL_START = "http://192.168.1.12:5000/cameras/Living_room"

# Paste coordinates from find_coords.py here
ICON_CAM1 = (24, 265)   # Living_room      ← replace
ICON_CAM2 = (25, 291)   # Living_room_2    ← replace

LOAD_WAIT    = 25   # seconds to wait for Vivaldi + stream on launch
FRIGATE_WAIT = 2    # seconds after pressing 'f' for Frigate animation
SIDEBAR_WAIT = 1    # seconds after sidebar appears before clicking
BACK_WAIT    = 2    # seconds after pressing back before pressing 'f'
CYCLE_WAIT   = 20   # seconds each camera is shown fullscreen


# ── Helpers ──────────────────────────────────────────────────────────────────────

def press(key):
    pyautogui.press(key)
    time.sleep(0.5)


def hotkey(*keys):
    pyautogui.hotkey(*keys)
    time.sleep(0.5)


def click_center():
    w, h = pyautogui.size()
    pyautogui.click(w // 2, h // 2)
    time.sleep(0.5)


def click_icon(coords):
    pyautogui.moveTo(coords[0], coords[1], duration=0.3)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(0.5)


def scroll_down(ticks=4):
    for _ in range(ticks):
        pyautogui.scroll(-1)
        time.sleep(0.2)


def park_mouse():
    w, h = pyautogui.size()
    pyautogui.moveTo(w - 1, h - 1)


def kill_browsers():
    print("Killing browsers...")
    os.system("killall -9 vivaldi-bin firefox firefox-bin 2>/dev/null")
    time.sleep(3)


# ── Startup ───────────────────────────────────────────────────────────────────────

def launch_and_setup():
    kill_browsers()

    print(f"Launching Vivaldi, waiting {LOAD_WAIT}s...")
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

    print("Pressing f11 for OS fullscreen...")
    press('f11')
    time.sleep(3.5)

    print("Clicking page for JS focus...")
    click_center()

    print("Pressing 'f' for Frigate expand...")
    press('f')
    time.sleep(FRIGATE_WAIT)

    print("Scrolling down to centre view...")
    click_center()
    scroll_down(4)

    park_mouse()
    print("Setup complete. Starting cycle loop.\n")


# ── Cycle ─────────────────────────────────────────────────────────────────────────

def switch_to(icon_coords, cam_name, press_back=False):
    """
    De-maximize → click sidebar icon → optional back → re-maximize → scroll.

    press_back=True: press Alt+Left after clicking the icon to return to the
    live stream view. Needed for Living_room because its sidebar icon navigates
    to a detail/sub-page rather than the live stream directly.
    """
    print(f"[Cycle] Switching to {cam_name}...")

    # De-maximize to reveal sidebar
    press('f')
    time.sleep(FRIGATE_WAIT + SIDEBAR_WAIT)

    # Click the camera icon
    click_icon(icon_coords)
    time.sleep(1.5)

    # Go back to the live stream if the icon lands on a sub-page
    if press_back:
        print(f"[Cycle] Pressing Alt+Left to reach live stream...")
        hotkey('alt', 'left')
        time.sleep(BACK_WAIT)
        # Page already has focus after back navigation — do NOT click_center()
        # here as clicking the video feed triggers Frigate detail/clip navigation
    else:
        click_center()

    # Re-maximize
    press('f')
    time.sleep(FRIGATE_WAIT)

    # Scroll into position
    click_center()
    scroll_down(4)

    park_mouse()
    print(f"[Cycle] Now showing {cam_name}.")


# ── Main ──────────────────────────────────────────────────────────────────────────

def main():
    launch_and_setup()

    # CAM1 (Living_room) is already showing after setup.
    # Cycle order: switch to CAM2, then back to CAM1, repeat.
    cameras = [
        ("Living_room_2", ICON_CAM2, False),   # sidebar nav works fine
        ("Living_room",   ICON_CAM1, True),    # needs Alt+Left after icon click
    ]
    idx = 0

    while True:
        print(f"[Loop] Waiting {CYCLE_WAIT}s...")
        time.sleep(CYCLE_WAIT)

        name, icon, needs_back = cameras[idx]
        switch_to(icon, name, press_back=needs_back)
        idx = (idx + 1) % len(cameras)


if __name__ == "__main__":
    main()