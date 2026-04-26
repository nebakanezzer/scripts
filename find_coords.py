#!/usr/bin/env python3
"""
find_coords.py — run this once to find the pixel coordinates of the two
Frigate sidebar camera icons.

Run as the normal user, not sudo:
  DISPLAY=:0 python3 find_coords.py

HOW TO USE:
  1. Manually open Vivaldi and navigate to your Frigate camera page.
  2. Press 'f' to DE-maximize so the left sidebar is visible.
  3. Run this script in a terminal.
  4. Hover your mouse over the Living_room sidebar icon and press Enter.
  5. Hover your mouse over the Living_room_2 sidebar icon and press Enter.
  6. Copy the printed coordinates into camera_cycle.py.
"""

import os

# Must be set BEFORE importing pyautogui — it reads DISPLAY at import time
os.environ.setdefault("DISPLAY", ":0")
os.environ.setdefault("XAUTHORITY", os.path.expanduser("~/.Xauthority"))

import pyautogui
pyautogui.FAILSAFE = False


def main():
    print("Make sure Frigate's sidebar is visible (press 'f' in the browser to de-maximize first).\n")

    input("Hover over the Living_room sidebar icon, then press Enter...")
    x1, y1 = pyautogui.position()
    print(f"  Living_room icon: x={x1}, y={y1}\n")

    input("Hover over the Living_room_2 sidebar icon, then press Enter...")
    x2, y2 = pyautogui.position()
    print(f"  Living_room_2 icon: x={x2}, y={y2}\n")

    print("=" * 50)
    print("Paste these values into camera_cycle.py:")
    print(f"  ICON_CAM1 = ({x1}, {y1})   # Living_room")
    print(f"  ICON_CAM2 = ({x2}, {y2})   # Living_room_2")
    print("=" * 50)


if __name__ == "__main__":
    main()