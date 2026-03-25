"""Base class shared by all game macros."""

import time
import threading
import keyboard


class BaseMacro:
    """
    Subclass this and implement:
      - setup()      – called once before the loop starts
      - tick(frame)  – called every loop iteration with the current screen frame

    Capture modes
    -------------
    default (emulator/mirror)  – pyautogui screenshot, optionally cropped to screen_region
    --adb                      – ADB screencap + ADB input (Android emulator / device)
    --ios                      – pymobiledevice3 screenshot + mirror-based input (iOS)
    """

    LOOP_INTERVAL = 0.05  # seconds between ticks (~20 fps)

    def __init__(self, use_adb=False, use_ios=False,
                 adb_device=None, screen_region=None, lockdown=None):
        self.use_adb = use_adb
        self.use_ios = use_ios
        self.adb_device = adb_device
        self.screen_region = screen_region
        self._lockdown = lockdown   # pre-created LockdownClient for iOS
        self._running = False
        self._thread = None

    # ------------------------------------------------------------------
    # Override in subclasses
    # ------------------------------------------------------------------

    def setup(self):
        pass

    def tick(self, frame):
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
        print(f"[{self.__class__.__name__}] Stopped.")

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

    def _run(self):
        self.setup()
        while self._running:
            start = time.time()
            frame = self._capture()
            if frame is not None:
                try:
                    self.tick(frame)
                except Exception as exc:
                    print(f"[{self.__class__.__name__}] tick error: {exc}")
            elapsed = time.time() - start
            sleep_time = self.LOOP_INTERVAL - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
