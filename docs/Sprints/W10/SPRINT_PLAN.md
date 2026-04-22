# Week 10 Sprint Plan

## Introduction

Week 10 focuses on the **ObstacleCourse** integration and batch run automation. The team must deliver a new map with obstacles, expose collision/out-of-bounds events through the protocol, and build the Python tooling to run missions in batch and summarize results in `batch_summary.csv`.

### End of Week Deliverables

1. `docs/Sprints/W10/*`
2. `docs/Presentations/W10`
3. `missions/obstacle_course_v1.json`
4. `tools/run_batch.py`
5. `runs/batch_summary.csv` (produced by at least one batch run)
6. At least one failing run documented with logs

---

## Team Roles and Responsibilities

| Role | Member |
|------|--------|
| R1 – Sprint Lead & Integrator | Ali |
| R2 – Build & Release Engineer | Success |
| R3 – 3D World & UX Engineer | Sopuru |
| R4 – Simulator API & Networking Engineer | Nyles |
| R5 – Python SDK, QA & Documentation Engineer | Muna |

---

## R1 – Sprint Lead & Integrator (Ali)

### Task 1 – Create Sprint Plan

**Finished Criteria:** Sprint plan documents each member's tasks with measurable evidence and finish criteria.  
**Evidence:** `docs/Sprints/W10/SPRINT_PLAN.md`

### Task 2 – Require Batch Run Artifacts

**Finished Criteria:** The week's PR/submission includes `batch_summary.csv` or `batch_summary.json` produced by an actual batch run (not hand-crafted). File must contain at minimum: run count, success count, failure count, success rate.  
**Evidence:** `runs/batch_summary.csv` committed alongside the PR.

### Task 3 – Require a Documented Failing Run

**Finished Criteria:** At least one failing run is captured with its log output and `metrics.json`. A written explanation (1–3 sentences) identifies the failure reason and whether it was expected.  
**Evidence:** `docs/Sprints/W10/failing_run_explanation.md` referencing the relevant `runs/Run_N_metrics.json`.

---

## R2 – Build & Release Engineer (Success)

### Task 1 – Include ObstacleCourse in Build/Deploy

**Finished Criteria:** The packaged build can load the `ObstacleCourse` map without editor access. The map appears as a selectable option at launch or via the existing map-selection mechanism.  
**Evidence:** `tests/TestsDocs/ObstacleCourse_Build_Verify.md` confirming the map loads from the build.

### Task 2 – Batch Runs Without Manual Restarts

**Finished Criteria:** Either (a) `tools/run_batch.py` can execute multiple missions end-to-end without a human restarting the sim between runs, or (b) a documented workaround is provided explaining the current limitation and the minimum manual steps required.  
**Evidence:** `docs/BUILD INFO/BATCH_RUN_PROCESS.md`

---

## R3 – 3D World & UX Engineer (Sopuru)

### Task 1 – Create ObstacleCourse Map

**Finished Criteria:** A new Unreal map named `ObstacleCourse` exists in the project with:
- At least 3 distinct obstacles (walls, pillars, or barriers) that the drone can collide with.
- Clear visual boundaries indicating the playable area (floor markings, walls, or fencing).
- Exactly 2 named drone spawn points.

**Evidence:** Map visible in the Unreal editor; spawn point names documented in `docs/Sprints/W10/ObstacleCourse_Guide.md`.

### Task 2 – Document Spawn Points and Mission Parameters

**Finished Criteria:** A guide describes each spawn point's coordinates, orientation, and recommended starting commands for `obstacle_course_v1.json`.  
**Evidence:** `docs/Sprints/W10/ObstacleCourse_Guide.md`

---

## R4 – Simulator API & Networking Engineer (Nyles)

### Task 1 – Expose Collision and Out-of-Bounds Events Consistently

**Finished Criteria:**
- Collision events fired by the Unreal sim are reliably received by `UserControl` (no silent drops).
- An out-of-bounds region is defined for `ObstacleCourse`; crossing it fires a detectable event or sets a flag in `UserControl`.

**Evidence:** `docs/BUILD INFO/PROTOCOL.md` updated with the out-of-bounds region definition and event spec; `tests/test_collision_oob_events.py` demonstrating detection.

### Task 2 – Protocol Returns Failure Reason on Command/Mission Failure

**Finished Criteria:** When a command or mission fails (collision, out-of-bounds, timeout), the protocol response or `metrics.json` includes a non-null `failure_reason` string matching the actual cause. R5's `metrics.json` implementation depends on this.  
**Evidence:** `docs/BUILD INFO/PROTOCOL.md` updated; coordinated with R5.

---

## R5 – Python SDK, QA & Documentation Engineer (Muna)

### Task 1 – Implement `failure_reason` Logic in `metrics.json`

**Finished Criteria:** `sdk/client/mission_runner.py` populates `failure_reason` with one of the structured codes defined in `docs/ARCHITECTURE/METRICS_SPEC.md` Week 10 additions: `"collision"`, `"out_of_bounds"`, `"timeout"`, or a descriptive exception string. `null` on success.  
**Evidence:** `tests/test_metrics_schema_min.py` updated/passing; `docs/ARCHITECTURE/METRICS_SPEC.md` Week 10 section added.

### Task 2 – Write `missions/obstacle_course_v1.json`

**Finished Criteria:** A valid mission JSON file that navigates the drone through `ObstacleCourse`, targeting at least 2 obstacles to test collision detection. Steps use the existing command vocabulary from `mission_runner.py`.  
**Evidence:** `missions/obstacle_course_v1.json` committed and loadable by `load_mission()` without validation errors.

### Task 3 – Write `tools/run_batch.py`

**Finished Criteria:** Script accepts a list of mission JSON paths, runs each via `run_mission()`, and writes `runs/batch_summary.csv` with columns:

| Column | Description |
|--------|-------------|
| `mission` | Mission file name |
| `success` | `true` / `false` |
| `completion_time_s` | Float |
| `collisions` | 0 or 1 |
| `failure_reason` | String or blank |

The final row (or a trailing summary line) includes total run count, success count, failure count, and success rate percentage.  
**Evidence:** `tools/run_batch.py` committed; `runs/batch_summary.csv` from an actual run attached to the PR.
