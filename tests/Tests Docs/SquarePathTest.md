# Square Path

This test tests the drone and its movements commands. 

### Results
```
Mission Description: Fly a square path: takeoff, four forward legs with right turns, land.

Command Log: 
  - Command: Takeoff, Duration: 0

  - Command: Forward, Duration: 2

  - Command: Yaw_Right, Duration: 2

  - Command: Forward, Duration: 2

  - Command: Yaw_Right, Duration: 2

  - Command: Forward, Duration: 2

  - Command: Yaw_Right, Duration: 2

  - Command: Forward, Duration: 2

  - Command: Yaw_Right, Duration: 2

  - Command: Land, Duration: 0

--- Mission Complete ---
  Success          : True
  Completion time  : 71.985 s
  Collisions       : 0
```

> Notes
The test didn't record collisions this will have to be solved. The drone also appears to get caught on a stray hitbox that does't match the visual models. 