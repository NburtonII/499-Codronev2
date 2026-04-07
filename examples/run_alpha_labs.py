# examples/run_alpha_labs.py
# Run the Week 7 alpha labs in sequence.

import asyncio

from lab_01_first_flight import run_lab as run_first_flight
from lab_square_path import run_lab as run_square_path
from lab_03_stop_before_wall import run_lab as run_stop_before_wall


async def main():
    print("ALPHA DEMO: starting lab sequence")
    await run_first_flight()
    print()
    await run_square_path()
    print()
    await run_stop_before_wall()
    print("ALPHA DEMO PASS: all three labs completed.")


if __name__ == "__main__":
    asyncio.run(main())
