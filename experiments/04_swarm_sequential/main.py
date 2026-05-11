"""
Experiment 04: Swarm -- Sequential Operations (High-Level Commander)
--------------------------------------------------------------------
Each drone in the swarm executes the action one after another using
`Swarm.sequential(...)` and the firmware's high-level commander
(via PositionHlCommander). Useful for staged take-offs (e.g. to avoid
prop wash) or any time you specifically do NOT want all drones moving
at the same instant.

Compare with experiment 05 which performs the same actions in
parallel.

Run:
    python experiments/04_swarm_sequential/main.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory, Swarm
from cflib.positioning.position_hl_commander import PositionHlCommander

from utils import wait_for_position_estimator

URIS = [
    "radio://0/10/2M/E7E7E7E7E7",
    "radio://0/20/2M/E7E7E7E7E7",
    "radio://0/30/2M/E7E7E7E7E7",
    "radio://0/40/2M/E7E7E7E7E7",
]
DEFAULT_HEIGHT = 0.5
HOVER_TIME = 2.0
DRY_RUN = True

# Arena bounds (metres)
X_BOUNDS = (0.3, 1.7)
Y_BOUNDS = (-0.7, 0.7)
Z_BOUNDS = (0.0, 1.0)


def take_off(scf) -> None:
    print(f"[04] Taking off    {scf.cf.link_uri}")
    cmdr = PositionHlCommander(
        scf,
        default_height=DEFAULT_HEIGHT,
        controller=PositionHlCommander.CONTROLLER_PID,
    )
    cmdr.take_off(DEFAULT_HEIGHT)
    scf._cmdr = cmdr
    time.sleep(1.0)


def hover(scf) -> None:
    print(f"[04] Hovering      {scf.cf.link_uri}")
    time.sleep(HOVER_TIME)


def land(scf) -> None:
    print(f"[04] Landing       {scf.cf.link_uri}")
    scf._cmdr.land()


def main() -> None:
    if DRY_RUN:
        print(f"[DRY_RUN] Would sequentially takeoff/hover/land {len(URIS)} drones:")
        for uri in URIS:
            print(f"  - {uri}")
        return

    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache="./cache")

    with Swarm(URIS, factory=factory) as swarm:
        print("[04] Waiting for position estimators (parallel)")
        swarm.parallel_safe(wait_for_position_estimator)

        print("[04] === SEQUENTIAL TAKEOFF ===")
        swarm.sequential(take_off)

        print("[04] === SEQUENTIAL HOVER ===")
        swarm.sequential(hover)

        print("[04] === SEQUENTIAL LAND ===")
        swarm.sequential(land)


if __name__ == "__main__":
    main()
