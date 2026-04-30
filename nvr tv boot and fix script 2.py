#!/usr/bin/env python3
"""
camera_cycle.py — single-browser Frigate camera cycling script.

Crash recovery is handled by systemd Restart=always.
Watchdog only handles network outages.
Logs to ~/frigate_kiosk.log so crashes are captured regardless of
journald configuration.
"""

import os

os.environ.setdefault("DISPLAY", ":0")
os.environ.setdefault("XAUTHORITY", os.path.expanduser("~/.Xauthority"))

import subprocess
import time
import urllib.request
import urllib.error
import logging
import pyautogui

pyautogui.FAILSAFE = False

# ── Logging ───────────────────────────────────────────────────────────────────────

logging.basicConfig(
    filename="/home/warmachine/frigate_kiosk.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def log(msg):
    print(msg)
    logging.info(msg)


# ── Config ───────────────────────────────────────────────────────────────────────

URL_START   = "http://192.168.1.12:5000/cameras/Living_room"
URL_NETWORK = "http://192.168.1.12:5000"

VIVALDI_KIOSK_DIR = "/home/warmachine/.config/vivaldi-kiosk"

ICON_CAM1 = (24, 265)   # Living_room
ICON_CAM2 = (25, 291)   # Living_room_2

# Safe zone: top of left sidebar, above first camera icon (y=265).
SAFE_X = 24
SAFE_Y = 100

LOAD_WAIT      = 20
FRIGATE_WAIT   = 1
SIDEBAR_WAIT   = 1
BACK_WAIT      = 1
SCROLL_WAIT    = 4
CYCLE_WAIT     = 20
CHECK_INTERVAL = 15


# ── Helpers ──────────────────────────────────────────────────────────────────────

def safe_mouse():
    pyautogui.moveTo(SAFE_X, SAFE_Y, duration=0.2)
    time.sleep(0.3)


def press_f():
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
    log("Killing browsers...")
    os.system("killall -9 vivaldi-bin firefox firefox-bin 2>/dev/null")
    time.sleep(3)


def wipe_vivaldi_session():
    session_files = [
        "Current Session", "Current Tabs",
        "Last Session",    "Last Tabs",
    ]
    profile_dir = os.path.join(VIVALDI_KIOSK_DIR, "Default")
    for fname in session_files:
        fpath = os.path.join(profile_dir, fname)
        if os.path.exists(fpath):
            os.remove(fpath)
            log(f"  Wiped: {fpath}")


# ── Network watchdog ──────────────────────────────────────────────────────────────

def is_network_up():
    try:
        urllib.request.urlopen(URL_NETWORK, timeout=5)
        return True
    except (urllib.error.URLError, TimeoutError):
        return False


def watchdog_wait(seconds):
    deadline = time.time() + seconds
    while time.time() < deadline:
        chunk = min(CHECK_INTERVAL, deadline - time.time())
        time.sleep(chunk)
        if not is_network_up():
            log("[Watchdog] Frigate unreachable — waiting for recovery...")
            while not is_network_up():
                time.sleep(5)
            log("[Watchdog] Frigate back online.")


# ── Startup ───────────────────────────────────────────────────────────────────────

def launch_and_setup():
    kill_browsers()
    wipe_vivaldi_session()

    log(f"Launching Vivaldi, waiting {LOAD_WAIT}s...")
    subprocess.Popen([
        "vivaldi",
        "--new-window",
        "--no-first-run",
        "--password-store=basic",
        "--disable-default-browser-check",
        f"--user-data-dir={VIVALDI_KIOSK_DIR}",
        # Prevent renderer memory spiraling on long-running video streams
        "--renderer-process-limit=1",           # single renderer process
        "--js-flags=--max-old-space-size=256",  # cap JS heap at 256MB
        "--disable-dev-shm-usage",              # avoid /dev/shm exhaustion
        # Force software video decode — hardware decode of multiple streams
        # causes renderer bloat and crashes on Intel integrated graphics
        "--disable-accelerated-video-decode",
        "--disable-accelerated-video-encode",
        URL_START,
    ])
    time.sleep(LOAD_WAIT)

    log("Pressing f11 for OS fullscreen...")
    safe_mouse()
    press('f11')
    time.sleep(3.5)

    log("Pressing 'f' for Frigate expand...")
    press_f()
    time.sleep(FRIGATE_WAIT)

    log("Scrolling to centre Living_room view...")
    time.sleep(SCROLL_WAIT)
    move_to_center()
    scroll_down(4)

    safe_mouse()
    log("Setup complete.\n")


# ── Cycle ─────────────────────────────────────────────────────────────────────────

def switch_to(icon_coords, cam_name, press_back=False, scroll=False):
    log(f"[Cycle] Switching to {cam_name}...")

    press_f()
    time.sleep(FRIGATE_WAIT + SIDEBAR_WAIT)

    click_icon(icon_coords)
    time.sleep(1.5)

    if press_back:
        log("[Cycle] Pressing Alt+Left to reach live stream...")
        hotkey('alt', 'left')
        time.sleep(BACK_WAIT)

    press_f()
    time.sleep(FRIGATE_WAIT)

    if scroll:
        time.sleep(SCROLL_WAIT)
        move_to_center()
        scroll_down(4)

    safe_mouse()
    log(f"[Cycle] Now showing {cam_name}.")


# ── Main ──────────────────────────────────────────────────────────────────────────

def main():
    log("=== frigate_kiosk starting ===")
    launch_and_setup()

    cameras = [
        ("Living_room_2", ICON_CAM2, False, False),
        ("Living_room",   ICON_CAM1, True,  True),
    ]
    idx = 0

    while True:
        log(f"[Loop] Waiting {CYCLE_WAIT}s...")
        watchdog_wait(CYCLE_WAIT)

        name, icon, needs_back, do_scroll = cameras[idx]
        switch_to(icon, name, press_back=needs_back, scroll=do_scroll)
        idx = (idx + 1) % len(cameras)


if __name__ == "__main__":
    main()