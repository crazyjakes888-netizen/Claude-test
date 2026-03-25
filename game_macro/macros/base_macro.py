"""Base class shared by all game macros."""

import time
import threading
import numpy as np
import keyboard


class BaseMacro:
    """
    Subclass this and implement:
      - setup()            – called once before the loop starts
      - tick(frame)        – called every frame while playing
      - is_game_over(frame)– return True when the game-over screen is detected
      - restart_game(frame)– tap/click whatever restarts the run

    The base loop handles the play → dead → restart → play cycle automatically.
    """

    LOOP_INTERVAL = 0.05          # seconds between ticks (~20 fps)
    DEAD_STILL_THRESHOLD = 3.0    # seconds of no screen motion before declaring dead
    STILL_DIFF_CUTOFF = 1.5       # mean-abs-diff below this = screen is static

    def __init__(self, use_adb=False, use_ios=False,
                 adb_device=None, screen_region=None, lockdown=None):
        self.use_adb = use_adb
        self.use_ios = use_ios
        self.adb_device = adb_device
        self.screen_region = screen_region
        self._lockdown = lockdown
        self._running = False
        self._thread = None

        self._prev_frame = None
        self._still_since = None   # timestamp when screen last went static
        self._state = 'playing'    # 'playing' | 'dead'
        self._run_count = 0

    # ------------------------------------------------------------------
    # Override in subclasses
    # ------------------------------------------------------------------

    def setup(self):
        pass

    def tick(self, frame):
        raise NotImplementedError

    def is_game_over(self, frame):
        """
        Return True if the game-over / results screen is visible.
        Default: rely purely on the motion-based detection in the base loop.
        Override to add colour-based detection for faster response.
        """
        return False

    def restart_game(self, frame):
        """
        Tap / click to dismiss the game-over screen and start a new run.
        Override in each game subclass.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print(f"[{self.__class__.__name__}] Running — press F8 to stop.")
        keyboard.wait('f8')
        self.stop()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        print(f"[{self.__class__.__name__}] Stopped after {self._run_count} run(s).")

    # ------------------------------------------------------------------
    # Internal loop
    # ------------------------------------------------------------------

    def _capture(self):
        if self.use_adb:
            from utils.input_handler import adb_screenshot
            return adb_screenshot(self.adb_device)
        elif self.use_ios:
            from utils.ios_handler import ios_screenshot
            return ios_screenshot(self._lockdown)
        else:
            from utils.screen import capture_screen
            return capture_screen(self.screen_region)

    def _screen_is_still(self, frame):
        """Return True if the screen hasn't changed since last frame."""
        if self._prev_frame is None or frame.shape != self._prev_frame.shape:
            return False
        diff = np.mean(np.abs(frame.astype(np.int16) - self._prev_frame.astype(np.int16)))
        return diff < self.STILL_DIFF_CUTOFF

    def _run(self):
        self.setup()

        while self._running:
            t_start = time.time()
            frame = self._capture()

            if frame is None:
                time.sleep(self.LOOP_INTERVAL)
                continue

            if self._state == 'playing':
                # ------ motion-based death detection ------
                if self._screen_is_still(frame):
                    if self._still_since is None:
                        self._still_since = time.time()
                    still_for = time.time() - self._still_since
                else:
                    self._still_since = None
                    still_for = 0.0

                colour_dead = self.is_game_over(frame)
                motion_dead = still_for >= self.DEAD_STILL_THRESHOLD

                if colour_dead or motion_dead:
                    reason = 'colour' if colour_dead else f'no motion for {still_for:.1f}s'
                    print(f"[{self.__class__.__name__}] Game over detected ({reason}) — restarting…")
                    self._on_death(frame)
                else:
                    try:
                        self.tick(frame)
                    except Exception as exc:
                        print(f"[{self.__class__.__name__}] tick error: {exc}")

            elif self._state == 'dead':
                # handled inside _on_death; state flips back to 'playing'
                pass

            self._prev_frame = frame

            elapsed = time.time() - t_start
            sleep_time = self.LOOP_INTERVAL - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _on_death(self, frame):
        """Release any held keys, wait for the results screen, then restart."""
        self._state = 'dead'
        self._release_all()
        self._still_since = None
        self._run_count += 1

        # Give the game a moment to fully show the game-over screen
        time.sleep(1.2)

        frame = self._capture()
        if frame is not None:
            try:
                self.restart_game(frame)
            except Exception as exc:
                print(f"[{self.__class__.__name__}] restart error: {exc}")

        # Wait for the new run to load before resuming ticks
        time.sleep(2.5)
        self._prev_frame = None
        self._state = 'playing'
        print(f"[{self.__class__.__name__}] Run #{self._run_count + 1} started.")

    def _release_all(self):
        """Override in subclasses to release any held keys/buttons."""
        pass

    # ------------------------------------------------------------------
    # Shared tap helper (works for mirror, ADB, and iOS modes)
    # ------------------------------------------------------------------

    def _tap(self, rx, ry):
        """
        Tap at a position expressed as fractions of the screen (0.0–1.0).
        rx=0.5, ry=0.5 taps the centre.
        """
        frame = self._capture()
        if frame is None:
            return
        h, w = frame.shape[:2]
        x, y = int(w * rx), int(h * ry)

        if self.use_adb:
            from utils.input_handler import adb_tap
            adb_tap(x, y, self.adb_device)
        elif self.use_ios:
            from utils.ios_handler import ios_tap
            ios_tap(x, y, self._lockdown)
        else:
            from utils.input_handler import click
            # Offset by screen_region origin if set
            if self.screen_region:
                x += self.screen_region[0]
                y += self.screen_region[1]
            click(x, y)
