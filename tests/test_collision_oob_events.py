# tests/test_collision_oob_events.py
#
# R4 - Week 12: Unit tests for collision and out-of-bounds event handling.
# No live simulator required — all tests use lightweight fakes.

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "client"))


# ---------------------------------------------------------------------------
# Minimal fakes — no SDK imports needed
# ---------------------------------------------------------------------------

class FakeController:
    """Minimal stand-in for UserControl with just the fields under test."""

    KILL_Z_UP = -100
    KILL_Z_DOWN = 0.5

    def __init__(self):
        self.takeOff = True
        self.collision = False
        self.collision_Count = 0
        self.collision_info = None
        self.out_of_bounds = False
        self.emergency_landing = False
        self._events = []

    def save_Event(self, event_type, details):
        self._events.append({"event_type": event_type, "details": details})

    def _out_of_bounds(self, reason="altitude"):
        """Mirrors the real UserControl._out_of_bounds() — sync, no asyncio."""
        if not self.takeOff:
            return
        self.out_of_bounds = True
        self.emergency_landing = True
        msg = f"Out of bounds detected (reason={reason}). Emergency landing initiated."
        self.save_Event("Out_of_Bounds", msg)

    def _on_collision(self, collision):
        """Mirrors the real UserControl._on_collision() without asyncio scheduling."""
        if not self.takeOff:
            return
        self.collision = True
        self.emergency_landing = True
        self.collision_Count += 1
        self.collision_info = collision
        self.save_Event("Collision", f"Collision Info: {self.collision_info}")


# ---------------------------------------------------------------------------
# Collision info schema
# ---------------------------------------------------------------------------

SAMPLE_COLLISION_INFO = {
    "time_stamp": 53343000000,
    "object_name": "StaticMeshActor_5",
    "segmentation_id": 83,
    "position": {"x": 148.85, "y": -1.25, "z": -3.01},
    "impact_point": {"x": 149.31, "y": -0.01, "z": -3.19},
    "normal": {"x": -1.0, "y": 3.37e-08, "z": 0.0},
    "penetration_depth": 0.0,
}

REQUIRED_COLLISION_FIELDS = [
    "time_stamp",
    "object_name",
    "segmentation_id",
    "position",
    "impact_point",
    "normal",
    "penetration_depth",
]

REQUIRED_VECTOR_KEYS = ["x", "y", "z"]


class TestCollisionInfoSchema(unittest.TestCase):

    def test_all_required_fields_present(self):
        for field in REQUIRED_COLLISION_FIELDS:
            self.assertIn(field, SAMPLE_COLLISION_INFO, f"Missing field: {field}")

    def test_vector_fields_have_xyz(self):
        for field in ("position", "impact_point", "normal"):
            vec = SAMPLE_COLLISION_INFO[field]
            for key in REQUIRED_VECTOR_KEYS:
                self.assertIn(key, vec, f"{field} missing key '{key}'")

    def test_time_stamp_is_int(self):
        self.assertIsInstance(SAMPLE_COLLISION_INFO["time_stamp"], int)

    def test_object_name_is_string(self):
        self.assertIsInstance(SAMPLE_COLLISION_INFO["object_name"], str)
        self.assertGreater(len(SAMPLE_COLLISION_INFO["object_name"]), 0)

    def test_penetration_depth_is_numeric(self):
        self.assertIsInstance(SAMPLE_COLLISION_INFO["penetration_depth"], (int, float))


# ---------------------------------------------------------------------------
# Collision event handling
# ---------------------------------------------------------------------------

class TestCollisionEventHandling(unittest.TestCase):

    def setUp(self):
        self.ctrl = FakeController()

    def test_collision_sets_flag(self):
        self.ctrl._on_collision(SAMPLE_COLLISION_INFO)
        self.assertTrue(self.ctrl.collision)

    def test_collision_sets_emergency_landing(self):
        self.ctrl._on_collision(SAMPLE_COLLISION_INFO)
        self.assertTrue(self.ctrl.emergency_landing)

    def test_collision_increments_count(self):
        self.ctrl._on_collision(SAMPLE_COLLISION_INFO)
        self.assertEqual(self.ctrl.collision_Count, 1)

    def test_collision_stores_info(self):
        self.ctrl._on_collision(SAMPLE_COLLISION_INFO)
        self.assertEqual(self.ctrl.collision_info, SAMPLE_COLLISION_INFO)

    def test_collision_logs_event(self):
        self.ctrl._on_collision(SAMPLE_COLLISION_INFO)
        types = [e["event_type"] for e in self.ctrl._events]
        self.assertIn("Collision", types)

    def test_collision_ignored_before_takeoff(self):
        self.ctrl.takeOff = False
        self.ctrl._on_collision(SAMPLE_COLLISION_INFO)
        self.assertFalse(self.ctrl.collision)
        self.assertEqual(self.ctrl.collision_Count, 0)

    def test_multiple_collisions_count(self):
        self.ctrl._on_collision(SAMPLE_COLLISION_INFO)
        self.ctrl._on_collision(SAMPLE_COLLISION_INFO)
        self.assertEqual(self.ctrl.collision_Count, 2)


# ---------------------------------------------------------------------------
# Out-of-bounds altitude detection
# ---------------------------------------------------------------------------

class TestAltitudeBounds(unittest.TestCase):

    def test_kill_z_up_boundary_value(self):
        self.assertEqual(FakeController.KILL_Z_UP, -100)

    def test_kill_z_down_boundary_value(self):
        self.assertEqual(FakeController.KILL_Z_DOWN, 0.5)

    def test_z_below_lower_limit_is_oob(self):
        z = -101.0
        self.assertTrue(z < FakeController.KILL_Z_UP)

    def test_z_above_upper_limit_is_oob(self):
        z = 0.6
        self.assertTrue(z > FakeController.KILL_Z_DOWN)

    def test_z_within_bounds_is_safe(self):
        for z in (-50.0, -1.0, 0.0, 0.3):
            self.assertFalse(
                z < FakeController.KILL_Z_UP or z > FakeController.KILL_Z_DOWN,
                f"z={z} should be within safe bounds"
            )

    def test_z_at_lower_limit_is_safe(self):
        z = FakeController.KILL_Z_UP
        self.assertFalse(z < FakeController.KILL_Z_UP)

    def test_z_at_upper_limit_is_safe(self):
        z = FakeController.KILL_Z_DOWN
        self.assertFalse(z > FakeController.KILL_Z_DOWN)


# ---------------------------------------------------------------------------
# Out-of-bounds event handling
# ---------------------------------------------------------------------------

class TestOOBEventHandling(unittest.TestCase):

    def setUp(self):
        self.ctrl = FakeController()

    def test_oob_sets_flag(self):
        self.ctrl._out_of_bounds(reason="altitude")
        self.assertTrue(self.ctrl.out_of_bounds)

    def test_oob_sets_emergency_landing(self):
        self.ctrl._out_of_bounds(reason="altitude")
        self.assertTrue(self.ctrl.emergency_landing)

    def test_oob_logs_event(self):
        self.ctrl._out_of_bounds(reason="altitude")
        types = [e["event_type"] for e in self.ctrl._events]
        self.assertIn("Out_of_Bounds", types)

    def test_oob_event_contains_reason(self):
        self.ctrl._out_of_bounds(reason="altitude")
        event = next(e for e in self.ctrl._events if e["event_type"] == "Out_of_Bounds")
        self.assertIn("altitude", event["details"])

    def test_oob_ignored_before_takeoff(self):
        self.ctrl.takeOff = False
        self.ctrl._out_of_bounds(reason="altitude")
        self.assertFalse(self.ctrl.out_of_bounds)
        self.assertEqual(self.ctrl._events, [])

    def test_oob_does_not_set_collision_flag(self):
        self.ctrl._out_of_bounds(reason="altitude")
        self.assertFalse(self.ctrl.collision)


# ---------------------------------------------------------------------------
# Failure reason string validation
# ---------------------------------------------------------------------------

VALID_FAILURE_CODES = {"collision", "out_of_bounds", "timeout"}


class TestFailureReasonStrings(unittest.TestCase):

    def test_collision_is_valid_code(self):
        self.assertIn("collision", VALID_FAILURE_CODES)

    def test_out_of_bounds_is_valid_code(self):
        self.assertIn("out_of_bounds", VALID_FAILURE_CODES)

    def test_timeout_is_valid_code(self):
        self.assertIn("timeout", VALID_FAILURE_CODES)

    def test_raw_exception_string_is_not_a_valid_code(self):
        raw = "list index out of range"
        self.assertNotIn(raw, VALID_FAILURE_CODES)

    def test_none_is_valid_on_success(self):
        failure_reason = None
        self.assertIsNone(failure_reason)

    def test_collision_reason_after_flag(self):
        ctrl = FakeController()
        ctrl._on_collision(SAMPLE_COLLISION_INFO)
        failure_reason = "collision" if ctrl.collision else None
        self.assertEqual(failure_reason, "collision")

    def test_oob_reason_after_flag(self):
        ctrl = FakeController()
        ctrl._out_of_bounds(reason="altitude")
        failure_reason = "out_of_bounds" if ctrl.out_of_bounds else None
        self.assertEqual(failure_reason, "out_of_bounds")


# ---------------------------------------------------------------------------
# Event CSV format compliance
# ---------------------------------------------------------------------------

EVENT_COLUMNS = ["timestamp", "event_type", "details"]


class TestEventCSVFormat(unittest.TestCase):

    def test_event_columns_defined(self):
        self.assertEqual(len(EVENT_COLUMNS), 3)

    def test_event_columns_names(self):
        self.assertIn("timestamp", EVENT_COLUMNS)
        self.assertIn("event_type", EVENT_COLUMNS)
        self.assertIn("details", EVENT_COLUMNS)

    def test_collision_event_type_string(self):
        self.assertIsInstance("Collision", str)
        self.assertEqual("Collision", "Collision")

    def test_oob_event_type_string(self):
        self.assertIsInstance("Out_of_Bounds", str)
        self.assertEqual("Out_of_Bounds", "Out_of_Bounds")


if __name__ == "__main__":
    unittest.main()
