<<<<<<< HEAD
# CSDP-499 CoDrone Architecture Document  

=======
# Architecture Overview
This document equips readers and the development team to understand the codebase of the project. Use it to navigate the repository and contribute as needed.

## Project Structure
```
[Project Root]/
├── docs/                          # Documentation produced during development
│   ├── ARCHITECTURE/              # Architecture documents (including this one)
│   ├── BUILD INFO/                # Build details documentation
│   ├── Presentation/              # Weekly presentations
│   ├── Sprints/                   # Weekly sprint plans
│   └── Templates/                 # Documentation templates
├── examples/                      # Test run programs for the SDK
├── missions/                      # Preprogrammed drone movement instructions
├── runs/                          # Data produced for each run
│   ├── RunCommands/               # Logs for each run command
│   ├── RunTelemetry/              # Drone telemetry data for each run
│   └── Startup.json               # Startup information for each run
├── sdk/                           # Python client and simulation interaction scripts
│   └── client/                    # Client scripts and libraries
│       ├── cpp/                   # AirSim C++ client files
│       ├── projectairsim/         # AirSim Python libraries and build files
│       ├── Python/                # Example scripts (IAMAI)
│       └── simConfig/             # Drone configuration files
├── sim/                           # Unreal Engine project files
│   ├── Build/Windows/             # Weekly build files
│   ├── Config/                   # Unreal configuration files
│   ├── Content/                  # Models and assets for the simulation
│   ├── Plugins/                  # Plugins (including Project AirSim)
│   └── CodroneSim.uproject       # Unreal project file
├── tests/                        # Test missions
├── tools/                        # (Not used yet)
├── .gitattributes               # Git configuration
├── .gitignore                   # Ignored files
├── README.md                    # Project description and credits
└── projectairsim_client.log     # Log from the previous run
```

## Core Technologies

The Codrone AirSim project uses the following components:

### Unreal Engine
Acts as the main physics and graphics engine.

### Project AirSim
Simulates the drone. Developed by IAMAI, it runs a server in Unreal and allows Python clients to connect and control the drone.

### Python
Primary scripting language used to interact with the Project AirSim API.
>>>>>>> 9c9051e78e657871a7f500e61e392a1ffe9f6c51
