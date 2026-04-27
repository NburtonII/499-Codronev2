# Project Communication Protocol

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

## Sensor Topics

### Distance Sensors (FrontRange / BottomRange)

The SDK provides access to distance sensors via `range_sensor.py`:

| Sensor ID   | Topic Key         | Access Path                                    |
|-------------|-------------------|------------------------------------------------|
| FrontRange  | distance_sensor   | `drone.sensors["FrontRange"]["distance_sensor"]` |
| BottomRange | distance_sensor   | `drone.sensors["BottomRange"]["distance_sensor"]` |

**Functions:**
- `get_front_range(controller, timeout_s)` → returns distance in metres (float or None)
- `get_bottom_range(controller, timeout_s)` → returns distance in metres (float or None)

### Lidar Sensor (Lidar1)

The Lidar sensor provides point cloud data for extracting distance measurements.

| Sensor ID | Topic Key | Access Path                              |
|-----------|-----------|------------------------------------------|
| Lidar1    | lidar     | `drone.sensors["Lidar1"]["lidar"]`       |

**Topic Data Structure:**
```python
{
    "time_stamp": 1234567890000000000,  # nanoseconds since epoch
    "point_cloud": [x1, y1, z1, x2, y2, z2, ...]  # flat array of coordinates
}
```

**Distance Extraction Method:**

The point cloud is stored as a flat array of floats where each point has 3 coordinates (x, y, z):
- Forward direction: +X axis (positive X values are in front of the drone)
- Downward direction: -Z axis (negative Z values are below the drone)

To extract distances:
1. Iterate through the point cloud array in groups of 3 (x, y, z)
2. For forward distance: find minimum X value where X > 0
3. For downward distance: find minimum absolute Z value where Z < 0

**SDK Function:**
- `get_lidar_distances(controller, timeout_s)` → returns `{"forward_m": float | None, "downward_m": float | None}`

**Error Handling:**
If the Lidar1 sensor ID is not found in `drone.sensors`, the function logs a clear error message:
```
ERROR: Lidar sensor ID 'Lidar1' not found in drone.sensors
Available sensors: [list of available sensor IDs]
```
This follows the same pattern used for FrontRange and BottomRange sensors.


