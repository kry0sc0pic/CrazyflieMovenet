"""
Experiment 05: Swarm -- Parallel Operations (High-Level Commander)
-------------------------------------------------------------------
All drones in the swarm execute the action simultaneously using
`Swarm.parallel_safe(...)` and the firmware's high-level commander
(via PositionHlCommander). This is the most common pattern for
choreographed flight: synchronised takeoff, formation moves, etc.

Each drone moves to a unique target position assigned per-URI via
the `args_dict` parameter -- that way `parallel_safe` calls the same
function but with different arguments per drone.

Run:
    python experiments/05_swarm_parallel/main.py
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
DRY_RUN = True

# Arena bounds (metres)
X_BOUNDS = (0.3, 1.7)
Y_BOUNDS = (-0.7, 0.7)
Z_BOUNDS = (0.0, 1.0)

# Target (x, y, z) for each URI -- all drones move at the same time,
# but each one has its own destination. All targets are within bounds.
TARGETS = {
    "radio://0/10/2M/E7E7E7E7E7": (0.5, -0.5, 0.5),
    "radio://0/20/2M/E7E7E7E7E7": (1.5, -0.5, 0.7),
    "radio://0/30/2M/E7E7E7E7E7": (1.5,  0.5, 0.5),
    "radio://0/40/2M/E7E7E7E7E7": (0.5,  0.5, 0.7),
}


def takeoff(scf) -> None:
    cmdr = PositionHlCommander(
        scf,
        default_height=DEFAULT_HEIGHT,
        controller=PositionHlCommander.CONTROLLER_PID,
    )
    cmdr.take_off(DEFAULT_HEIGHT)
    scf._cmdr = cmdr
    print(f"[05] Took off  {scf.cf.link_uri}")


def go_to(scf, x: float, y: float, z: float) -> None:
    print(f"[05] Moving    {scf.cf.link_uri} -> ({x}, {y}, {z})")
    scf._cmdr.go_to(x, y, z)


def land(scf) -> None:
    print(f"[05] Landing   {scf.cf.link_uri}")
    scf._cmdr.land()


def main() -> None:
    if DRY_RUN:
        print(f"[DRY_RUN] Would takeoff {len(URIS)} drones in parallel and move to:")
        for uri, target in TARGETS.items():
            print(f"  {uri} -> {target}")
        return

    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache="./cache")

    with Swarm(URIS, factory=factory) as swarm:
        print("[05] Waiting for position estimators (parallel)")
        swarm.parallel_safe(wait_for_position_estimator)

        print("[05] === PARALLEL TAKEOFF ===")
        swarm.parallel_safe(takeoff)
        time.sleep(2.0)

        print("[05] === PARALLEL MOVE TO PER-DRONE TARGETS ===")
        # `args_dict` is keyed by URI; each value is a tuple of args
        # forwarded to `go_to` for that drone.
        swarm.parallel_safe(go_to, args_dict=TARGETS)
        time.sleep(2.0)

        print("[05] === PARALLEL LAND ===")
        swarm.parallel_safe(land)


if __name__ == "__main__":
    main()
