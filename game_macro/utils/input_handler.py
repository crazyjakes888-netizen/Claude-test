"""Input simulation — supports pyautogui (emulator window) and ADB (real device)."""

import subprocess
import time
import pyautogui

pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort


# ---------------------------------------------------------------------------
# Emulator / desktop input (pyautogui)
# ---------------------------------------------------------------------------

def press_key(key, duration=0.05):
    pyautogui.keyDown(key)
    time.sleep(duration)
    pyautogui.keyUp(key)


def hold_key(key):
    pyautogui.keyDown(key)


def release_key(key):
    pyautogui.keyUp(key)


def click(x, y):
    pyautogui.click(x, y)


def drag(x1, y1, x2, y2, duration=0.2):
    pyautogui.moveTo(x1, y1)
    pyautogui.dragTo(x2, y2, duration=duration, button='left')


# ---------------------------------------------------------------------------
# ADB input (Android device / emulator via ADB)
# ---------------------------------------------------------------------------

def adb_tap(x, y, device=None):
    """Tap a coordinate on an ADB-connected device."""
    cmd = ['adb']
    if device:
        cmd += ['-s', device]
    cmd += ['shell', 'input', 'tap', str(x), str(y)]
    subprocess.run(cmd, capture_output=True)


def adb_swipe(x1, y1, x2, y2, duration_ms=200, device=None):
    """Swipe on an ADB-connected device."""
    cmd = ['adb']
    if device:
        cmd += ['-s', device]
    cmd += ['shell', 'input', 'swipe',
            str(x1), str(y1), str(x2), str(y2), str(duration_ms)]
    subprocess.run(cmd, capture_output=True)


def adb_screenshot(device=None):
    """Capture screen via ADB and return as a numpy BGR array."""
    import numpy as np
    import cv2
    cmd = ['adb']
    if device:
        cmd += ['-s', device]
    cmd += ['exec-out', 'screencap', '-p']
    result = subprocess.run(cmd, capture_output=True)
    arr = np.frombuffer(result.stdout, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img


def list_adb_devices():
    """Return a list of connected ADB device serials."""
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()[1:]
    return [line.split()[0] for line in lines if line.strip() and 'device' in line]
