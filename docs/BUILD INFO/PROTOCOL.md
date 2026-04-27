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


