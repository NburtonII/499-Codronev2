# tests/test_metrics_schema_min.py

#
# Validates that a metrics dict/file satisfies the Week 5 minimum schema:
#   success (bool), completion_time_s (float >= 0), collisions (int >= 0)
#
# No simulator connection required.
#
# Run from repo root:
#   pytest tests/test_metrics_schema_min.py

import json
import os
import tempfile
import unittest

# ------------------------------------------------------------------
# Schema validator (pure function, no SDK imports needed)
# ------------------------------------------------------------------

REQUIRED_FIELDS = ("success", "completion_time_s", "collisions")
STRUCTURED_FAILURE_REASONS = ("collision", "out_of_bounds", "timeout")


def validate_metrics(metrics):
    """
    Validate a metrics dict against the Week 5 minimum schema.

    Raises:
        ValueError:  If a required field is missing, or a numeric value is out of range.
        TypeError:   If a field has the wrong type.
    """
    for field in REQUIRED_FIELDS:
        if field not in metrics:
            raise ValueError(f"metrics missing required field: '{field}'")

    if not isinstance(metrics["success"], bool):
        raise TypeError(
            f"'success' must be bool, got {type(metrics['success']).__name__}"
        )

    if not isinstance(metrics["completion_time_s"], (int, float)):
        raise TypeError(
            f"'completion_time_s' must be numeric, "
            f"got {type(metrics['completion_time_s']).__name__}"
        )
    if metrics["completion_time_s"] < 0:
        raise ValueError("'completion_time_s' must be >= 0")

    if not isinstance(metrics["collisions"], int):
        raise TypeError(
            f"'collisions' must be int, got {type(metrics['collisions']).__name__}"
        )
    if metrics["collisions"] < 0:
        raise ValueError("'collisions' must be >= 0")

    failure_reason = metrics.get("failure_reason", None)
    if failure_reason is not None and not isinstance(failure_reason, str):
        raise TypeError(
            f"'failure_reason' must be str or None, got {type(failure_reason).__name__}"
        )


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------


class TestMetricsSchemaMin(unittest.TestCase):

    def _valid(self):
        """Return a minimal valid metrics dict."""
        return {
            "success": True,
            "completion_time_s": 12.4,
            "collisions": 0,
            "failure_reason": None,
        }

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    def test_valid_success_metrics_passes(self):
        """A valid successful metrics dict passes schema validation."""
        validate_metrics(self._valid())

    def test_valid_failure_metrics_passes(self):
        """A valid failure metrics dict passes schema validation."""
        m = self._valid()
        m["success"] = False
        m["collisions"] = 1
        m["failure_reason"] = "collision"
        validate_metrics(m)

    def test_zero_completion_time_passes(self):
        """completion_time_s of exactly 0 is valid."""
        m = self._valid()
        m["completion_time_s"] = 0
        validate_metrics(m)

    def test_extra_fields_are_allowed(self):
        """Additional fields beyond the minimum schema are permitted."""
        m = self._valid()
        m["min_front_range_cm"] = 55.0
        validate_metrics(m)

    def test_structured_failure_codes_pass(self):
        """Week 10 structured failure codes remain valid string values."""
        for code in STRUCTURED_FAILURE_REASONS:
            m = self._valid()
            m["success"] = False
            m["failure_reason"] = code
            validate_metrics(m)

    def test_descriptive_failure_string_passes(self):
        m = self._valid()
        m["success"] = False
        m["failure_reason"] = "rotate_to_yaw_async timed out after 2.0s"
        validate_metrics(m)

    # ------------------------------------------------------------------
    # Missing required fields
    # ------------------------------------------------------------------

    def test_missing_success_raises(self):
        m = self._valid()
        del m["success"]
        with self.assertRaises(ValueError):
            validate_metrics(m)

    def test_missing_completion_time_raises(self):
        m = self._valid()
        del m["completion_time_s"]
        with self.assertRaises(ValueError):
            validate_metrics(m)

    def test_missing_collisions_raises(self):
        m = self._valid()
        del m["collisions"]
        with self.assertRaises(ValueError):
            validate_metrics(m)

    # ------------------------------------------------------------------
    # Wrong types
    # ------------------------------------------------------------------

    def test_success_string_raises(self):
        m = self._valid()
        m["success"] = "true"
        with self.assertRaises(TypeError):
            validate_metrics(m)

    def test_success_int_raises(self):
        """An int 1 is not a bool in this strict check."""
        m = self._valid()
        m["success"] = 1
        with self.assertRaises(TypeError):
            validate_metrics(m)

    def test_completion_time_string_raises(self):
        m = self._valid()
        m["completion_time_s"] = "12.4"
        with self.assertRaises(TypeError):
            validate_metrics(m)

    def test_collisions_float_raises(self):
        """collisions must be int, not float."""
        m = self._valid()
        m["collisions"] = 1.0
        with self.assertRaises(TypeError):
            validate_metrics(m)

    def test_failure_reason_int_raises(self):
        m = self._valid()
        m["failure_reason"] = 123
        with self.assertRaises(TypeError):
            validate_metrics(m)

    # ------------------------------------------------------------------
    # Out-of-range values
    # ------------------------------------------------------------------

    def test_negative_completion_time_raises(self):
        m = self._valid()
        m["completion_time_s"] = -0.1
        with self.assertRaises(ValueError):
            validate_metrics(m)

    def test_negative_collisions_raises(self):
        m = self._valid()
        m["collisions"] = -1
        with self.assertRaises(ValueError):
            validate_metrics(m)

    # ------------------------------------------------------------------
    # JSON round-trip
    # ------------------------------------------------------------------

    def test_metrics_json_roundtrip(self):
        """metrics written to JSON and read back still pass schema validation."""
        metrics = self._valid()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(metrics, f)
            path = f.name
        try:
            with open(path) as f:
                loaded = json.load(f)
            validate_metrics(loaded)
            self.assertEqual(loaded["success"], metrics["success"])
            self.assertAlmostEqual(
                loaded["completion_time_s"], metrics["completion_time_s"]
            )
            self.assertEqual(loaded["collisions"], metrics["collisions"])
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
