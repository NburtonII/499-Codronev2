# First Flight Test

This test was run through the 04_run_mission_from_json.py script. That script can be set to run multiple JSON defined missions. The results are as follows. 

```
Mission Description: Beginner flight: take off, move forward, stabilize, and land.

Command Log: 
  - Command: Takeoff, Duration: 0

  - Command: Forward, Duration: 2

  - Command: State_Polling, Duration: 1

  - Command: Land, Duration: 0

--- Mission Complete ---
  Success          : True
  Completion time  : 31.459 s
  Collisions       : 0

  metrics.json written to: runs/Run_28_metrics.json
```


> Notes
The Run didn't capture that in the editor the performance of the simulation suffered. This will have to be solved in the future. 