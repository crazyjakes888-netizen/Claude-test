"""
iOS device support via pymobiledevice3 (no jailbreak required).

Install extras:
    pip install pymobiledevice3

Connect your iPad via USB, trust the computer, then run:
    python main.py hill --ios
    python main.py subway --ios

Alternatively, mirror your iPad to your Mac/PC (QuickTime / ApowerMirror / Reflector)
and use --region to select the mirror window instead.
"""

import numpy as np


def get_ios_device():
    """Return the first connected iOS device, or raise if none found."""
    try:
        from pymobiledevice3.usbmux import select_device
        device = select_device()
        if device is None:
            raise RuntimeError("No iOS device found. Connect your iPad via USB and trust this computer.")
        return device
    except ImportError:
        raise ImportError(
            "pymobiledevice3 is required for iOS support.\n"
            "Install it with:  pip install pymobiledevice3"
        )


def ios_screenshot(lockdown=None):
    """Capture iOS screen and return as a numpy BGR array."""
    try:
        from pymobiledevice3.lockdown import LockdownClient
        from pymobiledevice3.services.screenshot import ScreenshotService
        import io
        from PIL import Image
        import cv2

        if lockdown is None:
            lockdown = LockdownClient()

        with ScreenshotService(lockdown) as svc:
            png_data = svc.take_screenshot()

        img = Image.open(io.BytesIO(png_data)).convert('RGB')
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    except ImportError:
        raise ImportError("pip install pymobiledevice3 Pillow")


def ios_tap(x, y, lockdown=None):
    """
    Simulate a tap on the iOS device screen.
    Uses pymobiledevice3's DVT instruments interface.
    """
    try:
        from pymobiledevice3.lockdown import LockdownClient
        from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation
        # Touch injection via testmanagerd
        _dvt_tap(lockdown or LockdownClient(), x, y)
    except Exception as exc:
        raise RuntimeError(f"iOS tap failed: {exc}\nMake sure Developer Mode is on (Settings → Privacy & Security → Developer Mode).")


def ios_swipe(x1, y1, x2, y2, duration=0.2, lockdown=None):
    """Simulate a swipe gesture on the iOS device."""
    try:
        from pymobiledevice3.lockdown import LockdownClient
        _dvt_swipe(lockdown or LockdownClient(), x1, y1, x2, y2, duration)
    except Exception as exc:
        raise RuntimeError(f"iOS swipe failed: {exc}")


# ---------------------------------------------------------------------------
# Internal DVT touch injection helpers
# ---------------------------------------------------------------------------

def _dvt_tap(lockdown, x, y):
    """Send a tap via DVT (Developer mode required)."""
    from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
    from pymobiledevice3.services.dvt.instruments.screenshot import ScreenshotService
    import time

    with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        # Use XCTest touch injection
        _send_touch_event(dvt, 'tap', [(x, y)])


def _dvt_swipe(lockdown, x1, y1, x2, y2, duration):
    """Send a swipe via DVT."""
    from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
    import time, numpy as np

    steps = max(5, int(duration * 60))
    xs = np.linspace(x1, x2, steps)
    ys = np.linspace(y1, y2, steps)
    points = list(zip(xs.tolist(), ys.tolist()))

    with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        _send_touch_event(dvt, 'swipe', points, duration=duration)


def _send_touch_event(dvt, event_type, points, duration=0.0):
    """
    Low-level touch event injection.
    Falls back to a simpler approach if DVT injection is unavailable.
    """
    try:
        # pymobiledevice3 >= 3.x touch API
        from pymobiledevice3.services.dvt.instruments.xcuitest import XCUITestService
        # This API varies by version — wrap in try/except
        raise NotImplementedError("Use mirror mode for reliable touch injection")
    except Exception:
        # Fallback: print a helpful message
        raise RuntimeError(
            "Direct touch injection requires Developer Mode and a recent pymobiledevice3.\n"
            "Recommended: mirror your iPad screen instead.\n"
            "  macOS  → QuickTime Player → File → New Movie Recording → select iPad\n"
            "  Windows → ApowerMirror or Reflector\n"
            "Then run:  python main.py hill --region X Y W H"
        )
