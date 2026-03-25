"""
Subway Surfers macro.

Strategy
--------
The runner is always in one of three lanes (left / center / right).
We scan the screen for obstacles using colour analysis:
  - Dark pixels concentrated in the lower-centre = obstacle ahead → dodge
  - Bright gap on the left/right = safe lane to move into
  - Obstacle fills both sides → jump

Controls:
  Emulator keyboard:  Left/Right arrow = lane change, Up = jump, Down = roll
  ADB swipe:          swipe left/right/up/down on screen centre
"""

import time
import random
import numpy as np
from .base_macro import BaseMacro
from utils import region_has_color, find_color_region
from utils.input_handler import press_key, adb_swipe


class SubwaySurfersMacro(BaseMacro):

    LOOP_INTERVAL = 0.08  # ~12 fps is enough to react

    # BGR colour ranges for obstacle detection (trains are mostly dark/grey)
    OBSTACLE_LOWER = [20, 20, 20]
    OBSTACLE_UPPER = [90, 90, 90]

    # ADB screen size
    ADB_SCREEN_W = 1080
    ADB_SCREEN_H = 1920

    # Cooldown between moves (seconds) — prevents spamming
    MOVE_COOLDOWN = 0.35

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lane = 1          # 0=left, 1=center, 2=right
        self._last_move = 0.0

    def setup(self):
        print("[SubwaySurfers] Starting in 3 seconds — switch to game window!")
        time.sleep(3)

    # ------------------------------------------------------------------
    # Main logic
    # ------------------------------------------------------------------

    def tick(self, frame):
        if time.time() - self._last_move < self.MOVE_COOLDOWN:
            return

        h, w = frame.shape[:2]

        # Analyse the danger zone: lower-middle 40% of screen, vertically centred
        zone_top = int(h * 0.35)
        zone_bot = int(h * 0.75)
        zone = frame[zone_top:zone_bot, :]
        zh, zw = zone.shape[:2]

        left_col   = zone[:, :zw // 3]
        center_col = zone[:, zw // 3: 2 * zw // 3]
        right_col  = zone[:, 2 * zw // 3:]

        left_danger   = self._obstacle_density(left_col)
        center_danger = self._obstacle_density(center_col)
        right_danger  = self._obstacle_density(right_col)

        action = self._decide(left_danger, center_danger, right_danger)
        if action:
            self._execute(action)
            self._last_move = time.time()

    # ------------------------------------------------------------------
    # Decision logic
    # ------------------------------------------------------------------

    def _obstacle_density(self, region):
        """Return fraction of pixels classified as obstacles (0.0 – 1.0)."""
        mask = find_color_region(region, self.OBSTACLE_LOWER, self.OBSTACLE_UPPER)
        return np.count_nonzero(mask) / max(mask.size, 1)

    def _decide(self, left, center, right):
        DANGER = 0.08  # threshold to consider a lane blocked

        current_danger = [left, center, right][self._lane]

        if current_danger < DANGER:
            return None  # safe, do nothing

        # Current lane is blocked
        if self._lane == 1:  # center
            if left < right and self._lane > 0:
                return 'left'
            elif right < left and self._lane < 2:
                return 'right'
            else:
                return 'jump'
        elif self._lane == 0:  # left lane
            if center < DANGER:
                return 'right'
            elif right < DANGER:
                return 'right'  # move toward safety
            else:
                return 'jump'
        else:  # right lane (2)
            if center < DANGER:
                return 'left'
            elif left < DANGER:
                return 'left'
            else:
                return 'jump'

    # ------------------------------------------------------------------
    # Input execution
    # ------------------------------------------------------------------

    def _execute(self, action):
        cx = self.ADB_SCREEN_W // 2
        cy = self.ADB_SCREEN_H // 2
        swipe_dist = 300

        if action == 'left':
            self._lane = max(0, self._lane - 1)
            if self.use_adb:
                adb_swipe(cx, cy, cx - swipe_dist, cy, 150, self.adb_device)
            else:
                press_key('left')

        elif action == 'right':
            self._lane = min(2, self._lane + 1)
            if self.use_adb:
                adb_swipe(cx, cy, cx + swipe_dist, cy, 150, self.adb_device)
            else:
                press_key('right')

        elif action == 'jump':
            if self.use_adb:
                adb_swipe(cx, cy, cx, cy - swipe_dist, 150, self.adb_device)
            else:
                press_key('up')

        elif action == 'roll':
            if self.use_adb:
                adb_swipe(cx, cy, cx, cy + swipe_dist, 150, self.adb_device)
            else:
                press_key('down')

        print(f"[SubwaySurfers] → {action}  (lane {self._lane})")
