# BUILD STATUS

## Week 3 (Milestone) – <2026 6 March>

### Golden Machine (Primary Validation)

Location: Classroom PC (Golden Machine)
Machine: Dell Precision 5860 Tower
OS: Windows 11 (64-bit)
CPU: Intel(R) Xeon(R) w3-2435 (3.10 GHz)
GPU: NVIDIA RTX A4000 (16GB)
RAM: 32 GB
Unreal Engine: 5.7.3
Python: 3.9.13

### Secondary Validation Machine (Milestone Requirement)

Machine: Personal Laptop
OS: Windows 10 Home
GPU: Intel(R) UHD Graphics 620 (128 MB)
RAM: 8 GB

---

## Reproducible Run Workflow (Editor)

1. Clone:
   - git clone https://github.com/NburtonII/499-Codrone-Sim.git
   - cd 499-Codrone-Sim
2. Open Unreal project:
   - sim/CodroneSim/CodroneSim.uproject
3. In Unreal Editor:
   - Content Drawer → Content/Maps → BasicArena
   - Press Play (▶)

Expected:

- BasicArena loads
- You spawn inside arena
- Walls block movement

---

## Packaged Build Artifact (Windows Development)

Artifact link: https://github.com/NburtonII/499-Codrone-Sim/releases/tag/v0.3-week3

Run:

- Download + unzip
- Launch: CodroneSim.exe (inside packaged folder)

Expected:

- Build launches successfully

---

## Validation Results

Golden Machine: PASS
Secondary Machine: PASS

---

## Milestone Validation Note (Week 3)

Verified the packaged build on a second machine/account at least once: PASS
Evidence: https://github.com/NburtonII/499-Codrone-Sim/releases/tag/v0.3-week3

---

## Release Notes (Week 3)

- Packaged Windows development build created.
- Default map set to BasicArena.
- Verified build runs on golden machine and secondary machine.
-

## Known Issues

- None at this time

---

## Week 9 – <2026-04-16>

### Lidar Sensor – Config Verification (R2)

Lidar sensor added and enabled in the active robot config:

- **Config file:** `sdk/client/sim_config/robot_quadrotor_fastphysics.jsonc`
- **Sensor ID:** `Lidar1`
- **Type:** `lidar`
- **Enabled:** `true`
- **Channels:** 16
- **Range:** 100 m
- **FOV:** 360° horizontal, +15° to -90° vertical
- **Mounted at:** `xyz: 0 0 0.2` on the Frame link

All roles (R4, R5) must reference the sensor as `"Lidar1"` when accessing `drone.sensors["Lidar1"]["lidar"]`.

### Validation

- [ ] Lidar1 appears in drone sensor topic list on startup (editor)
- [ ] Lidar1 topic streams point cloud data during flight (editor)
- [ ] Lidar1 confirmed streaming in packaged build
