"""
Experiment 01: Single Drone Takeoff and Land (High-Level Commander)
-------------------------------------------------------------------
The simplest possible flight. Connects to ONE Crazyflie, takes off
with the high-level commander, hovers in place for a few seconds,
then lands.

Uses PositionHlCommander, which wraps the firmware's high-level
commander (takeoff/land/go_to). The `with` block automatically
takes off on enter and lands on exit.

Run:
    python experiments/01_single_takeoff_land/main.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander

from utils import wait_for_position_estimator

URI = "radio://0/10/2M/E7E7E7E7E7"
DEFAULT_HEIGHT = 0.5  # meters
HOVER_TIME = 3.0      # seconds
DRY_RUN = True        # set False to actually fly

# Arena bounds (metres) -- all flight stays inside this box
X_BOUNDS = (0.3, 1.7)
Y_BOUNDS = (-0.7, 0.7)
Z_BOUNDS = (0.0, 1.0)


def main() -> None:
    if DRY_RUN:
        print(f"[DRY_RUN] Would takeoff {URI} to {DEFAULT_HEIGHT}m, "
              f"hover {HOVER_TIME}s, and land.")
        return

    cflib.crtp.init_drivers()
    cf = Crazyflie(rw_cache="./cache")

    with SyncCrazyflie(URI, cf=cf) as scf:
        wait_for_position_estimator(scf)

        with PositionHlCommander(
            scf,
            x=0.0, y=0.0, z=0.0,
            default_height=DEFAULT_HEIGHT,
            controller=PositionHlCommander.CONTROLLER_PID,
        ) as cmdr:
            print(f"[01] Took off to {DEFAULT_HEIGHT}m, hovering...")
            time.sleep(HOVER_TIME)
            print("[01] Landing.")


if __name__ == "__main__":
    main()
