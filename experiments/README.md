# Crazyflie Experiments

A set of progressively-complex samples for controlling Crazyflie drones with
[`cflib`](https://github.com/bitcraze/crazyflie-lib-python). They build on the
patterns and the `utils.manager.SwarmManager` helper from the parent project.

Each experiment lives in its own folder and ships with a single `main.py`.
**Every script defaults to `DRY_RUN = True`**, which prints what it *would*
do without opening radio links — flip the flag at the top of the file once
your URIs and arena are configured.

## Layout

| #   | Folder                       | Drones | Pattern    | Commander used         | What it shows                                          |
| --- | ---------------------------- | ------ | ---------- | ---------------------- | ------------------------------------------------------ |
| 01  | `01_single_takeoff_land/`    | 1      | —          | `MotionCommander`      | Minimal lifecycle — takeoff, hover, land               |
| 02  | `02_single_position_move/`   | 1      | —          | `PositionHlCommander`  | Absolute (x, y, z) waypoints in the world frame        |
| 03  | `03_single_box_pattern/`     | 1      | —          | `MotionCommander`      | Body-frame relative moves + yaw turn                   |
| 04  | `04_swarm_sequential/`       | N      | Sequential | `MotionCommander`      | `Swarm.sequential(...)` — one drone at a time          |
| 05  | `05_swarm_parallel/`         | N      | Parallel   | `PositionHlCommander`  | `Swarm.parallel_safe(...)` + per-drone `args_dict`     |

## Running

From the repository root (so that `utils/` is importable):

```bash
# single drone
python experiments/01_single_takeoff_land/main.py
python experiments/02_single_position_move/main.py
python experiments/03_single_box_pattern/main.py

# swarm
python experiments/04_swarm_sequential/main.py
python experiments/05_swarm_parallel/main.py
```

## Before flying for real

1. Edit the `URI` / `URIS` at the top of the script to match your radios.
2. Make sure each Crazyflie has a working positioning system (Loco/Lighthouse
   for absolute position, or a Flow deck for relative motion).
3. Start the drones in the (x, y) location your script assumes — experiments
   02 and 05 use the world frame, so `(0, 0, 0)` is wherever the
   Kalman filter says it is at startup.
4. Set `DRY_RUN = False` and run.

## Sequential vs. parallel — quick guide

`Swarm` exposes three primitives:

- `swarm.sequential(fn, args_dict=...)` — runs `fn` on each drone one after the other.
- `swarm.parallel(fn, args_dict=...)` — runs `fn` on all drones at the same time, swallowing errors.
- `swarm.parallel_safe(fn, args_dict=...)` — same as `parallel`, but raises on the first failure (preferred).

Use *sequential* for staged actions where simultaneous motion is unsafe
(e.g. taking off in close formation). Use *parallel* for synchronised
behaviour (formations, choreography).
