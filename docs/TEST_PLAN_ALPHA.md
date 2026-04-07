# Alpha Test Plan

## Goal

Prevent breakage in the Week 7 alpha labs and in the minimum logging and metrics outputs.

## Single regression command

```bash
tools/run_alpha_regression.sh
```

This runs:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Required coverage

The alpha suite must cover:

1. Basic flight flow
2. Square-path mission flow
3. Front-range stop behavior

## Automated tests in the repo

- `tests/test_mission_parser.py`
  - validates `mission_runner.load_mission()`
  - validates `missions/first_flight.json`
  - validates `missions/square_path.json`
- `tests/test_alpha_lab_assets.py`
  - validates the alpha lab entry points, quickstart commands, and regression runner
- `tests/test_range_timeout_conversion.py`
  - validates stop-threshold logic and range timing math
- `tests/test_range_columns_present.py`
  - validates Week 6 telemetry and metric fields
- `tests/test_metrics_schema_min.py`
  - validates the minimum metrics schema

## Manual alpha check

Run these with Unreal already open:

1. `python3 examples/lab_01_first_flight.py`
2. `python3 examples/lab_square_path.py`
3. `python3 examples/lab_03_stop_before_wall.py`
4. `python3 examples/run_alpha_labs.py`

## Pass criteria

- Automated tests pass.
- Each lab reaches its success print.
- Each lab produces run metadata, command logs, telemetry logs, and metrics.
- Stop Before Wall stops before the obstacle and lands cleanly.
- New run artifacts appear under `runs/`.
