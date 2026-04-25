import argparse
import asyncio
import csv
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SDK_CLIENT_DIR = REPO_ROOT / "sdk" / "client"

if str(SDK_CLIENT_DIR) not in sys.path:
    sys.path.insert(0, str(SDK_CLIENT_DIR))

from batchCommands import connect_controller  # noqa: E402
from mission_runner import load_mission, run_mission  # noqa: E402


DEFAULT_MAP_NAME = "BasicArena"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "runs" / "batch_summary.csv"
SUMMARY_COLUMNS = [
    "mission",
    "success",
    "completion_time_s",
    "collisions",
    "failure_reason",
]


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run multiple mission JSON files and write runs/batch_summary.csv.",
    )
    parser.add_argument(
        "missions",
        nargs="+",
        help="One or more mission JSON paths.",
    )
    parser.add_argument(
        "--map",
        default=DEFAULT_MAP_NAME,
        help=f"Map name to use when connecting the simulator. Defaults to {DEFAULT_MAP_NAME}.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Output CSV path. Defaults to {DEFAULT_OUTPUT_PATH}.",
    )
    return parser.parse_args(argv)


def _normalise_mission_paths(mission_args):
    paths = []
    for mission_arg in mission_args:
        mission_path = Path(mission_arg)
        if not mission_path.is_absolute():
            mission_path = (Path.cwd() / mission_path).resolve()
        paths.append(mission_path)
    return paths


def _format_success(value):
    return "true" if value else "false"


def _format_failure_reason(value):
    return "" if value in (None, "") else str(value)


def _write_summary(output_path, rows):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_runs = len(rows)
    success_count = sum(1 for row in rows if row["success"] == "true")
    failure_count = total_runs - success_count
    success_rate = (success_count / total_runs * 100.0) if total_runs else 0.0

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
        writer.writerow(
            {
                "mission": f"SUMMARY total_runs={total_runs}",
                "success": f"success_count={success_count}",
                "completion_time_s": f"failure_count={failure_count}",
                "collisions": "",
                "failure_reason": f"success_rate={success_rate:.2f}%",
            }
        )


async def _run_batch(mission_paths, map_name):
    rows = []

    for mission_path in mission_paths:
        load_mission(str(mission_path))
        controller = connect_controller(map_name=map_name)
        try:
            metrics, _ = await run_mission(str(mission_path), controller)
        finally:
            controller.close()

        rows.append(
            {
                "mission": mission_path.name,
                "success": _format_success(metrics["success"]),
                "completion_time_s": metrics["completion_time_s"],
                "collisions": metrics["collisions"],
                "failure_reason": _format_failure_reason(metrics.get("failure_reason")),
            }
        )

    return rows


def main(argv=None):
    args = _parse_args(argv)
    mission_paths = _normalise_mission_paths(args.missions)
    rows = asyncio.run(_run_batch(mission_paths, map_name=args.map))
    _write_summary(args.output, rows)
    print(f"Wrote batch summary to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
