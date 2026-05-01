#!/usr/bin/env python3
# tools/run_batch.py
#
# Run one or more mission JSON files in sequence and write runs/batch_summary.csv.
# Creates a fresh controller connection for each mission so collision state resets cleanly.
#
# Usage:
#   python tools/run_batch.py missions/first_flight.json missions/square_path.json
#   python tools/run_batch.py --dir missions/
#   python tools/run_batch.py missions/first_flight.json --repeat 50

import argparse
import asyncio
import csv
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = _REPO_ROOT / "runs" / "batch_summary.csv"


def _sdk_imports():
    """Import SDK modules lazily so --help works without the simulator installed."""
    sys.path.insert(0, str(_REPO_ROOT / "sdk" / "client"))
    from UserControl import UserControl
    from mission_runner import run_mission
    return UserControl, run_mission


FIELDNAMES = ["mission", "run_number", "success", "completion_time_s", "collisions", "failure_reason"]


def _collect_missions(paths: list, repeat: int) -> list:
    missions = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            missions.extend(sorted(path.glob("*.json")))
        elif path.is_file():
            missions.append(path)
        else:
            print(f"Warning: '{p}' not found — skipping.")
    return missions * repeat


async def _run_one(mission_path: Path) -> dict:
    """Connect a fresh controller, run the mission, disconnect. Returns a result row."""
    UserControl, run_mission = _sdk_imports()
    controller = UserControl()
    try:
        controller.connect()
    except Exception as e:
        return {
            "mission": mission_path.name,
            "run_number": "?",
            "success": False,
            "completion_time_s": 0.0,
            "collisions": 0,
            "failure_reason": f"connect failed: {e}",
        }

    try:
        metrics, _ = await run_mission(str(mission_path), controller)
        return {
            "mission": mission_path.name,
            "run_number": controller.runNumber,
            "success": metrics["success"],
            "completion_time_s": metrics["completion_time_s"],
            "collisions": metrics["collisions"],
            "failure_reason": metrics.get("failure_reason") or "",
        }
    except Exception as e:
        return {
            "mission": mission_path.name,
            "run_number": getattr(controller, "runNumber", "?"),
            "success": False,
            "completion_time_s": 0.0,
            "collisions": 0,
            "failure_reason": str(e),
        }
    finally:
        controller.close()


def _write_summary(results: list) -> None:
    total = len(results)
    successes = sum(1 for r in results if r["success"])
    failures = total - successes
    rate = (successes / total * 100) if total else 0.0

    SUMMARY_PATH.parent.mkdir(exist_ok=True)
    with open(SUMMARY_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)
        # Summary rows at the bottom
        f.write("\n")
        f.write(f"TOTAL,{total},,,,\n")
        f.write(f"SUCCESS,{successes},,,,\n")
        f.write(f"FAILED,{failures},,,,\n")
        f.write(f"SUCCESS_RATE,{rate:.1f}%,,,,\n")


def _run_batch(missions: list) -> list:
    results = []
    for i, mission_path in enumerate(missions, 1):
        print(f"[{i}/{len(missions)}] {mission_path.name} ...", end=" ", flush=True)
        result = asyncio.run(_run_one(mission_path))
        status = "PASS" if result["success"] else f"FAIL ({result['failure_reason']})"
        print(f"{status}  ({result['completion_time_s']:.2f}s)")
        results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run mission JSON files in batch and write runs/batch_summary.csv."
    )
    parser.add_argument("missions", nargs="*", help="Mission JSON file paths")
    parser.add_argument("--dir", help="Directory of mission JSON files to run")
    parser.add_argument(
        "--repeat", type=int, default=1,
        help="Repeat the full mission list N times (e.g. --repeat 50 for 50 trials)"
    )
    args = parser.parse_args()

    sources = list(args.missions)
    if args.dir:
        sources.append(args.dir)
    if not sources:
        parser.print_help()
        return 1

    missions = _collect_missions(sources, repeat=args.repeat)
    if not missions:
        print("No mission files found.")
        return 1

    print(f"Starting batch: {len(missions)} run(s)...")
    results = _run_batch(missions)

    total = len(results)
    successes = sum(1 for r in results if r["success"])
    rate = (successes / total * 100) if total else 0.0

    _write_summary(results)

    print(f"\nBatch complete: {successes}/{total} passed ({rate:.1f}%)")
    print(f"Summary written to {SUMMARY_PATH}")

    return 0 if successes == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
