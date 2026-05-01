#!/usr/bin/env python3
# tools/plot_telemetry.py
#
# Plain-text log viewer for Run_N_Telemetry.csv files.
# No external dependencies required.
#
# Usage:
#   python tools/plot_telemetry.py runs/RunTelemetry/Run_25_Telemetry.csv
#   python tools/plot_telemetry.py --latest
#   python tools/plot_telemetry.py --run 25

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_TELEMETRY_DIR = _REPO_ROOT / "runs" / "RunTelemetry"


def _find_latest() -> Path:
    files = sorted(_TELEMETRY_DIR.glob("Run_*_Telemetry.csv"), key=lambda f: f.stat().st_mtime)
    if not files:
        raise FileNotFoundError(f"No telemetry files found in {_TELEMETRY_DIR}")
    return files[-1]


def _find_by_run(n: int) -> Path:
    path = _TELEMETRY_DIR / f"Run_{n}_Telemetry.csv"
    if not path.exists():
        raise FileNotFoundError(f"No telemetry file for run {n}: {path}")
    return path


def _parse_collision(raw: str) -> int:
    """Accept '0'/'1', 'True'/'False', or empty — always return int 0 or 1."""
    v = raw.strip().lower()
    if v in ("true", "1"):
        return 1
    return 0


def _parse_row(parts: list) -> dict | None:
    """Parse one CSV line into a telemetry dict. Returns None on header/bad rows."""
    if len(parts) < 8:
        return None
    # Skip header row
    if parts[0].strip().lower() == "timestamp":
        return None
    try:
        return {
            "timestamp": parts[0],
            "x": float(parts[1]),
            "y": float(parts[2]),
            "z": float(parts[3]),
            "collision": _parse_collision(parts[8]) if len(parts) > 8 else 0,
            "front_range_cm": float(parts[9]) if len(parts) > 9 and parts[9].strip() else None,
            "bottom_range_cm": float(parts[10]) if len(parts) > 10 and parts[10].strip() else None,
        }
    except (ValueError, IndexError):
        return None


def _load(path: Path) -> list:
    rows = []
    with open(path, newline="") as f:
        for line in f:
            row = _parse_row(line.strip().split(","))
            if row is not None:
                rows.append(row)
    return rows


def _sparkline(values: list, width: int = 60) -> str:
    bars = "._-=+#@$"
    lo, hi = min(values), max(values)
    span = hi - lo if hi != lo else 1.0
    step = max(1, len(values) // width)
    sampled = values[::step][:width]
    return "".join(bars[int((v - lo) / span * (len(bars) - 1))] for v in sampled)


def _display(rows: list, path: Path) -> None:
    if not rows:
        print("No valid telemetry rows found.")
        return

    # NED frame: negate z for display as altitude above ground
    altitudes = [-r["z"] for r in rows]
    xs = [r["x"] for r in rows]
    ys = [r["y"] for r in rows]
    collision_rows = [r for r in rows if r["collision"]]
    front_ranges = [r["front_range_cm"] for r in rows if r["front_range_cm"] is not None]
    bottom_ranges = [r["bottom_range_cm"] for r in rows if r["bottom_range_cm"] is not None]

    print()
    sep = "=" * max(0, 50 - len(path.name))
    print(f"--- Telemetry: {path.name} {sep}")
    print(f"  Rows          : {len(rows)}")
    print(f"  Start         : {rows[0]['timestamp']}")
    print(f"  End           : {rows[-1]['timestamp']}")
    print(f"  X range (m)   : {min(xs):>9.3f}  to  {max(xs):.3f}")
    print(f"  Y range (m)   : {min(ys):>9.3f}  to  {max(ys):.3f}")
    print(f"  Altitude (m)  : {min(altitudes):>9.3f}  to  {max(altitudes):.3f}")

    if collision_rows:
        print(f"  Collisions    : {len(collision_rows)} event(s)  [first at {collision_rows[0]['timestamp']}]")
    else:
        print(f"  Collisions    : none")

    if front_ranges:
        avg_fr = sum(front_ranges) / len(front_ranges)
        print(f"  Front range   : min={min(front_ranges):.1f} cm  max={max(front_ranges):.1f} cm  avg={avg_fr:.1f} cm")
    else:
        print(f"  Front range   : no readings")

    if bottom_ranges:
        avg_br = sum(bottom_ranges) / len(bottom_ranges)
        print(f"  Bottom range  : min={min(bottom_ranges):.1f} cm  max={max(bottom_ranges):.1f} cm  avg={avg_br:.1f} cm")
    else:
        print(f"  Bottom range  : no readings")

    # Altitude sparkline (ASCII only)
    if len(altitudes) > 1:
        spark = _sparkline(altitudes)
        print()
        print(f"  Altitude profile ({min(len(altitudes), 60)} samples):")
        print(f"  {max(altitudes):.2f}m ^")
        print(f"  {'':6} |{spark}")
        print(f"  {min(altitudes):.2f}m v")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Plain-text viewer for Run_N_Telemetry.csv files."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("file", nargs="?", help="Path to a telemetry CSV file")
    group.add_argument("--latest", action="store_true", help="Use the most recently modified telemetry file")
    group.add_argument("--run", type=int, metavar="N", help="View telemetry for run number N")
    args = parser.parse_args()

    try:
        if args.latest or (not args.file and args.run is None):
            path = _find_latest()
            print(f"Using latest: {path.name}")
        elif args.run is not None:
            path = _find_by_run(args.run)
        else:
            path = Path(args.file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    if not path.exists():
        print(f"File not found: {path}")
        return 1

    rows = _load(path)
    _display(rows, path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
