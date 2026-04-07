# Alpha Build

## Build ID

- `W07-ALPHA-2026-04-03`

## Purpose

This alpha build packages the Week 7 student labs using the repo's existing Python SDK, `UserControl`, `mission_runner`, logging files, and range-sensor support.

## How to run the demo

From the repository root:

```bash
source .venv/bin/activate
python3 examples/run_alpha_labs.py
```

## Regression command

```bash
tools/run_alpha_regression.sh
```

## Included labs

- `examples/lab_01_first_flight.py`
- `examples/lab_square_path.py`
- `examples/lab_03_stop_before_wall.py`

## Notes

- The current map prompt should be answered with `BasicArena`.
- All three labs write `runs/Run_<N>_metrics.json`.
- The updated SDK flow also writes `runs/Run_<N>_run.json` for run metadata.
