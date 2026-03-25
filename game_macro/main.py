"""
Game Macro Launcher
===================
Automates Hill Climb Racing and Subway Surfers.

── iOS tablet (recommended) ──────────────────────────────────────────────────
1. Mirror your iPad to your Mac or PC:
     macOS   → QuickTime Player → File → New Movie Recording → pick your iPad
     Windows → ApowerMirror, Reflector, or LonelyScreen (free trial)

2. Resize the mirror window so you can see it, note its position on screen.

3. Run (replace X Y W H with the mirror window coordinates):
     python main.py hill   --region 100 50 800 600
     python main.py subway --region 100 50 800 600

4. Switch focus to the mirror window and press F8 to stop at any time.

── Android emulator (BlueStacks / LDPlayer) ─────────────────────────────────
     python main.py hill   --adb
     python main.py subway --adb --device emulator-5554

── Keyboard-controlled emulator ─────────────────────────────────────────────
     python main.py hill   --region 0 0 1280 720
     python main.py subway --region 0 0 1280 720
"""

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Game Macro Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('game', choices=['hill', 'subway'],
                        help="Which game to automate")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--adb', action='store_true',
                      help="Android device/emulator via ADB")
    mode.add_argument('--ios', action='store_true',
                      help="iOS device via pymobiledevice3 (USB)")

    parser.add_argument('--device', default=None,
                        help="ADB device serial (default: first found)")
    parser.add_argument('--region', nargs=4, type=int, metavar=('X', 'Y', 'W', 'H'),
                        help="Desktop screen region to capture (mirror window position)")
    return parser.parse_args()


def main():
    args = parse_args()

    lockdown = None

    if args.adb:
        from utils.input_handler import list_adb_devices
        devices = list_adb_devices()
        if not devices:
            print("ERROR: No ADB devices found. Connect a device or start an emulator.")
            sys.exit(1)
        device = args.device or devices[0]
        print(f"ADB device: {device}")
        use_adb, use_ios = True, False
        adb_device = device
    elif args.ios:
        try:
            from pymobiledevice3.lockdown import LockdownClient
            lockdown = LockdownClient()
            print(f"iOS device: {lockdown.identifier}  ({lockdown.product_type})")
        except ImportError:
            print("ERROR: pymobiledevice3 is required for --ios mode.")
            print("       pip install pymobiledevice3")
            sys.exit(1)
        except Exception as exc:
            print(f"ERROR: Could not connect to iOS device: {exc}")
            print("       Make sure your iPad is connected via USB and you have tapped 'Trust'.")
            sys.exit(1)
        use_adb, use_ios = False, True
        adb_device = None
    else:
        use_adb, use_ios = False, False
        adb_device = None

    region = tuple(args.region) if args.region else None

    common_kwargs = dict(
        use_adb=use_adb,
        use_ios=use_ios,
        adb_device=adb_device,
        screen_region=region,
        lockdown=lockdown,
    )

    from macros import HillClimbRacingMacro, SubwaySurfersMacro

    if args.game == 'hill':
        macro = HillClimbRacingMacro(**common_kwargs)
        print("=== Hill Climb Racing Macro ===")
    else:
        macro = SubwaySurfersMacro(**common_kwargs)
        print("=== Subway Surfers Macro ===")

    print("Press F8 at any time to stop.\n")
    macro.start()


if __name__ == '__main__':
    main()
