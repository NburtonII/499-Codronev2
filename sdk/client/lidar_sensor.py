# sdk/client/lidar_sensor.py

"""
Provides get_lidar_distances() for a connected UserControl instance.
Subscribes to the Lidar point cloud topic registered in the active
robot config (sdk/client/sim_config/robot_quadrotor_fastphysics.jsonc).

Sensor ID in the robot config:
  Lidar1 - Livox Mid-70 Lidar sensor (360° horizontal, 100m range)

Public API:
  get_lidar_distances(controller, timeout_s) -> dict | None

Returns a dictionary with:
  - "forward_m": minimum forward distance in metres (None if no points in front)
  - "downward_m": minimum downward distance in metres (None if no points below)

The point cloud data contains 3D points as a flat array [x1, y1, z1, x2, y2, z2, ...].
Forward direction is +X, downward direction is -Z.
"""

import asyncio

LIDAR_SENSOR_ID = "Lidar1"
SENSOR_TOPIC_KEY = "lidar"


def _subscribe_lidar(controller):
    """
    Subscribe to the Lidar point cloud topic on the connected controller.

    Returns a list that will be populated with the latest point cloud data
    once a message arrives.

    Args:
        controller (UserControl): A connected UserControl instance.

    Returns:
        list: Mutable container; result[0] will be set to the lidar data dict.
    """
    result = []

    def _on_reading(_, data):
        if data is not None and not result:
            result.append(data)

    topic = controller.drone.sensors[LIDAR_SENSOR_ID][SENSOR_TOPIC_KEY]
    controller.client.subscribe(topic, _on_reading)
    return result


def _extract_distances(lidar_data):
    """
    Extract minimum forward and downward distances from point cloud data.

    The point cloud is stored as a flat array of floats:
    [x1, y1, z1, x2, y2, z2, ...]

    Forward direction: +X axis (positive X values)
    Downward direction: -Z axis (negative Z values)

    Args:
        lidar_data (dict): Lidar data containing "point_cloud" key with
                          flat array of coordinate values.

    Returns:
        dict: {"forward_m": float | None, "downward_m": float | None}
    """
    point_cloud = lidar_data.get("point_cloud", [])
    
    if not point_cloud:
        return {"forward_m": None, "downward_m": None}

    # Point cloud is a flat array [x1, y1, z1, x2, y2, z2, ...]
    # Process in groups of 3
    min_forward = None
    min_downward = None

    for i in range(0, len(point_cloud), 3):
        if i + 2 >= len(point_cloud):
            break
        x = point_cloud[i]
        y = point_cloud[i + 1]
        z = point_cloud[i + 2]

        # Forward: positive X values (in front of the drone)
        if x > 0:
            if min_forward is None or x < min_forward:
                min_forward = x

        # Downward: negative Z values (below the drone)
        if z < 0:
            distance = abs(z)
            if min_downward is None or distance < min_downward:
                min_downward = distance

    return {"forward_m": min_forward, "downward_m": min_downward}


async def get_lidar_distances(controller, timeout_s=1.0):
    """
    Read the Lidar sensor and return minimum forward and downward distances.

    Subscribes to the Lidar1 sensor topic, waits up to timeout_s seconds
    for the first point cloud reading, then extracts and returns the distances.

    Args:
        controller (UserControl): A connected UserControl instance.
        timeout_s  (float):       Maximum seconds to wait for a reading.

    Returns:
        dict: {"forward_m": float | None, "downward_m": float | None}
              Returns None if no reading arrives within timeout.
    """
    # Check if Lidar1 sensor exists
    if LIDAR_SENSOR_ID not in controller.drone.sensors:
        print(f"ERROR: Lidar sensor ID '{LIDAR_SENSOR_ID}' not found in drone.sensors")
        print(f"Available sensors: {list(controller.drone.sensors.keys())}")
        return None

    result = _subscribe_lidar(controller)
    elapsed = 0.0
    interval = 0.05
    while not result and elapsed < timeout_s:
        await asyncio.sleep(interval)
        elapsed += interval

    if not result:
        return None

    return _extract_distances(result[0])