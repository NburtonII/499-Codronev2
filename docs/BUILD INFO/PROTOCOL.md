# Project Communication Protocol


## Out of bounds Behavior

Each map uses physical walls to enforce horizontal bounds. The drone either avoids hitting these walls or if they do collide it initiates an emergency landing. 

For the vertical bounds the drone initiates an emergency landing once the drone reaches a z coordinate of -100.

The emergency landing function makes the drone slowly descend until it reaches the ground level. 
### Command Messages: 
{
  timeStamp:"Time", 
  Command: "CommandText", 
  Duration: "Duration in seconds"
}

### Telemetry Reply Message:
{
  timeStamp:"Time",
  X_m : "North/South Pos",
  Y_m : "West/East", 
  Z_m : "Up/Down", 
  Roll_deg : "Rotation around the x axis",
  Pitch_deg : "Rotation around the y axis", 
  Yaw_deg : "Rotation around the z axis", 
}

---

## Week 12 – Collision and Out-of-Bounds Event Specification (R4)

### Collision Event Schema

When the simulator detects a physical impact, `UserControl._on_collision()` fires and writes a `Collision` row to `runs/RunEvents/Run_{N}_Events.csv`.

The raw collision payload from the simulator has this structure:

```json
{
  "time_stamp": 53343000000,
  "object_name": "StaticMeshActor_5",
  "segmentation_id": 83,
  "position":     { "x": 148.85, "y": -1.25, "z": -3.01 },
  "impact_point": { "x": 149.31, "y": -0.01, "z": -3.19 },
  "normal":       { "x": -1.0,  "y": 3.37e-08, "z": 0.0 },
  "penetration_depth": 0.0
}
```

| Field | Type | Description |
|---|---|---|
| `time_stamp` | int | Simulator timestamp in nanoseconds |
| `object_name` | string | Unreal actor name of the struck object |
| `segmentation_id` | int | Segmentation mask ID of the struck object |
| `position` | {x,y,z} | Drone position at moment of impact (metres) |
| `impact_point` | {x,y,z} | World position of the contact point (metres) |
| `normal` | {x,y,z} | Surface normal at the contact point (unit vector) |
| `penetration_depth` | float | Overlap depth in metres (0 = surface contact) |

**Event CSV row format:**
```
<timestamp>,Collision,"Collision Info: <raw dict>"
```

---

### Out-of-Bounds Event Schema

Out-of-bounds (OOB) is detected by `UserControl` in two ways:

| Detection type | Trigger | Code path |
|---|---|---|
| Altitude violation | `z < -100` or `z > 0.5` | `statePoll` loop → `_out_of_bounds(reason="altitude")` |
| Horizontal violation | Physical wall collision | Handled as a standard `Collision` event |

When `_out_of_bounds()` fires it:
1. Sets `self.out_of_bounds = True`
2. Sets `self.emergency_landing = True`
3. Writes an `Out_of_Bounds` event row to the events CSV
4. Schedules `_emergency_land()` on `Lidar_loop`

**Event CSV row format:**
```
<timestamp>,Out_of_Bounds,"Out of bounds detected (reason=altitude). Emergency landing initiated."
```

**Altitude bounds (hardcoded in `UserControl.__init__`):**
```
Kill_z_up   = -100   (triggers OOB when z < -100)
kill_z_down =  0.5   (triggers OOB when z > 0.5)
```

---

### Failure Reason Code Table

`mission_runner.run_mission()` sets `failure_reason` in `metrics.json` using these structured codes:

| Code | Trigger condition | Set by |
|---|---|---|
| `"collision"` | `controller.collision is True` | `mission_runner` collision check |
| `"out_of_bounds"` | `controller.out_of_bounds is True` | `mission_runner` OOB check (W12) |
| `"timeout"` | Not yet implemented — reserved for future use | — |
| `null` | Mission completed successfully | `mission_runner` default |
| raw exception string | Unhandled exception during step execution | `mission_runner` except block |

Raw exception strings are **non-standard**. Any new failure path should map to one of the structured codes above before surfacing in metrics.

---

### Week 12 Gap Notes (R4)

- Horizontal OOB is currently enforced by physical map walls, which produce a `Collision` event — there is no separate horizontal-boundary event at the protocol level. A future enhancement could add named boundary actors so `object_name` can distinguish wall collisions from obstacle collisions.
- `_out_of_bounds()` was a non-functional stub prior to Week 12. It is now implemented and wired into the altitude check in `statePoll`.
- The `out_of_bounds` flag is checked in `mission_runner` immediately after the `collision` flag, so both failure paths produce a non-null `failure_reason` in `metrics.json`.

