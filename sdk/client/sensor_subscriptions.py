"""
Small subscription helpers for sensor topics already exposed by the SDK.

This mirrors the lightweight async pattern used by ``range_sensor.py`` so the
rest of the SDK can subscribe to:

- proximity / LiDAR data via ``drone.sensors[<sensor_id>]["lidar"]``
- color data via ``drone.sensors["DownCamera"]["scene_camera"]`` by default
"""

import asyncio


DEFAULT_PROXIMITY_SENSOR_ID = "lidar1"
DEFAULT_COLOR_SENSOR_ID = "DownCamera"
PROXIMITY_TOPIC_KEY = "lidar"
COLOR_TOPIC_KEY = "scene_camera"


def resolve_sensor_topic(controller, sensor_id, topic_key):
    """
    Resolve a sensor topic from the active controller's drone configuration.

    Args:
        controller: Connected ``UserControl`` instance.
        sensor_id (str): Sensor ID from the active robot config.
        topic_key (str): Topic name registered under ``drone.sensors[sensor_id]``.

    Returns:
        str: Topic path ready to pass to ``client.subscribe()``.
    """
    sensors = getattr(getattr(controller, "drone", None), "sensors", {})
    if sensor_id not in sensors:
        available = ", ".join(sorted(sensors.keys())) or "<none>"
        raise KeyError(
            f"Sensor '{sensor_id}' is not available on the active drone. "
            f"Available sensors: {available}"
        )

    sensor_topics = sensors[sensor_id]
    if topic_key not in sensor_topics:
        available = ", ".join(sorted(sensor_topics.keys())) or "<none>"
        raise KeyError(
            f"Sensor '{sensor_id}' does not expose topic '{topic_key}'. "
            f"Available topics: {available}"
        )

    return sensor_topics[topic_key]


def subscribe_sensor(controller, sensor_id, topic_key, callback=None, reliability=1.0):
    """
    Subscribe to a sensor topic and keep the latest payload in a mutable dict.

    Returns:
        dict: ``{"topic": <topic_path>, "data": <latest_message_or_None>}``
    """
    topic = resolve_sensor_topic(controller, sensor_id, topic_key)
    latest = {"topic": topic, "data": None}

    def _on_sensor_message(_, data):
        latest["data"] = data
        if callback is not None:
            callback(_, data)

    controller.client.subscribe(topic, _on_sensor_message, reliability=reliability)
    return latest


async def get_sensor_data(
    controller,
    sensor_id,
    topic_key,
    timeout_s=1.0,
    callback=None,
    reliability=1.0,
):
    """
    Subscribe to a sensor topic and wait for the first payload to arrive.

    Returns:
        dict | None: Sensor message payload, or ``None`` on timeout.
    """
    latest = subscribe_sensor(
        controller,
        sensor_id=sensor_id,
        topic_key=topic_key,
        callback=callback,
        reliability=reliability,
    )
    elapsed = 0.0
    interval = 0.05

    while latest["data"] is None and elapsed < timeout_s:
        await asyncio.sleep(interval)
        elapsed += interval

    return latest["data"]


def subscribe_lidar_sensor(
    controller,
    sensor_id=DEFAULT_PROXIMITY_SENSOR_ID,
    callback=None,
    reliability=1.0,
):
    """Subscribe to an existing LiDAR sensor topic and return its latest payload."""
    return subscribe_sensor(
        controller,
        sensor_id=sensor_id,
        topic_key=PROXIMITY_TOPIC_KEY,
        callback=callback,
        reliability=reliability,
    )


async def get_lidar_data(
    controller,
    sensor_id=DEFAULT_PROXIMITY_SENSOR_ID,
    timeout_s=1.0,
    callback=None,
    reliability=1.0,
):
    """Wait for one LiDAR payload from the configured proximity sensor."""
    return await get_sensor_data(
        controller,
        sensor_id=sensor_id,
        topic_key=PROXIMITY_TOPIC_KEY,
        timeout_s=timeout_s,
        callback=callback,
        reliability=reliability,
    )


def subscribe_proximity_sensor(
    controller,
    sensor_id=DEFAULT_PROXIMITY_SENSOR_ID,
    callback=None,
    reliability=1.0,
):
    """Alias for LiDAR subscriptions used by the Week 8 proximity story."""
    return subscribe_lidar_sensor(
        controller,
        sensor_id=sensor_id,
        callback=callback,
        reliability=reliability,
    )


async def get_proximity_data(
    controller,
    sensor_id=DEFAULT_PROXIMITY_SENSOR_ID,
    timeout_s=1.0,
    callback=None,
    reliability=1.0,
):
    """Alias for one-shot LiDAR reads used by the Week 8 proximity story."""
    return await get_lidar_data(
        controller,
        sensor_id=sensor_id,
        timeout_s=timeout_s,
        callback=callback,
        reliability=reliability,
    )


def subscribe_color_sensor(
    controller,
    sensor_id=DEFAULT_COLOR_SENSOR_ID,
    topic_key=COLOR_TOPIC_KEY,
    callback=None,
    reliability=1.0,
):
    """
    Subscribe to the existing RGB camera feed used as the repo's color sensor.

    By default this uses ``DownCamera.scene_camera``. Callers can pass a
    different topic key such as ``segmentation_camera`` if their scene config
    enables it.
    """
    return subscribe_sensor(
        controller,
        sensor_id=sensor_id,
        topic_key=topic_key,
        callback=callback,
        reliability=reliability,
    )


async def get_color_data(
    controller,
    sensor_id=DEFAULT_COLOR_SENSOR_ID,
    topic_key=COLOR_TOPIC_KEY,
    timeout_s=1.0,
    callback=None,
    reliability=1.0,
):
    """Wait for one color-sensor payload from the configured camera topic."""
    return await get_sensor_data(
        controller,
        sensor_id=sensor_id,
        topic_key=topic_key,
        timeout_s=timeout_s,
        callback=callback,
        reliability=reliability,
    )
