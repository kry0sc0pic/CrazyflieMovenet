"""
Experiment 03: Single Drone Box Pattern (High-Level Commander)
--------------------------------------------------------------
Flies a square in absolute world-frame coordinates using
PositionHlCommander.go_to(), driven by the firmware's high-level
commander. The drone visits the four corners of an axis-aligned
square (well inside the arena bounds) and returns to start.

Run:
    python experiments/03_single_box_pattern/main.py
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
DEFAULT_HEIGHT = 0.5
DRY_RUN = True

# Arena bounds (metres)
X_BOUNDS = (0.3, 1.7)
Y_BOUNDS = (-0.7, 0.7)
Z_BOUNDS = (0.0, 1.0)

# Box corners (absolute world coords, all within bounds). Last point
# returns the drone to the first corner before landing.
BOX_CORNERS = [
    (0.7, -0.3, DEFAULT_HEIGHT),
    (1.3, -0.3, DEFAULT_HEIGHT),
    (1.3,  0.3, DEFAULT_HEIGHT),
    (0.7,  0.3, DEFAULT_HEIGHT),
    (0.7, -0.3, DEFAULT_HEIGHT),
]


def fly_box(cmdr: PositionHlCommander) -> None:
    for i, (x, y, z) in enumerate(BOX_CORNERS):
        print(f"[03] Corner {i + 1}/{len(BOX_CORNERS)} -> ({x}, {y}, {z})")
        cmdr.go_to(x, y, z)
        time.sleep(1.0)


def main() -> None:
    if DRY_RUN:
        print(f"[DRY_RUN] Would fly a box at {DEFAULT_HEIGHT}m on {URI}.")
        for c in BOX_CORNERS:
            print(f"  -> {c}")
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
            time.sleep(1.0)
            fly_box(cmdr)
            print("[03] Landing")


if __name__ == "__main__":
    main()
