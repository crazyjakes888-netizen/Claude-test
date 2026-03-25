"""
Subway Surfers macro — with auto-restart on death.

Game-over detection
-------------------
1. Colour: the "Play Again" button is bright blue/green. When it appears the
   background overlay is dark. We check for that button colour in the
   lower-centre of the screen.
2. Motion fallback: no screen motion for 3 s → assume dead.

Restart
-------
Taps "Play Again" at roughly (50%, 68%) then dismisses any follow-up prompts.
"""

import time
import numpy as np
from .base_macro import BaseMacro
from utils import region_has_color, find_color_region
from utils.input_handler import press_key, adb_swipe


class SubwaySurfersMacro(BaseMacro):

    LOOP_INTERVAL = 0.08

    # BGR colour ranges for obstacle detection (trains / barriers are dark)
    OBSTACLE_LOWER = [20, 20, 20]
    OBSTACLE_UPPER = [90, 90, 90]

    # "Play Again" button — typically bright blue (BGR)
    PLAY_AGAIN_LOWER = [180, 100, 0]
    PLAY_AGAIN_UPPER = [255, 200, 80]

    ADB_SCREEN_W = 1080
    ADB_SCREEN_H = 1920

    MOVE_COOLDOWN = 0.35

    # Relative tap position for "Play Again"
    PLAY_AGAIN_RX = 0.50
    PLAY_AGAIN_RY = 0.68

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lane = 1
        self._last_move = 0.0

    def setup(self):
        print("[SubwaySurfers] Starting in 3 seconds — switch to game window!")
        time.sleep(3)

    # ------------------------------------------------------------------
    # Game-over detection
    # ------------------------------------------------------------------

    def is_game_over(self, frame):
        """
        Detect the end screen by checking for the blue 'Play Again' button
        in the lower third of the screen.
        """
        h, w = frame.shape[:2]
        lower = frame[int(h * 0.5):, :]
        return region_has_color(lower, self.PLAY_AGAIN_LOWER, self.PLAY_AGAIN_UPPER,
                                threshold=0.015)

    # ------------------------------------------------------------------
    # Restart
    # ------------------------------------------------------------------

    def restart_game(self, frame):
        """Tap 'Play Again' and reset lane tracking."""
        print("[SubwaySurfers] Tapping Play Again…")
        self._tap(self.PLAY_AGAIN_RX, self.PLAY_AGAIN_RY)
        time.sleep(0.4)
        # Dismiss any score/reward screen with a second tap
        self._tap(self.PLAY_AGAIN_RX, self.PLAY_AGAIN_RY)
        # Reset state
        self._lane = 1
        self._last_move = 0.0

    # ------------------------------------------------------------------
    # Main playing logic
    # ------------------------------------------------------------------

    def tick(self, frame):
        if time.time() - self._last_move < self.MOVE_COOLDOWN:
            return

        h, w = frame.shape[:2]
        zone_top = int(h * 0.35)
        zone_bot = int(h * 0.75)
        zone = frame[zone_top:zone_bot, :]
        zh, zw = zone.shape[:2]

        left_col   = zone[:, :zw // 3]
        center_col = zone[:, zw // 3: 2 * zw // 3]
        right_col  = zone[:, 2 * zw // 3:]

        left_d   = self._obstacle_density(left_col)
        center_d = self._obstacle_density(center_col)
        right_d  = self._obstacle_density(right_col)

        action = self._decide(left_d, center_d, right_d)
        if action:
            self._execute(action)
            self._last_move = time.time()

    # ------------------------------------------------------------------
    # Decision logic
    # ------------------------------------------------------------------

    def _obstacle_density(self, region):
        mask = find_color_region(region, self.OBSTACLE_LOWER, self.OBSTACLE_UPPER)
        return np.count_nonzero(mask) / max(mask.size, 1)

    def _decide(self, left, center, right):
        DANGER = 0.08
        current_danger = [left, center, right][self._lane]

        if current_danger < DANGER:
            return None

        if self._lane == 1:
            if left < right:
                return 'left'
            elif right < left:
                return 'right'
            else:
                return 'jump'
        elif self._lane == 0:
            return 'right' if center < DANGER or right < DANGER else 'jump'
        else:
            return 'left' if center < DANGER or left < DANGER else 'jump'

    # ------------------------------------------------------------------
    # Input execution
    # ------------------------------------------------------------------

    def _execute(self, action):
        cx = self.ADB_SCREEN_W // 2
        cy = self.ADB_SCREEN_H // 2
        dist = 300

        if action == 'left':
            self._lane = max(0, self._lane - 1)
            if self.use_adb:
                adb_swipe(cx, cy, cx - dist, cy, 150, self.adb_device)
            else:
                press_key('left')

        elif action == 'right':
            self._lane = min(2, self._lane + 1)
            if self.use_adb:
                adb_swipe(cx, cy, cx + dist, cy, 150, self.adb_device)
            else:
                press_key('right')

        elif action == 'jump':
            if self.use_adb:
                adb_swipe(cx, cy, cx, cy - dist, 150, self.adb_device)
            else:
                press_key('up')

        elif action == 'roll':
            if self.use_adb:
                adb_swipe(cx, cy, cx, cy + dist, 150, self.adb_device)
            else:
                press_key('down')

        print(f"[SubwaySurfers] → {action}  (lane {self._lane})")
