# tests/test_batch_commands.py

import asyncio
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "client"))

from batchCommands import execute_batch, load_commands, normalize_command_step  # noqa: E402


class FakeController:
    def __init__(self):
        self.commandList = [
            "Reset",
            "Close",
            "Takeoff",
            "State_Polling",
            "Land",
            "Forward",
            "Backward",
            "Left",
            "Right",
            "Up",
            "Down",
            "Yaw_Left",
            "Yaw_Right",
            "Square",
        ]
        self.takeOff = False
        self.collision = False
        self.saved_commands = []
        self.saved_events = []
        self.closed = False

    async def commandParse(self, command, duration):
        if command == "Takeoff":
            self.takeOff = True
            self.save_Command(command, duration, status="ok", notes="")
            return

        if command == "Land":
            self.takeOff = False
            self.save_Command(command, duration, status="ok", notes="")
            return

        if command == "Forward" and duration == 99:
            self.save_Command(
                command,
                duration,
                status="failed",
                notes="simulated forward failure",
            )
            return

        if command == "Close":
            self.close()
            return

        self.save_Command(command, duration, status="ok", notes="")

    def save_Command(self, command, duration, status="ok", notes=""):
        self.saved_commands.append(
            {
                "command": command,
                "duration": duration,
                "status": status,
                "notes": notes,
            }
        )

    def save_Event(self, event_type, details=""):
        self.saved_events.append((event_type, details))

    def close(self):
        self.closed = True


class TestBatchCommands(unittest.TestCase):
    def test_normalize_command_uses_value_alias(self):
        step = normalize_command_step(
            {"command": "Forward", "value": "2.5"},
            valid_commands=["Forward"],
        )
        self.assertEqual(step["command"], "Forward")
        self.assertEqual(step["duration"], 2.5)

    def test_load_commands_accepts_json_file(self):
        payload = {
            "commands": [
                {"command": "Takeoff"},
                {"command": "Forward", "duration": 2},
                {"command": "Land"},
            ]
        }
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        try:
            json.dump(payload, temp_file)
            temp_file.close()

            commands = load_commands(temp_file.name)
            self.assertEqual([item["command"] for item in commands], ["Takeoff", "Forward", "Land"])
            self.assertEqual(commands[1]["duration"], 2.0)
        finally:
            os.unlink(temp_file.name)

    def test_execute_batch_stops_after_first_failure(self):
        controller = FakeController()
        commands = [
            {"command": "Takeoff"},
            {"command": "Forward", "duration": 1},
            {"command": "Forward", "duration": 99},
            {"command": "Land"},
        ]

        summary = asyncio.run(
            execute_batch(
                commands,
                controller=controller,
                close_when_done=False,
            )
        )

        self.assertFalse(summary["success"])
        self.assertEqual(summary["failed_command"], "Forward")
        self.assertEqual(len(summary["results"]), 3)
        self.assertEqual(
            [item["command"] for item in controller.saved_commands],
            ["Takeoff", "Forward", "Forward"],
        )


if __name__ == "__main__":
    unittest.main()
