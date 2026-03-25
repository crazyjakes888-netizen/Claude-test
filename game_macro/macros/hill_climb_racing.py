"""
Hill Climb Racing macro — with auto-restart on death.

Game-over detection
-------------------
1. Colour: the results screen has a dark overlay (mean brightness drops sharply)
   combined with an orange "RETRY" button in the bottom half.
2. Motion fallback: if the screen is static for 3 s we assume the run ended.

Restart
-------
Taps the "RETRY" button, which lives roughly at 50% x, 72% y on most screens.
"""

import time
import numpy as np
from .base_macro import BaseMacro
from utils import region_has_color, get_average_brightness
from utils.input_handler import hold_key, release_key, adb_tap


class HillClimbRacingMacro(BaseMacro):

    LOOP_INTERVAL = 0.033  # ~30 fps

    # ADB screen dimensions (adjust to match your device)
    ADB_SCREEN_W = 1280
    ADB_SCREEN_H = 720

    # Sky colour (BGR) — bright blue/white sky
    SKY_LOWER = [180, 200, 200]
    SKY_UPPER = [255, 255, 255]

    # Orange retry button colour range (BGR)
    RETRY_LOWER = [0, 100, 200]
    RETRY_UPPER = [60, 180, 255]

    # Relative position of the RETRY button on the results screen
    RETRY_RX = 0.50   # horizontal centre
    RETRY_RY = 0.72   # roughly 72% down

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._gas_held = False
        self._brake_held = False

    def setup(self):
        print("[HillClimbRacing] Starting in 3 seconds — switch to game window!")
        time.sleep(3)
        self._start_gas()

    # ------------------------------------------------------------------
    # Game-over detection
    # ------------------------------------------------------------------

    def is_game_over(self, frame):
        """
        Detect the results screen by checking for:
        - Overall dark overlay (average brightness < 80)
        - Orange retry button somewhere in the lower half
        """
        avg = get_average_brightness(frame)
        if avg > 80:
            return False  # screen is bright → still playing

        h, w = frame.shape[:2]
        lower_half = frame[h // 2:, :]
        has_retry = region_has_color(lower_half, self.RETRY_LOWER, self.RETRY_UPPER,
                                     threshold=0.01)
        return has_retry

    # ------------------------------------------------------------------
    # Restart
    # ------------------------------------------------------------------

    def restart_game(self, frame):
        """Tap the RETRY button to begin a new run."""
        print("[HillClimbRacing] Tapping RETRY…")
        self._tap(self.RETRY_RX, self.RETRY_RY)
        time.sleep(0.3)
        # Second tap in case the first hit an ad or intermediate screen
        self._tap(self.RETRY_RX, self.RETRY_RY)

    # ------------------------------------------------------------------
    # Called by base class before restart sequence
    # ------------------------------------------------------------------

    def _release_all(self):
        self._stop_gas()
        self._stop_brake()

    # ------------------------------------------------------------------
    # Main playing logic
    # ------------------------------------------------------------------

    def tick(self, frame):
        slope = self._estimate_slope(frame)
        flipped = self._is_flipped(frame)

        if flipped:
            self._start_gas()
            self._stop_brake()
            return

        if slope < -0.15:
            self._start_gas()
            self._stop_brake()
        elif slope > 0.25:
            self._stop_gas()
            self._start_brake()
            time.sleep(0.05)
            self._stop_brake()
            self._start_gas()
        else:
            self._start_gas()
            self._stop_brake()

    # ------------------------------------------------------------------
    # Terrain slope estimation
    # ------------------------------------------------------------------

    def _estimate_slope(self, frame):
        h, w = frame.shape[:2]
        strip_y = int(h * 0.7)
        strip_h = int(h * 0.1)
        strip = frame[strip_y:strip_y + strip_h, :]
        left_b  = get_average_brightness(strip, region=(0, 0, w // 2, strip_h))
        right_b = get_average_brightness(strip, region=(w // 2, 0, w // 2, strip_h))
        return (left_b - right_b) / 255.0

    def _is_flipped(self, frame):
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
