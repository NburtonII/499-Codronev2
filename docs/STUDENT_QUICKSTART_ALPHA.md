# Student Quickstart Alpha

This guide is for a beginner who has never run the repo before.

## What you will run

1. First Flight
2. Square Path
3. Stop Before Wall

## Repo root

Open a terminal in the repository root before running any commands.

## Python setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python SDK using the repo's existing package files:

```bash
pip install -r sdk/client/projectairsim/requirements.txt
pip install -e sdk/client/projectairsim
```

## Start the simulator

Open the Unreal simulator before running the labs.

When the SDK asks:

```text
Which map is currently open in Unreal? Enter name:
```

enter:

```text
BasicArena
```

## Run Lab 1: First Flight

```bash
python3 examples/lab_01_first_flight.py
```

Expected success output includes:

```text
LAB 1: First Flight
success=True
collisions=0
LAB 1 PASS: First Flight completed.
```

## Run Lab 2: Square Path

```bash
python3 examples/lab_square_path.py
```

Expected success output includes:

```text
LAB 2: Square Path
success=True
collisions=0
LAB 2 PASS: Square Path completed.
```

## Run Lab 3: Stop Before Wall

```bash
python3 examples/lab_03_stop_before_wall.py
```

Expected success output includes:

```text
LAB 3: Stop Before Wall
FrontRange: ... cm
Wall detected at ... cm. Stopping flight.
LAB 3 PASS: Stop Before Wall completed.
```

## Run the full alpha demo

```bash
python3 examples/run_alpha_labs.py
```

Expected success output ends with:

```text
ALPHA DEMO PASS: all three labs completed.
```

## Run the regression suite

```bash
tools/run_alpha_regression.sh
```

Expected success output ends with:

```text
Ran ... tests in ...
OK
```

## Run artifacts

The current repo writes run artifacts using the existing `runs/` layout:

- `runs/Run_<N>_run.json`
- `runs/RunCommands/Run_<N>_Commands.csv`
- `runs/RunTelemetry/Run_<N>_Telemetry.csv`
- `runs/RunEvents/Run_<N>_Events.csv`
- `runs/Run_<N>_metrics.json`
