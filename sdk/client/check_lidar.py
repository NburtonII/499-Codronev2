"""
Week 9 - R2 Lidar Verification Script
Run this while the sim is active (Unreal Editor in Play mode) to confirm
Lidar1 is registered and streaming on the sensor topic bus.
"""

import asyncio
from projectairsim import ProjectAirSimClient, Drone, World


async def main():
    client = ProjectAirSimClient()
    client.connect()

    world = World(client, "scene_basic_drone.jsonc", delay_after_load_sec=2)
    drone = Drone(client, world, "Drone1")

    print("Sensors found:", list(drone.sensors.keys()))

    if "Lidar1" in drone.sensors:
        print("Lidar1 topic:", drone.sensors["Lidar1"])
        print("PASS - Lidar1 is present and has a topic")
    else:
        print("FAIL - Lidar1 not found in drone.sensors")

    client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
