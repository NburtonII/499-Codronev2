# examples/lab_square_path.py
#
# Beginner square-path lab for the Week 7 alpha release.
#
# Prerequisites:
#   1. Start the Unreal simulator.
#   2. When prompted for the map name, enter BasicArena.
#   3. Activate your virtual environment.
#   4. Run from the repo root:
#        python3 examples/lab_square_path.py
#
# Expected success output includes:
#   LAB 2: Square Path
#   success=True
#   collisions=0
#   LAB 2 PASS: Square Path completed.

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "client"))

from UserControl import UserControl  # noqa: E402
from mission_runner import run_mission  # noqa: E402


MISSION_FILE = os.path.join(
    os.path.dirname(__file__), "..", "missions", "square_path.json"
)


async def run_lab():
    mission_path = os.path.abspath(MISSION_FILE)
    controller = UserControl()
    controller.connect()

    try:
        print("LAB 2: Square Path")
        print(f"Mission file: {mission_path}")
        metrics = await run_mission(mission_path, controller)
        print(f"success={metrics['success']}")
        print(f"completion_time_s={metrics['completion_time_s']}")
        print(f"collisions={metrics['collisions']}")
        print(f"min_front_range_cm={metrics['min_front_range_cm']}")
        if metrics["failure_reason"]:
            print(f"failure_reason={metrics['failure_reason']}")
        if not metrics["success"]:
            raise RuntimeError("Square Path mission failed.")
        print("LAB 2 PASS: Square Path completed.")
    finally:
        controller.close()


async def main():
    await run_lab()


if __name__ == "__main__":
    asyncio.run(main())
