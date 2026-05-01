# Golden Test Specification

**Version:** 1.0
**Week:** 11
**Owner:** R5 – Python SDK, QA & Documentation Engineer

---

## Purpose

The golden test runs the `first_flight` mission against a live simulator and asserts that key metrics stay within documented tolerance bands. It acts as a regression gate — if a code or simulator change degrades performance or breaks correctness, the golden test fails before it reaches main.

---

## Golden Mission

**File:** `missions/first_flight.json`

Chosen because it is the simplest complete mission (Takeoff → Forward 2s → State_Polling 1s → Land) and has the most stable expected behavior. It isolates basic flight correctness from map-specific or obstacle-specific variables.

---

## Test File

`tests/test_golden_mission.py`

Three test cases, all marked `@pytest.mark.integration`:

| Test | What it checks |
|------|----------------|
| `test_golden_first_flight_succeeds` | `success=True`, `collisions=0`, `failure_reason=None` |
| `test_golden_first_flight_completion_time_in_band` | `completion_time_s` within hard floor/ceiling and within 50% of baseline |
| `test_golden_first_flight_front_range_positive` | `min_front_range_cm > 0` if readings were collected |

---

## Tolerance Bands

### Hard bands (always enforced)

| Field | Floor | Ceiling | Rationale |
|-------|-------|---------|-----------|
| `completion_time_s` | 0.5 s | 60 s | Below 0.5s = mission short-circuited; above 60s = hang |
| `collisions` | — | 0 | Any collision in first_flight is a regression |
| `success` | — | `true` | Must always pass |

### Baseline-relative band

`completion_time_s` must not deviate more than **±50%** from the baseline value stored in `tests/golden/first_flight_baseline.json`.

Example: baseline = 10.0 s → allowed range = 5.0 s to 15.0 s.

The 50% band is intentionally wide to avoid false failures from normal simulator variance while still catching serious regressions (hangs, missing steps, broken reset).

---

## Baseline File

`tests/golden/first_flight_baseline.json`

```json
{
  "mission_id": "first_flight",
  "completion_time_s": 10.0,
  "tolerance": {
    "completion_time_s_max_deviation_pct": 50,
    "completion_time_s_hard_ceiling_s": 60
  }
}
```

### Updating the baseline

Run the mission several times to get a stable average, then update `completion_time_s` to that average. Commit the updated baseline with the PR and note the reason (new hardware, simulator version bump, etc.).

---

## Running the Tests

```bash
# Skip integration tests (no simulator needed):
pytest tests/ -m "not integration"

# Run golden test only (requires live simulator):
pytest tests/test_golden_mission.py -m integration -v

# Run everything including integration:
pytest tests/ -v
```

---

## Skip Behavior

The test automatically skips (not fails) if:
- `UserControl` cannot be imported (SDK not installed)
- The simulator is not reachable at connect time

This means the golden test will never block the offline unit test suite.
