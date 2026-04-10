# Week 9 Sprint Plan

## Introduction

This Document outlines the sprint plan for week 9. Week 9 is about continuing to work on the Beta Build-up and running.
### End of week Deliverables:

1. Docs/Sprint/W09/*
2. DOCS/presentations/W09



## Team Roles and Responsibilities

* Sprint Lead: Muna
* Build: Ali
* World: Success
* API: Sopuru
* SDK: Nyles

### Sprint Lead Tasks

##### Task 1 - Create Sprint tasks

Finished Criteria: Document the tasks of each team member with appropriate, measurable evidence and finished criteria.
Evidence: docs/Sprints/WO8/SPRINT_PLAN.md

##### Task 2: Implementation of testing technologies

Finished Criteria: Python and Unreal testing modules are at least implemented and added to the project. And some attempt to set up some basic automatic testing is made.
Evidence:

1. Python and Unreal test modules/libraries are a part of the project.

2. docs/BUILD INFO/TEST_PLAN.md

### Build Tasks

##### Task 1 - Ensure the build/deploy works the same as the editor.

Finished Criteria: The build’s behavior is consistent and representative of how it behaves in the editor.
Evidence: tests/TestsDocs/Buid_v_Editor.md

##### Task 2 - Document graphics settings that must be fixed for consistency

Finished Criteria: Build has at least partial coverage of graphical issues and potential causes/fixes.
Evidence:  tests/TestsDocs/GRAPHICS_SETTINGS.md

##### Task 3 - performance on lower-powered machines is documented and optimized.

Finished Criteria: Build can run at least 10% to 20% better on lower-powered laptops.
Evidence: tests/TestDocs/Graphics_settings.md

### World Tasks

##### Task 1: Add three distinct color zones.

Finished Criteria: There are three color zones in each scene that are labeled.
Evidence: The color zones are present, and the lighting does not interfere with the color detection of the drone.

##### Task 2: Camera Fixed

Finished Criteria: The camera on the drone is fixed so that it has collisions and is able to get closer to the drone while still having a max distance that it attempts to keep.
Evidence: When the build or editor is run, the camera does not clip through meshes and keeps a consistent space otherwise.

### API Tasks

##### Story 1: Subscribe the drone to the proximity and color sensors

Finished criteria: The simulated drone has sensors that detect proximity and color sensors, and it has associated behaviors to respond to its detection.
Evidence: The drone can respond to commands to head toward a color landing pad and to avoid collision with an object.

##### Story 2: Drone accepts batch commands.

finished Criteria: Drone has a script that accepts and processes a batch of commands written and follows those instructions until an error is raised.
Evidence: sdk/client/batchCommands.py

### SDK Tasks

##### Story 1: Drone can accept a land-on Color command

Finished Criteria: Drone can take its color detection and land on the user-identified color specification.
Evidence: UserControl.py has implemented LandOnColor() Command.

##### Story 2: Write the Land-on-Color lab and ensure it logs color columns

Finished Criteria: Lab runs with no issues and logs behavior
Evidence: test/land_on_Color.py
