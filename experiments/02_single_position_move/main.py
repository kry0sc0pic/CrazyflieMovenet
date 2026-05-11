"""
Experiment 02: Single Drone Position Moves (High-Level Commander)
------------------------------------------------------------------
Demonstrates absolute position flight with PositionHlCommander.

The drone takes off, then moves through a list of (x, y, z) waypoints
in the world frame. The position estimator must be initialised before
flying -- `wait_for_position_estimator` from `utils` blocks until the
Kalman filter has converged.

Run:
    python experiments/02_single_position_move/main.py
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
TAKEOFF_HEIGHT = 0.5
DRY_RUN = True

# Arena bounds (metres) -- all waypoints stay inside this box
X_BOUNDS = (0.3, 1.7)
Y_BOUNDS = (-0.7, 0.7)
Z_BOUNDS = (0.0, 1.0)

WAYPOINTS = [
    # (x, y, z) in metres, world frame -- all within bounds above
    (1.0, -0.5, 0.5),
    (1.5, -0.5, 0.8),
    (1.5,  0.5, 0.8),
    (0.5,  0.5, 0.5),
    (0.5, -0.5, 0.5),
]


def main() -> None:
    if DRY_RUN:
        print(f"[DRY_RUN] Would takeoff {URI} and visit {len(WAYPOINTS)} waypoints.")
        for wp in WAYPOINTS:
            print(f"  -> go_to{wp}")
        return

    cflib.crtp.init_drivers()
    cf = Crazyflie(rw_cache="./cache")

    with SyncCrazyflie(URI, cf=cf) as scf:
        wait_for_position_estimator(scf)

        with PositionHlCommander(
            scf,
            x=0.0, y=0.0, z=0.0,
            default_height=TAKEOFF_HEIGHT,
            controller=PositionHlCommander.CONTROLLER_PID,
        ) as cmdr:
            print("[02] Taking off")

            for i, (x, y, z) in enumerate(WAYPOINTS):
                print(f"[02] Waypoint {i + 1}/{len(WAYPOINTS)} -> ({x}, {y}, {z})")
                cmdr.go_to(x, y, z)
                time.sleep(2)
            print("[02] Landing")


if __name__ == "__main__":
    main()
