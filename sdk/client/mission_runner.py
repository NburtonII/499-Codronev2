# sdk/client/mission_runner.py

#
# Reads a JSON mission config and executes each step via UserControl.commandParse().
# Writes runs/Run_{N}_metrics.json on completion using the existing run-numbering
# convention established by UserControl (runs/Startup.json).
#
# Public API:
#   load_mission(json_path)              -> list of step dicts  (pure, sync, testable)
#   run_mission(json_path, controller)   -> metrics dict        (async, requires connected controller)

import csv
import json
import os
import time

from range_sensor import get_front_range

# Must match UserControl.commandList exactly (case-sensitive).
VALID_COMMANDS = [
    "Reset", "Close", "Takeoff", "State_Polling", "Land",
    "Forward", "Backward", "Left", "Right", "Up", "Down",
    "Yaw_Left", "Yaw_Right",
]

def _load_mission_document(json_path):
    with open(json_path, "r") as f:
        mission = json.load(f)

    if "steps" not in mission:
        raise ValueError(f"Mission file missing 'steps' key: {json_path}")

    steps = mission["steps"]

    if not isinstance(steps, list) or len(steps) == 0:
        raise ValueError(f"Mission 'steps' must be a non-empty list: {json_path}")

    for i, step in enumerate(steps):
        if "command" not in step:
            raise ValueError(f"Step {i} missing required field 'command'")
        if "duration" not in step:
            raise ValueError(f"Step {i} missing required field 'duration'")
        if step["command"] not in VALID_COMMANDS:
            raise ValueError(
                f"Step {i} has unknown command: '{step['command']}'. "
                f"Valid commands: {VALID_COMMANDS}"
            )
        if not isinstance(step["duration"], (int, float)) or step["duration"] < 0:
            raise ValueError(
                f"Step {i} has invalid duration: '{step['duration']}'. "
                f"Must be a non-negative number."
            )

    return mission


def load_mission(json_path):
    """
    Load and validate a mission JSON file.

    Args:
        json_path (str): Path to the mission JSON file.

    Returns:
        list: Validated list of step dicts, each with 'command' and 'duration'.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError:        If the file structure or step fields are invalid.
    """
    mission = _load_mission_document(json_path)
    return mission["steps"]


def _normalise_exception_text(exc):
    return str(exc).strip()


def _is_timeout_text(text):
    lowered = text.lower()
    return "timeout" in lowered or "timed out" in lowered


def _controller_out_of_bounds(controller):
    out_of_bounds_method = getattr(controller, "_out_of_bounds", None)
    if callable(out_of_bounds_method):
        try:
            return bool(out_of_bounds_method())
        except Exception:
            pass

    return bool(getattr(controller, "out_of_bounds", False))


def _last_command_entry(controller):
    command_file = getattr(controller, "CommandFilePath", None)
    if not command_file or not os.path.exists(command_file):
        return None

    last_row = None
    with open(command_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row:
                last_row = row

    return last_row


def _failure_reason_from_controller(controller):
    if bool(getattr(controller, "collision", False)):
        return "collision"
    if _controller_out_of_bounds(controller):
        return "out_of_bounds"
    return None


def _failure_reason_from_exception(exc):
    message = _normalise_exception_text(exc)
    if _is_timeout_text(message):
        return "timeout"
    return message or exc.__class__.__name__


def _failure_reason_from_command_entry(controller, expected_command):
    entry = _last_command_entry(controller)
    if not entry:
        return None

    logged_command = (entry.get("command") or "").strip()
    status = (entry.get("status") or "").strip().lower()
    notes = (entry.get("notes") or "").strip()

    if logged_command and logged_command != expected_command:
        return None

    if status in ("", "ok"):
        return None

    if _is_timeout_text(notes):
        return "timeout"

    controller_reason = _failure_reason_from_controller(controller)
    if controller_reason is not None:
        return controller_reason

    return notes or f"{expected_command} reported status '{status}'"


async def run_mission(json_path, controller):
    """
    Execute a mission from a JSON config file using a connected UserControl instance.

    Reads steps from the JSON file, executes each via controller.commandParse(),
    and writes a metrics.json file to runs/Run_{N}_metrics.json on completion.

    Args:
        json_path  (str):         Path to the mission JSON file.
        controller (UserControl): A connected, armed UserControl instance.

    Returns:
        dict: Metrics with keys: success, completion_time_s, collisions, failure_reason.
    """
    mission = _load_mission_document(json_path)
    steps = mission["steps"]
    description = mission.get("description", "")
    start_time = time.time()
    success = True
    failure_reason = None
    front_range_readings = []

    try:
        for step in steps:
            command = step["command"]
            duration = step["duration"]

            await controller.commandParse(command, duration)

            reading_m = await get_front_range(controller, timeout_s=0.5)
            if reading_m is not None:
                front_range_readings.append(reading_m * 100.0)

            command_failure = _failure_reason_from_command_entry(controller, command)
            if command_failure is not None:
                success = False
                failure_reason = command_failure
                break

            controller_failure = _failure_reason_from_controller(controller)
            if controller_failure is not None:
                success = False
                failure_reason = controller_failure
                break

    except Exception as e:
        success = False
        failure_reason = _failure_reason_from_exception(e)

    completion_time_s = round(time.time() - start_time, 3)
    collisions = 1 if bool(getattr(controller, "collision", False)) else 0
    min_front_range_cm = round(min(front_range_readings), 3) if front_range_readings else None

    metrics = {
        "description": description,
        "success": success,
        "completion_time_s": completion_time_s,
        "collisions": collisions,
        "failure_reason": None if success else failure_reason,
        "min_front_range_cm": min_front_range_cm,
    }

    _write_metrics(metrics, controller)
    return metrics, steps


def _write_metrics(metrics, controller):
    """
    Write the metrics dict to runs/Run_{N}_metrics.json.

    Follows the existing run-file naming convention:
      runs/Run_{N}_Commands.csv
      runs/Run_{N}_Telemetry.csv
      runs/Run_{N}_metrics.json   <- written here
    """
    metrics_path = os.path.join(
        controller.project_root,
        "runs",
        f"Run_{controller.runNumber}_metrics.json",
    )
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)


def write_metrics(metrics, controller):
    """
    Public wrapper for writing metrics using the repo's existing run naming.

    Args:
        metrics (dict): Metrics payload to persist.
        controller: Connected UserControl instance for resolving the run number.
    """
    _write_metrics(metrics, controller)
