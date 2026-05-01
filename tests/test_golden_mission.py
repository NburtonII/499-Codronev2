# tests/test_golden_mission.py
#
# Golden regression test for the first_flight mission.
# Requires a live simulator — automatically skipped when the simulator is unreachable.
#
# Run offline suite (skips this file):
#   pytest tests/ -m "not integration"
#
# Run with live simulator:
#   pytest tests/test_golden_mission.py -m integration -v

import asyncio
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "client"))

MISSION_PATH = os.path.join(os.path.dirname(__file__), "..", "missions", "first_flight.json")
BASELINE_PATH = os.path.join(os.path.dirname(__file__), "golden", "first_flight_baseline.json")

# Hard tolerance bands — mission must always pass these regardless of baseline.
COMPLETION_TIME_CEILING_S = 60
COMPLETION_TIME_FLOOR_S = 0.5


def _load_baseline():
    with open(BASELINE_PATH) as f:
        return json.load(f)


def _run_mission_sync():
    """Connect, run the golden mission, disconnect. Returns metrics dict."""
    try:
        from UserControl import UserControl
    except ImportError as e:
        pytest.skip(f"UserControl not importable — simulator SDK missing: {e}")

    try:
        from mission_runner import run_mission
    except ImportError as e:
        pytest.skip(f"mission_runner not importable: {e}")

    controller = UserControl()
    try:
        controller.connect()
    except Exception as e:
        pytest.skip(f"Simulator not reachable: {e}")

    try:
        metrics, _ = asyncio.run(run_mission(MISSION_PATH, controller))
    finally:
        controller.close()

    return metrics


@pytest.mark.integration
def test_golden_first_flight_succeeds():
    """Golden mission must complete without collision or failure."""
    metrics = _run_mission_sync()

    assert metrics["success"] is True, (
        f"Golden mission failed. failure_reason='{metrics.get('failure_reason')}'"
    )
    assert metrics["collisions"] == 0, (
        f"Unexpected collision in golden mission."
    )
    assert metrics["failure_reason"] is None, (
        f"failure_reason should be null on success, got: '{metrics['failure_reason']}'"
    )


@pytest.mark.integration
def test_golden_first_flight_completion_time_in_band():
    """completion_time_s must stay within hard floor/ceiling and within 50% of baseline."""
    metrics = _run_mission_sync()
    t = metrics["completion_time_s"]

    assert t > COMPLETION_TIME_FLOOR_S, (
        f"completion_time_s={t:.2f}s is suspiciously fast (floor={COMPLETION_TIME_FLOOR_S}s) — "
        "mission may have short-circuited."
    )
    assert t < COMPLETION_TIME_CEILING_S, (
        f"completion_time_s={t:.2f}s exceeded ceiling of {COMPLETION_TIME_CEILING_S}s — "
        "possible hang or very slow run."
    )

    baseline = _load_baseline()
    baseline_t = float(baseline["completion_time_s"])
    max_deviation_pct = baseline["tolerance"]["completion_time_s_max_deviation_pct"]
    allowed_delta = baseline_t * (max_deviation_pct / 100.0)

    assert abs(t - baseline_t) <= allowed_delta, (
        f"completion_time_s={t:.2f}s deviates more than {max_deviation_pct}% from "
        f"baseline {baseline_t:.2f}s (allowed delta ±{allowed_delta:.2f}s). "
        "Possible performance regression — update baseline if change is intentional."
    )


@pytest.mark.integration
def test_golden_first_flight_front_range_positive():
    """If front range readings were collected, they must be positive."""
    metrics = _run_mission_sync()
    min_fr = metrics.get("min_front_range_cm")

    if min_fr is not None:
        assert min_fr > 0, (
            f"min_front_range_cm={min_fr} is not positive — sensor may be misbehaving."
        )
