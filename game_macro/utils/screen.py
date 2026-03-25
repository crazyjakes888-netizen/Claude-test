"""Screen capture and image analysis utilities."""

import numpy as np
import pyautogui
import cv2
from PIL import Image


def capture_screen(region=None):
    """Capture the full screen or a region. region=(x, y, w, h)"""
    screenshot = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def find_color_region(frame, lower_bgr, upper_bgr):
    """Return a mask of pixels within a BGR color range."""
    lower = np.array(lower_bgr, dtype=np.uint8)
    upper = np.array(upper_bgr, dtype=np.uint8)
    return cv2.inRange(frame, lower, upper)


def region_has_color(frame, lower_bgr, upper_bgr, threshold=0.01):
    """Return True if at least `threshold` fraction of the frame matches the color."""
    mask = find_color_region(frame, lower_bgr, upper_bgr)
    ratio = np.count_nonzero(mask) / mask.size
    return ratio >= threshold


def find_template(frame, template_path, threshold=0.8):
    """
    Search for a template image inside frame.
    Returns (x, y, w, h) of best match or None.
    """
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        return None
    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        h, w = template.shape[:2]
        return (*max_loc, w, h)
    return None


def get_average_brightness(frame, region=None):
    """Return average pixel brightness (0-255) of a region."""
    if region:
        x, y, w, h = region
        frame = frame[y:y+h, x:x+w]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray))
