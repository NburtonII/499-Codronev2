# Build Instructions for project AirSim SDK

### Prereqs
1. Python
2. Java
3. Cmake

I installed Java from Adoptium.


## Build the plugin
### In x64 Native Tools Command Prompt for Visual Studio
1. cd to the "sdk\ProjectAirSim\"
2. Set UE-ROOT with 
>[!NOTE]
> $ set UE_ROOT=C:\Program Files\Epic Games\UE_5.7
3. Run the build CMD with
>[!NOTE]
> $ build.cmd simlibs_release
4.  Copy the plug-in to the Unreal project
>[!NOTE]
> robocopy "unreal\Blocks\Plugins\ProjectAirSim" "C:\path\to\CSDP_499_Codrone\sim\Plugins\ProjectAirSim" /E

5. Regenerate VS Project files
    - go to Visual Studios 20xx
    - open project and right click "sim\CodroneSim.Uproject"
    - select Regenerate VS project files and select "Generate Visual Studio Project Files."


The project should open in Unreal at this point. I will update this with error fixes and solutions as we run into them.
