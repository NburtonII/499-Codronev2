# ObstacleCourse Guide

## Overview
The ObstacleCourse map is a basic drone navigation test environment designed to support obstacle avoidance, collision testing, and controlled maneuvering within a bounded play area.

The course contains guiding walls, vertical obstacles, and elevated horizontal beams intended to require directional control and precision movement from the drone.

---

## Map Features

### 1. Boundary / Guidance Walls
The course includes wall structures that serve two purposes:

- Define the playable area
- Guide the drone through the intended obstacle path

These walls create a constrained navigation route and help prevent unrestricted movement outside the designed course.

---

## Obstacles

### 2. Vertical Pillars
The course contains **two pillar obstacles** placed within the route.

Purpose:
- Test maneuvering around narrow obstacles
- Support collision detection scenarios
- Encourage path correction and controlled steering

Obstacle Count:
- Pillars: 2

---

### 3. Horizontal Beam Obstacles
The course contains **two horizontal beams** positioned to require the drone to maneuver through or under constrained space.

Purpose:
- Test precision navigation
- Simulate clearance-based obstacles
- Require altitude and positional adjustments

Obstacle Count:
- Horizontal Beams: 2

---

## Total Distinct Obstacles
The map currently includes at least three distinct obstacle types:

1. Guidance / barrier walls  
2. Vertical pillars  
3. Horizontal beam obstacles

These satisfy the obstacle variety requirement for the sprint.

---

## Playable Area Design
The obstacle course is designed as a guided route rather than an open arena.

Characteristics:
- Structured path progression
- Visual boundaries established by walls
- Obstacles positioned to encourage sequential navigation

---

## Collision Test Opportunities
The following map elements can be used for collision testing:

- Boundary / guidance walls
- Pillars
- Horizontal beams

Each obstacle type presents a unique collision scenario.

---

## Notes
- Map Name: `ObstacleCourse`
- Environment intended for obstacle avoidance and UX testing
- Layout may be extended with additional obstacles in future revisions

---

## Evidence
Verification available through:
- Unreal Editor map: `ObstacleCourse`
- In-editor obstacle layout inspection