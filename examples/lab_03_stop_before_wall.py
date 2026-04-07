# examples/lab_03_stop_before_wall.py
#
# Beginner range-sensor lab for the Week 7 alpha release.
#
# Prerequisites:
#   1. Start the Unreal simulator.
#   2. When prompted for the map name, enter BasicArena.
#   3. Activate your virtual environment.
#   4. Run from the repo root:
#        python3 examples/lab_03_stop_before_wall.py
#
# Expected success output includes:
#   LAB 3: Stop Before Wall
#   FrontRange: ... cm
#   Wall detected at ... cm. Stopping flight.
#   LAB 3 PASS: Stop Before Wall completed.

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "client"))

from UserControl import UserControl  # noqa: E402
from mission_runner import write_metrics  # noqa: E402
from range_sensor import get_front_range  # noqa: E402

STOP_THRESHOLD_M = 2.0
POLL_INTERVAL_S = 0.5
FLY_DURATION_S = 10.0


async def run_lab():
    controller = UserControl()
    controller.connect()
    stopped_for_wall = False
    front_range_readings_cm = []

    try:
        print("LAB 3: Stop Before Wall")
        print("Taking off...")
        await controller.commandParse("Takeoff", 0)

        print(f"Flying forward. Will stop when FrontRange <= {STOP_THRESHOLD_M:.1f} m.")
        fly_task = asyncio.create_task(controller.commandParse("Forward", FLY_DURATION_S))

        elapsed = 0.0
        while elapsed < FLY_DURATION_S:
            await asyncio.sleep(POLL_INTERVAL_S)
            elapsed += POLL_INTERVAL_S

            distance_m = await get_front_range(controller, timeout_s=0.5)
            if distance_m is None:
                print(f"  [{elapsed:.1f}s] FrontRange: no reading")
                continue

            distance_cm = distance_m * 100.0
            front_range_readings_cm.append(distance_cm)
            print(f"  [{elapsed:.1f}s] FrontRange: {distance_cm:.1f} cm")
            if distance_m <= STOP_THRESHOLD_M:
                stopped_for_wall = True
                print(f"  Wall detected at {distance_cm:.1f} cm. Stopping flight.")
                fly_task.cancel()
                await controller.commandParse("State_Polling", 1)
                break

        try:
            await fly_task
        except asyncio.CancelledError:
            pass

        print("Landing...")
        await controller.commandParse("Land", 0)

        metrics = {
            "success": stopped_for_wall,
            "completion_time_s": round(elapsed, 3),
            "collisions": 1 if controller.collision else 0,
            "failure_reason": None if stopped_for_wall else "threshold_not_reached",
            "min_front_range_cm": round(min(front_range_readings_cm), 3) if front_range_readings_cm else None,
        }
        write_metrics(metrics, controller)

        if not stopped_for_wall:
            raise RuntimeError("Stop Before Wall did not trigger before the safety timeout.")
        print("LAB 3 PASS: Stop Before Wall completed.")
    finally:
        controller.close()


async def main():
    await run_lab()


if __name__ == "__main__":
    asyncio.run(main())
