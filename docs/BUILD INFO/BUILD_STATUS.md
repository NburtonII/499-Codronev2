# Build Info

This document is meant to give information on what machine and hardware the project was initially developed on, and to provide instructions on how to set up the project on other machines.

## Golden Machine

A golden machine is the computer that this project was required to run on. At the end of every sprint, stories were not considered complete until it could run without unexpected issues on this machine. The specifications of the machine are as follows:

- Operating System: Windows 11
- Processor: Intel(R) Xeon (R) w3-2435
- Memory - 32 GB Ram
- NVIDIA RTX A4000

## Minimum Requirements

We have to test what the minimum requirements for the project are, but we will try our best to test this in the future.

##  Set Up Instructions

The following are steps to set up the AirSim dependencies in the project.

### Unreal

These instructions assume a fresh install of everything.

1. Make sure you install the following:

    - Install Python 3.14, and
  
    - Unreal 5.7

    - Visual Studio with 2022 build tools.
      - [Download](https://visualstudio.microsoft.com/vs/older-downloads/)
      - Navigate to the link above, open the 2022 tab, and click Download.
      - Sign in to your Microsoft App.
      - Download the latest Build Tools for Visual Studio 2022
      - Proceed with VS Studio installer instructions.
        - Make sure you include "MSVC v143 - VS 2022 C++ x64/x86 build tools"

2. Navigate to your preferred Directory and clone the repo using:

```bash
    Git clone https://github.com/NburtonII/499-Codrone-Sim.git
```

3. In addition, you must clone the IAMAI's project airsim repo. You can clone it into the sdk directory of the project using:

```bash
cd <Directorylocation>/sdk
git clone https://github.com/iamaisim/ProjectAirSim.git
```

4. The simLibs from the airsim repo must be build do that by running the build.cmd. Open "x64 Nativ Tools Command Prompt for 2022". Navigate to the projects directory and open  /sdk/projectairsim. Then run build.cmd in the command line.

```bash
cd PathtoClone/sdk/ProjectAirSim
set VSCMD_ARG_TGT_ARCH=x64
set VSCMD_ARG_HOST_ARCH=x64
set UE_ROOT="C:\Program Files\Epic Games\UE_5.7"
build.cmd -Wno-dev simlib_release
```
NOTE: If you run into "The system cannot find the path specified" error, you could likely do this:
* Fix the vcvarsall.bat path in build.cmd
    - The script hardcoded the path to BuildTools flavor of VS 2022, which wasn't present. Change to the Community/Enterprise/Professional install path(whatever version of Visual Studio you have).
    - To make this edit, run ```bash notepad build.cmd ``` to edit the build.cmd and change "BuildTools" and remove "(x86)" in this line:
    - ```bash
      call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64 -vcvars_ver=%MSVC_VER%
      ```
    - to look like this(if using Community):
    - ```bash
      call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64 -vcvars_ver=%MSVC_VER%
      ```
5. Navigate to sdk\ProjectAirSim\unreal\Blocks. Run: blocks_genprojfiles_vscode.bat

  >[!Note]
  >Ensure that the UE_ROOT is set. Running this will cause errors if it isn't.

1. Once finished with the last step. Copy sdk/ProjectAirSim\unreal\Blocks\Plugins to the sim folder in the main directory. It is fine to replace the current plugins directory.

2. Launch the unrela project in the sim directory. Click build when the unreal messages pop up. The system will be ready once finished.

### Python SDK
1. Navigate to the Python client directory
  >>sdk\ProjectAirSim\client\python\projectairsim

2. Now install Python libraries using:

  ```cmd
  pip install .
  ```
