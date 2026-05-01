# Performance Notes

**Version:** 1.0
**Week:** 11
**Owner:** R5 – Python SDK, QA & Documentation Engineer

---

## Purpose

Documents observed mission performance baselines and defines what constitutes a regression. Used to inform tolerance bands in the golden test and to track changes across weeks.

---

## Measurement Method

All timings are Python-side wall-clock (`completion_time_s` from `metrics.json`). This includes:
- Command execution time inside `commandParse()`
- Time waiting for the simulator to respond to each step
- Front range sensor polling after each step (0.5 s timeout)

It does **not** include `UserControl.connect()` or `controller.close()`.

---

## first_flight.json Baseline

Mission steps: Takeoff → Forward 2s → State_Polling 1s → Land

| Metric | Expected | Notes |
|--------|----------|-------|
| `completion_time_s` | ~10 s | Simulator-dependent; update after first clean run |
| `collisions` | 0 | Open arena, no obstacles |
| `success` | true | |
| `min_front_range_cm` | > 0 | Sensor reading after Forward step |

*Update the table above after running the mission and recording actual values.*

---

## square_path.json Baseline

Mission steps: Takeoff → (Forward 2s + Yaw_Right 2s) × 4 → Land

| Metric | Expected | Notes |
|--------|----------|-------|
| `completion_time_s` | ~25–35 s | 4 legs × ~4s + overhead |
| `collisions` | 0 | |
| `success` | true | |

*Update after running.*

---

## Batch Run Performance (50 trials)

Target: 50 × `first_flight.json` via `tools/run_batch.py --repeat 50`

| Metric | Target | Notes |
|--------|--------|-------|
| Total wall time | < 15 min | ~10 s per run × 50 + connect overhead |
| Success rate | ≥ 90% | Allows up to 5 failures from transient simulator errors |
| Manual restarts required | 0 | See `docs/BUILD INFO/BATCH_RUN_PROCESS.md` (R2) |

*Update after running the 50-trial batch.*

---

## Performance Sanity Check Checklist

Before submitting a PR that touches `mission_runner.py`, `UserControl.py`, or any sensor module:

- [ ] Run `missions/first_flight.json` and confirm `completion_time_s` is within the golden band (see `docs/GOLDEN_TEST_SPEC.md`)
- [ ] Run `pytest tests/ -m "not integration"` — all unit tests pass
- [ ] Run `pytest tests/test_golden_mission.py -m integration -v` with live simulator — golden test passes
- [ ] Check `runs/Run_N_metrics.json` for `success: true` and `failure_reason: null`

---

## Known Variance Sources

- **Simulator load time:** First run after cold start is slower by 2–5 s
- **Front range polling:** Each step adds up to 0.5 s for the sensor timeout if no reading arrives
- **Reset between runs:** `close()` + fresh `connect()` adds ~3–5 s per batch iteration
