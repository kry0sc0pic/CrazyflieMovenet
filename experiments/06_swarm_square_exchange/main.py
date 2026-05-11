"""
Experiment 06: Swarm -- Square with Position Exchange (High-Level Commander)
----------------------------------------------------------------------------
Four drones start at the four corners (A, B, C, D) of an axis-aligned
square inside the arena. They take off in parallel, then perform a
sequence of clockwise cyclic shifts -- each drone moves to the NEXT
clockwise corner. Because drones travel along the four different edges
of the square at the same time, their paths never cross.

After NUM_SHIFTS = 4 the rotation completes a full revolution and every
drone is back at its original corner before landing.

Drone-to-corner assignment:
    URIS[i] -> CORNERS[(i + shift) % 4]

The drones are physically placed on the floor at the corners listed in
INITIAL_CORNER before the script starts.

Run:
    python experiments/06_swarm_square_exchange/main.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory, Swarm
from cflib.positioning.position_hl_commander import PositionHlCommander

from utils import wait_for_position_estimator

URI_10 = "radio://0/10/2M/E7E7E7E7E7"
URI_20 = "radio://0/20/2M/E7E7E7E7E7"
URI_30 = "radio://0/30/2M/E7E7E7E7E7"
URI_40 = "radio://0/40/2M/E7E7E7E7E7"

URIS = [URI_10, URI_20, URI_30, URI_40]

DEFAULT_HEIGHT = 0.5
SHIFT_PAUSE = 2.0       # seconds to hover between shifts
NUM_SHIFTS = 4          # 4 -> full revolution, back to original corners
DRY_RUN = False

# Arena bounds (metres)
X_BOUNDS = (0.3, 1.7)
Y_BOUNDS = (-0.7, 0.7)
Z_BOUNDS = (0.0, 1.0)

# Square corners, listed clockwise A -> B -> C -> D -> A.
# All comfortably within the arena bounds (0.2 m margin on each side).
A = (0.5, -0.5, DEFAULT_HEIGHT)
B = (1.5, -0.5, DEFAULT_HEIGHT)
C = (1.5,  0.5, DEFAULT_HEIGHT)
D = (0.5,  0.5, DEFAULT_HEIGHT)
CORNERS = [A, B, C, D]

# Physical starting corner for each drone -- place them here before
# running. Order matches CORNERS so the cyclic-shift logic is trivial.
INITIAL_CORNER = {
    URI_10: A,
    URI_20: B,
    URI_30: C,
    URI_40: D,
}


def setup_and_takeoff(scf, x: float, y: float, z: float) -> None:
    """Build a PositionHlCommander seeded with the drone's true start
    position, then take off to the target hover height z."""
    print(f"[06] Took off  {scf.cf.link_uri} from ({x:.2f}, {y:.2f})")
    cmdr = PositionHlCommander(
        scf,
        x=x, y=y, z=0.0,
        default_height=z,
        controller=PositionHlCommander.CONTROLLER_PID,
    )
    cmdr.take_off(z)
    scf._cmdr = cmdr


def go_to(scf, x: float, y: float, z: float) -> None:
    print(f"[06] {scf.cf.link_uri} -> ({x:.2f}, {y:.2f}, {z:.2f})")
    scf._cmdr.go_to(x, y, z)


def land(scf) -> None:
    print(f"[06] Landing   {scf.cf.link_uri}")
    scf._cmdr.land()


def shifted_assignment(shift: int) -> dict:
    """Drone -> corner mapping after `shift` clockwise rotations.

    URIS[i] is sent to CORNERS[(i + shift) % 4], so each drone moves
    one edge clockwise per shift. All four edges are used at once,
    which keeps trajectories disjoint.
    """
    return {uri: CORNERS[(i + shift) % len(CORNERS)] for i, uri in enumerate(URIS)}


def main() -> None:
    if DRY_RUN:
        print(f"[DRY_RUN] Square position-exchange with {len(URIS)} drones.")
        print(f"[DRY_RUN] Initial corners:")
        for uri, corner in INITIAL_CORNER.items():
            print(f"  {uri} @ {corner}")
        for s in range(1, NUM_SHIFTS + 1):
            print(f"[DRY_RUN] After clockwise shift {s}:")
            for uri, corner in shifted_assignment(s).items():
                print(f"  {uri} -> {corner}")
        return

    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache="./cache")

    with Swarm(URIS, factory=factory) as swarm:
        print("[06] Waiting for position estimators (parallel)")
        swarm.parallel_safe(wait_for_position_estimator)

        print("[06] === PARALLEL TAKEOFF (each drone at its own corner) ===")
        swarm.parallel_safe(
            setup_and_takeoff,
            args_dict={uri: INITIAL_CORNER[uri] for uri in URIS},
        )
        time.sleep(2.0)

        for s in range(1, NUM_SHIFTS + 1):
            print(f"[06] === CLOCKWISE SHIFT {s}/{NUM_SHIFTS} ===")
            swarm.parallel_safe(go_to, args_dict=shifted_assignment(s))
            time.sleep(SHIFT_PAUSE)

        print("[06] === PARALLEL LAND ===")
        swarm.parallel_safe(land)


if __name__ == "__main__":
    main()
