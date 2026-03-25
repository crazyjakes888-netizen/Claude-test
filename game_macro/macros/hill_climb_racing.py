"""
Hill Climb Racing macro.

Strategy
--------
The car's angle relative to horizontal determines the optimal action:
- Tilting nose DOWN (going into a valley) → gas
- Tilting nose UP  (going up a steep hill) → brake then gas
- Car flipping backward                    → gas hard

Screen analysis:
  We track a strip along the bottom of the frame for terrain colour
  and estimate the road slope using brightness gradient.

Controls (emulator keyboard mapping — adjust to match your emulator):
  Gas   → Right arrow  (or hold right mouse button if using on-screen)
  Brake → Left arrow
"""

import time
import numpy as np
from .base_macro import BaseMacro
from utils import region_has_color, get_average_brightness
from utils.input_handler import hold_key, release_key, adb_tap, adb_swipe


class HillClimbRacingMacro(BaseMacro):
    """
    Macro for Hill Climb Racing.

    Emulator mode  – uses keyboard arrow keys (right = gas, left = brake).
    ADB mode       – taps right/left half of the screen.
    """

    LOOP_INTERVAL = 0.033  # ~30 fps

    # ADB screen dimensions (adjust to your device resolution)
    ADB_SCREEN_W = 1280
    ADB_SCREEN_H = 720

    # Sky colour range (BGR) — used to detect if car has flipped
    SKY_LOWER = [180, 200, 200]
    SKY_UPPER = [255, 255, 255]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._gas_held = False
        self._brake_held = False
        self._prev_slope = 0.0

    def setup(self):
        print("[HillClimbRacing] Starting in 3 seconds — switch to game window!")
        time.sleep(3)
        self._start_gas()

    # ------------------------------------------------------------------
    # Main logic
    # ------------------------------------------------------------------

    def tick(self, frame):
        h, w = frame.shape[:2]

        slope = self._estimate_slope(frame)
        flipped = self._is_flipped(frame)

        if flipped:
            # Car upside down — keep gas to try to flip back
            self._start_gas()
            self._stop_brake()
            return

        if slope < -0.15:
            # Steep downhill: go fast
            self._start_gas()
            self._stop_brake()
        elif slope > 0.25:
            # Very steep uphill: brake briefly then gas
            self._stop_gas()
            self._start_brake()
            time.sleep(0.05)
            self._stop_brake()
            self._start_gas()
        else:
            # Normal terrain: hold gas
            self._start_gas()
            self._stop_brake()

        self._prev_slope = slope

    # ------------------------------------------------------------------
    # Terrain slope estimation
    # ------------------------------------------------------------------

    def _estimate_slope(self, frame):
        """
        Sample brightness in a horizontal strip near the bottom of the frame.
        Compare left half vs right half brightness to estimate road tilt.
        Positive → road rising right (uphill), Negative → road falling right (downhill).
        """
        h, w = frame.shape[:2]
        strip_y = int(h * 0.7)
        strip_h = int(h * 0.1)
        strip = frame[strip_y:strip_y + strip_h, :]

        left_brightness = get_average_brightness(strip, region=(0, 0, w // 2, strip_h))
        right_brightness = get_average_brightness(strip, region=(w // 2, 0, w // 2, strip_h))

        # Brighter on left = terrain higher on left = going uphill
        return (left_brightness - right_brightness) / 255.0

    def _is_flipped(self, frame):
        """Detect if the car is upside-down by checking if sky dominates the lower half."""
        h, w = frame.shape[:2]
        lower_half = frame[h // 2:, :]
        return region_has_color(lower_half, self.SKY_LOWER, self.SKY_UPPER, threshold=0.3)

    # ------------------------------------------------------------------
    # Input helpers
    # ------------------------------------------------------------------

    def _start_gas(self):
        if self._gas_held:
            return
        self._gas_held = True
        if self.use_adb:
            adb_tap(int(self.ADB_SCREEN_W * 0.75), int(self.ADB_SCREEN_H * 0.75),
                    self.adb_device)
        else:
            hold_key('right')

    def _stop_gas(self):
        if not self._gas_held:
            return
        self._gas_held = False
        if not self.use_adb:
            release_key('right')

    def _start_brake(self):
        if self._brake_held:
            return
        self._brake_held = True
        if self.use_adb:
            adb_tap(int(self.ADB_SCREEN_W * 0.25), int(self.ADB_SCREEN_H * 0.75),
                    self.adb_device)
        else:
            hold_key('left')

    def _stop_brake(self):
        if not self._brake_held:
            return
        self._brake_held = False
        if not self.use_adb:
            release_key('left')
