# Metrics Specification

**Version:** 1.1
**Weeks:** 5, 6, 10
**Owner:** R5 - Python SDK, QA & Documentation Engineer

---

## Overview

After each mission run, `run_mission()` in `sdk/client/mission_runner.py` writes a
`metrics.json` file capturing the outcome of the run.

---

## File Location

Metrics files follow the existing run-numbering convention in `runs/`:

```text
runs/
  Startup.json                       <- current run counter {"RunNumber": N}
  RunCommands/Run_{N}_Commands.csv   <- command log for run N
  RunTelemetry/Run_{N}_Telemetry.csv <- telemetry log for run N
  Run_{N}_metrics.json               <- mission metrics for run N
```

`N` is read from `runs/Startup.json` at connect time and incremented by
`controller.close()`.

---

## Week 5 Minimum Schema

```json
{
  "success": true,
  "completion_time_s": 12.4,
  "collisions": 0,
  "failure_reason": null
}
```

### Field Definitions

| Field               | Type | Required | Description |
|---------------------|------|----------|-------------|
| `success`           | bool | Yes | `true` if all steps completed without a mission-ending failure |
| `completion_time_s` | float (>= 0) | Yes | Wall-clock seconds from first step start to last step end |
| `collisions`      | int (0 or 1) | Yes | `1` if a collision was detected during the mission, else `0` |
| `failure_reason` | string or null | No | Reason for mission failure; `null` on success |

---

## Week 6 Addition

```json
{
  "success": true,
  "completion_time_s": 12.4,
  "collisions": 0,
  "failure_reason": null,
  "min_front_range_cm": 180.0
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `min_front_range_cm` | float (>= 0) or null | No | Minimum front range reading captured during the mission; `null` if no reading arrived |

---

## Week 10 Failure Reason Rules

`failure_reason` now supports structured failure codes for the main mission-ending
cases the SDK can identify directly:

| Value | Meaning |
|-------|---------|
| `null` | Mission succeeded |
| `"collision"` | `controller.collision` became `True` during the mission |
| `"out_of_bounds"` | The controller reported an out-of-bounds condition |
| `"timeout"` | A command failed with a timeout-style error message |
| descriptive exception string | Any other unstructured Python or command failure |

### Detection Rules

- `mission_runner.run_mission()` checks controller state after each step.
- If `controller.collision` is set, `failure_reason` becomes `"collision"`.
- If `controller._out_of_bounds()` or `controller.out_of_bounds` reports an active
  bounds violation, `failure_reason` becomes `"out_of_bounds"`.
- If the last failed command note or raised exception contains `timeout` or
  `timed out`, `failure_reason` becomes `"timeout"`.
- Any other exception or failed-command note is written as its descriptive string.

### Current Implementation Notes

- `collisions` remains `0` or `1`, not a running count, to match the existing
  metrics contract.
- The current out-of-bounds signal is based on the SDK's safe altitude guard in
  `UserControl.statePoll()`. More general map-boundary support may be added later
  by the simulator/protocol layer.
- `failure_reason` is only non-null when `success` is `false`.

---

## Validation

`tests/test_metrics_schema_min.py` validates the minimum schema and accepts both
the Week 10 structured failure codes and descriptive strings.

`tests/test_range_columns_present.py` validates the Week 6 range field additions.

Run from the repo root:

```bash
pytest tests/test_metrics_schema_min.py
pytest tests/test_range_columns_present.py
```
