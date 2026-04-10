"""
Batch command runner that reuses the existing ``UserControl`` command pipeline.

Accepted inputs:
- Python list of command dictionaries
- JSON list
- JSON file path containing either ``[...]`` or ``{"commands": [...]}``

Because ``UserControl.commandParse()`` already treats its second argument as a
duration in seconds, this script accepts both ``duration`` and ``value`` and
maps them to that existing parameter.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_MAP_NAME = "BasicArena"
ZERO_DURATION_COMMANDS = {"Close", "Land", "Reset", "Takeoff"}
AIRBORNE_COMMANDS = {
    "Backward",
    "Down",
    "Forward",
    "Left",
    "Right",
    "Square",
    "Up",
    "Yaw_Left",
    "Yaw_Right",
}
EXAMPLE_COMMANDS = [
    {"command": "Takeoff"},
    {"command": "Forward", "duration": 2},
    {"command": "Land"},
]


class BatchCommandError(RuntimeError):
    """Raised when a batch command cannot safely continue."""


class _CommandStatusTracker:
    """Capture ``save_Command()`` writes without changing UserControl itself."""

    def __init__(self, controller: Any):
        self.controller = controller
        self.last_entry: Optional[Dict[str, Any]] = None
        self._original_save_command = getattr(controller, "save_Command", None)
        if callable(self._original_save_command):
            controller.save_Command = self._tracked_save_command

    def _tracked_save_command(
        self,
        command: str,
        duration: float,
        status: str = "ok",
        notes: str = "",
    ) -> Any:
        self.last_entry = {
            "command": command,
            "duration": duration,
            "status": status,
            "notes": notes,
        }
        return self._original_save_command(
            command,
            duration,
            status=status,
            notes=notes,
        )

    def reset(self) -> None:
        self.last_entry = None

    def restore(self) -> None:
        if callable(self._original_save_command):
            self.controller.save_Command = self._original_save_command


def _ensure_sdk_import_paths() -> None:
    sdk_client_dir = Path(__file__).resolve().parent
    projectairsim_src = sdk_client_dir / "projectairsim" / "src"

    for path in (sdk_client_dir, projectairsim_src):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


def _get_user_control_class():
    _ensure_sdk_import_paths()
    from UserControl import UserControl  # noqa: WPS433

    return UserControl


def _get_logger():
    _ensure_sdk_import_paths()
    try:
        from projectairsim.utils import projectairsim_log  # noqa: WPS433

        return projectairsim_log()
    except Exception:
        return None


def _log_info(message: str) -> None:
    logger = _get_logger()
    if logger is not None:
        logger.info(message)


def _coerce_duration(value: Any) -> float:
    if value in (None, ""):
        return 0
    if isinstance(value, (int, float)):
        duration = float(value)
    elif isinstance(value, str):
        try:
            duration = float(value.strip())
        except ValueError as exc:
            raise ValueError(f"Invalid command duration/value: {value!r}") from exc
    else:
        raise ValueError(f"Invalid command duration/value: {value!r}")

    if duration < 0:
        raise ValueError(f"Command duration must be non-negative: {value!r}")
    return duration


def _coerce_command_collection(payload: Any) -> List[Any]:
    if isinstance(payload, dict):
        if "commands" in payload:
            payload = payload["commands"]
        elif "steps" in payload:
            payload = payload["steps"]
        else:
            raise ValueError("JSON object must contain 'commands' or 'steps'.")

    if not isinstance(payload, list):
        raise ValueError("Batch commands must be provided as a list.")

    return payload


def get_valid_commands(controller: Optional[Any] = None) -> List[str]:
    if controller is not None:
        return list(getattr(controller, "commandList", []))

    user_control_class = _get_user_control_class()
    temp_controller = user_control_class()
    return list(temp_controller.commandList)


def normalize_command_step(
    step: Any,
    valid_commands: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if isinstance(step, str):
        step = {"command": step}

    if not isinstance(step, dict):
        raise ValueError(f"Each batch command must be a dict or string, got {type(step)!r}")

    command = step.get("command")
    if not isinstance(command, str) or not command.strip():
        raise ValueError(f"Batch command is missing a valid 'command': {step!r}")
    command = command.strip()

    duration = _coerce_duration(step.get("duration", step.get("value", 0)))

    if valid_commands is not None and command not in valid_commands:
        raise ValueError(
            f"Unknown command '{command}'. Valid commands: {', '.join(valid_commands)}"
        )

    return {
        "command": command,
        "duration": duration,
    }


def load_commands(commands_source: Any) -> List[Dict[str, Any]]:
    if isinstance(commands_source, list):
        payload = commands_source
    elif isinstance(commands_source, os.PathLike):
        payload = json.loads(Path(commands_source).read_text())
    elif isinstance(commands_source, str):
        stripped = commands_source.strip()
        if stripped.startswith("[") or stripped.startswith("{"):
            payload = json.loads(stripped)
        else:
            source_path = Path(commands_source)
            if not source_path.is_file():
                raise ValueError(
                    "String command sources must be a JSON string or a path to a JSON file."
                )
            payload = json.loads(source_path.read_text())
    else:
        raise ValueError(
            "Commands must be provided as a Python list, JSON string, or JSON file path."
        )

    raw_steps = _coerce_command_collection(payload)
    return [normalize_command_step(step) for step in raw_steps]


def _build_map_selector(controller: Any, preferred_map: str):
    def _select_map():
        if not getattr(controller, "maps_config", None):
            controller._load_maps_config()

        if preferred_map in controller.maps_config:
            controller.current_map = preferred_map
            return controller.maps_config[preferred_map]

        fallback_map = DEFAULT_MAP_NAME
        if fallback_map not in controller.maps_config:
            fallback_map = next(iter(controller.maps_config))

        controller.current_map = fallback_map
        _log_info(
            f"Requested map '{preferred_map}' was not found. "
            f"Using '{fallback_map}' instead."
        )
        return controller.maps_config[fallback_map]

    return _select_map


def connect_controller(map_name: str = DEFAULT_MAP_NAME):
    user_control_class = _get_user_control_class()
    controller = user_control_class()
    controller._detect_map = _build_map_selector(controller, map_name)
    controller.connect()
    return controller


def _maybe_save_event(controller: Any, event_type: str, details: str = "") -> None:
    save_event = getattr(controller, "save_Event", None)
    if callable(save_event):
        save_event(event_type, details)


def _validate_preconditions(controller: Any, command: str) -> None:
    valid_commands = get_valid_commands(controller)
    if command not in valid_commands:
        raise BatchCommandError(
            f"Unknown command '{command}'. Valid commands: {', '.join(valid_commands)}"
        )

    takeoff_state = bool(getattr(controller, "takeOff", False))

    if command == "Takeoff" and takeoff_state:
        raise BatchCommandError("Takeoff cannot run because the drone is already airborne.")
    if command == "Land" and not takeoff_state:
        raise BatchCommandError("Land cannot run because the drone is already on the ground.")
    if command in AIRBORNE_COMMANDS and not takeoff_state:
        raise BatchCommandError(f"{command} requires the drone to take off first.")


def _command_failure_message(
    command: str,
    tracker: _CommandStatusTracker,
) -> Optional[str]:
    if tracker.last_entry is None:
        if command in {"Close", "Reset"}:
            return None
        return f"{command} did not report a completion status."

    if tracker.last_entry["command"] != command:
        return (
            f"{command} completed with an unexpected log entry for "
            f"{tracker.last_entry['command']}."
        )

    if tracker.last_entry["status"] != "ok":
        return tracker.last_entry["notes"] or (
            f"{command} reported status '{tracker.last_entry['status']}'."
        )

    return None


async def execute_batch(
    commands_source: Any,
    controller: Optional[Any] = None,
    map_name: str = DEFAULT_MAP_NAME,
    close_when_done: Optional[bool] = None,
) -> Dict[str, Any]:
    commands = load_commands(commands_source)
    own_controller = controller is None
    if close_when_done is None:
        close_when_done = own_controller

    if own_controller:
        controller = connect_controller(map_name=map_name)

    tracker = _CommandStatusTracker(controller)
    results: List[Dict[str, Any]] = []
    stopped_on_close = False

    print(f"Executing {len(commands)} batch commands...")
    _log_info(f"Batch execution starting with {len(commands)} commands.")

    try:
        for index, step in enumerate(commands, start=1):
            command = step["command"]
            duration = step["duration"]
            duration_text = f"{duration:g}s" if duration or command not in ZERO_DURATION_COMMANDS else "0s"

            print(f"[{index}/{len(commands)}] {command} ({duration_text})")
            _maybe_save_event(
                controller,
                "batch_command_started",
                f"index:{index},command:{command},duration:{duration:g}",
            )

            try:
                _validate_preconditions(controller, command)
                tracker.reset()
                await controller.commandParse(command, duration)

                if getattr(controller, "collision", False):
                    raise BatchCommandError(
                        "Collision detected during batch execution."
                    )

                failure_message = _command_failure_message(command, tracker)
                if failure_message is not None:
                    raise BatchCommandError(failure_message)

                result = {
                    "index": index,
                    "command": command,
                    "duration": duration,
                    "status": "success",
                }
                results.append(result)
                print(f"  SUCCESS: {command}")
                _maybe_save_event(
                    controller,
                    "batch_command_succeeded",
                    f"index:{index},command:{command},duration:{duration:g}",
                )

                if command == "Close":
                    stopped_on_close = True
                    print("Batch stopped by Close command.")
                    break

            except Exception as exc:
                result = {
                    "index": index,
                    "command": command,
                    "duration": duration,
                    "status": "failed",
                    "error": str(exc),
                }
                results.append(result)
                print(f"  FAILED: {exc}")
                _maybe_save_event(
                    controller,
                    "batch_command_failed",
                    f"index:{index},command:{command},error:{exc}",
                )
                break

        failed_result = next((item for item in results if item["status"] == "failed"), None)
        summary = {
            "success": failed_result is None,
            "completed": sum(1 for item in results if item["status"] == "success"),
            "total": len(commands),
            "failure_reason": failed_result["error"] if failed_result else None,
            "failed_command": failed_result["command"] if failed_result else None,
            "stopped_on_close": stopped_on_close,
            "results": results,
        }

        if summary["success"]:
            print(
                f"Batch complete: {summary['completed']}/{summary['total']} commands succeeded."
            )
        else:
            print(
                f"Batch stopped on '{summary['failed_command']}': "
                f"{summary['failure_reason']}"
            )

        return summary

    finally:
        tracker.restore()
        if own_controller and close_when_done and not stopped_on_close:
            controller.close()


def run_batch(
    commands_source: Any,
    map_name: str = DEFAULT_MAP_NAME,
) -> Dict[str, Any]:
    return asyncio.run(execute_batch(commands_source, map_name=map_name))


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Execute existing UserControl commands from a JSON file or JSON list.",
    )
    parser.add_argument(
        "commands",
        nargs="?",
        help="JSON file path or raw JSON string. Defaults to the built-in example batch.",
    )
    parser.add_argument(
        "--map",
        default=DEFAULT_MAP_NAME,
        help=f"Map name to use when connecting the controller. Defaults to {DEFAULT_MAP_NAME}.",
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Run the built-in example batch command list.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_argument_parser()
    args = parser.parse_args(argv)

    commands_source: Any
    if args.example or not args.commands:
        commands_source = EXAMPLE_COMMANDS
    else:
        commands_source = args.commands

    summary = run_batch(commands_source, map_name=args.map)
    return 0 if summary["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
