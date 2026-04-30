#!/usr/bin/env python3
"""
camera_cycle.py — single-browser Frigate camera cycling script.

Crash recovery is handled by systemd Restart=always — no pixel-based crash
detection needed. The watchdog only handles network outages, pausing the
cycle until Frigate is reachable again rather than cycling broken streams.
"""

import os

os.environ.setdefault("DISPLAY", ":0")
os.environ.setdefault("XAUTHORITY", os.path.expanduser("~/.Xauthority"))

import subprocess
import time
import urllib.request
import urllib.error
import pyautogui

pyautogui.FAILSAFE = False

# ── Config ───────────────────────────────────────────────────────────────────────

URL_START   = "http://192.168.1.12:5000/cameras/Living_room"
URL_NETWORK = "http://192.168.1.12:5000"

VIVALDI_KIOSK_DIR = "/home/warmachine/.config/vivaldi-kiosk"

ICON_CAM1 = (24, 265)   # Living_room
ICON_CAM2 = (25, 291)   # Living_room_2

# Safe zone: top of left sidebar, above first camera icon (y=265).
# Cursor must be here before every 'f' press — Frigate maximizes whichever
# camera tile the cursor is over, so it must never be over a tile.
SAFE_X = 24
SAFE_Y = 100

LOAD_WAIT      = 20   # seconds after launching Vivaldi
FRIGATE_WAIT   = 1    # seconds after pressing 'f'
SIDEBAR_WAIT   = 1    # seconds after sidebar appears before clicking
BACK_WAIT      = 1    # seconds after Alt+Left
SCROLL_WAIT    = 4    # extra settle time before scroll on Living_room
CYCLE_WAIT     = 20   # seconds each camera is shown
CHECK_INTERVAL = 15   # network watchdog poll interval


# ── Helpers ──────────────────────────────────────────────────────────────────────

def safe_mouse():
    pyautogui.moveTo(SAFE_X, SAFE_Y, duration=0.2)
    time.sleep(0.3)


def press_f():
    """Always move to safe zone before pressing 'f'."""
    safe_mouse()
    pyautogui.press('f')
    time.sleep(0.5)


def press(key):
    pyautogui.press(key)
    time.sleep(0.5)


def hotkey(*keys):
    pyautogui.hotkey(*keys)
    time.sleep(0.5)


def move_to_center():
    w, h = pyautogui.size()
    pyautogui.moveTo(w // 2, h // 2, duration=0.2)
    time.sleep(0.3)


def scroll_down(ticks=4):
    for _ in range(ticks):
        pyautogui.scroll(-1)
        time.sleep(0.2)


def click_icon(coords):
    pyautogui.moveTo(coords[0], coords[1], duration=0.3)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(0.5)


def kill_browsers():
    print("Killing browsers...")
    os.system("killall -9 vivaldi-bin firefox firefox-bin 2>/dev/null")
    time.sleep(3)


def wipe_vivaldi_session():
    """
    Delete Vivaldi's saved session files so it always starts fresh at
    URL_START rather than restoring the last visited page.
    """
    session_files = [
        "Current Session", "Current Tabs",
        "Last Session",    "Last Tabs",
    ]
    profile_dir = os.path.join(VIVALDI_KIOSK_DIR, "Default")
    for fname in session_files:
        fpath = os.path.join(profile_dir, fname)
        if os.path.exists(fpath):
            os.remove(fpath)
            print(f"  Wiped: {fpath}")


# ── Network watchdog ──────────────────────────────────────────────────────────────

def is_network_up():
    try:
        urllib.request.urlopen(URL_NETWORK, timeout=5)
        return True
    except (urllib.error.URLError, TimeoutError):
        return False


def watchdog_wait(seconds):
    """
    Wait for `seconds` total, checking network every CHECK_INTERVAL.
    If Frigate goes offline, block here until it comes back — no point
    cycling between two broken streams.
    Does not check for crashes — systemd Restart=always handles those.
    """
    deadline = time.time() + seconds
    while time.time() < deadline:
        chunk = min(CHECK_INTERVAL, deadline - time.time())
        time.sleep(chunk)

        if not is_network_up():
            print("[Watchdog] Frigate unreachable — waiting for recovery...")
            while not is_network_up():
                time.sleep(5)
            print("[Watchdog] Frigate back online.")

    return False


# ── Startup ───────────────────────────────────────────────────────────────────────

def launch_and_setup():
    kill_browsers()
    wipe_vivaldi_session()

    print(f"Launching Vivaldi, waiting {LOAD_WAIT}s...")
    subprocess.Popen([
        "vivaldi",
        "--new-window",
        "--no-first-run",
        "--password-store=basic",
        "--disable-default-browser-check",
        f"--user-data-dir={VIVALDI_KIOSK_DIR}",
        URL_START,
    ])
    time.sleep(LOAD_WAIT)

    print("Pressing f11 for OS fullscreen...")
    safe_mouse()
    press('f11')
    time.sleep(3.5)

    print("Pressing 'f' for Frigate expand...")
    press_f()
    time.sleep(FRIGATE_WAIT)

    print("Scrolling to centre Living_room view...")
    time.sleep(SCROLL_WAIT)
    move_to_center()
    scroll_down(4)

    safe_mouse()
    print("Setup complete.\n")


# ── Cycle ─────────────────────────────────────────────────────────────────────────

def switch_to(icon_coords, cam_name, press_back=False, scroll=False):
    print(f"[Cycle] Switching to {cam_name}...")

    # De-maximize to reveal sidebar
    press_f()
    time.sleep(FRIGATE_WAIT + SIDEBAR_WAIT)

    # Click sidebar icon
    click_icon(icon_coords)
    time.sleep(1.5)

    if press_back:
        print("[Cycle] Pressing Alt+Left to reach live stream...")
        hotkey('alt', 'left')
        time.sleep(BACK_WAIT)

    # Re-maximize
    press_f()
    time.sleep(FRIGATE_WAIT)

    if scroll:
        time.sleep(SCROLL_WAIT)
        move_to_center()
        scroll_down(4)

    safe_mouse()
    print(f"[Cycle] Now showing {cam_name}.")


# ── Main ──────────────────────────────────────────────────────────────────────────

def main():
    launch_and_setup()

    cameras = [
        ("Living_room_2", ICON_CAM2, False, False),
        ("Living_room",   ICON_CAM1, True,  True),
    ]
    idx = 0

    while True:
        print(f"[Loop] Waiting {CYCLE_WAIT}s...")
        watchdog_wait(CYCLE_WAIT)

        name, icon, needs_back, do_scroll = cameras[idx]
        switch_to(icon, name, press_back=needs_back, scroll=do_scroll)
        idx = (idx + 1) % len(cameras)


if __name__ == "__main__":
    main()