# CoDrone Simulator - Setup Script
# Run from the repo root on any new Windows machine before opening Unreal.
# Usage: .\setup.ps1
#        .\setup.ps1 -UERoot "D:\Epic Games\UE_5.7"

param(
    [string]$UERoot = "C:\Program Files\Epic Games\UE_5.7"
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$Failed = @()

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CoDrone Simulator - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ── 1. Python 3.12 ────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[1/4] Checking Python 3.12..." -ForegroundColor Yellow
try {
    $pyVersion = & python --version 2>&1
    if ($pyVersion -match "3\.12") {
        Write-Host "      PASS: $pyVersion" -ForegroundColor Green
    } else {
        Write-Host "      FAIL: Found $pyVersion — Python 3.12 is required." -ForegroundColor Red
        Write-Host "            Download: https://www.python.org/downloads/" -ForegroundColor Red
        $Failed += "Python 3.12"
    }
} catch {
    Write-Host "      FAIL: Python not found in PATH." -ForegroundColor Red
    Write-Host "            Download: https://www.python.org/downloads/" -ForegroundColor Red
    $Failed += "Python 3.12"
}

# ── 2. Visual Studio 2022 ─────────────────────────────────────────────────────
Write-Host ""
Write-Host "[2/4] Checking Visual Studio 2022..." -ForegroundColor Yellow
$vsPaths = @(
    "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat",
    "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat",
    "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat",
    "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
)
$vsFound = $vsPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($vsFound) {
    Write-Host "      PASS: Found at $vsFound" -ForegroundColor Green
} else {
    Write-Host "      FAIL: Visual Studio 2022 with C++ build tools not found." -ForegroundColor Red
    Write-Host "            Download: https://visualstudio.microsoft.com/vs/older-downloads/" -ForegroundColor Red
    Write-Host "            Required component: MSVC v143 - VS 2022 C++ x64/x86 build tools" -ForegroundColor Red
    $Failed += "Visual Studio 2022"
}

# ── 3. Unreal Engine 5.7 ──────────────────────────────────────────────────────
Write-Host ""
Write-Host "[3/4] Checking Unreal Engine 5.7..." -ForegroundColor Yellow
$ueBinary = Join-Path $UERoot "Engine\Binaries\Win64\UnrealEditor.exe"
if (Test-Path $ueBinary) {
    Write-Host "      PASS: Found at $UERoot" -ForegroundColor Green
} else {
    Write-Host "      FAIL: Unreal Engine 5.7 not found at: $UERoot" -ForegroundColor Red
    Write-Host "            If installed elsewhere rerun with:" -ForegroundColor Red
    Write-Host "            .\setup.ps1 -UERoot 'C:\path\to\UE_5.7'" -ForegroundColor Red
    $Failed += "Unreal Engine 5.7"
}

# ── 4. Install Python SDK ─────────────────────────────────────────────────────
Write-Host ""
Write-Host "[4/4] Installing Python SDK..." -ForegroundColor Yellow
$sdkReqs = Join-Path $RepoRoot "sdk\client\projectairsim\requirements.txt"
if (Test-Path $sdkReqs) {
    try {
        pip install -r $sdkReqs
        Write-Host "      PASS: Python SDK installed." -ForegroundColor Green
    } catch {
        Write-Host "      FAIL: pip install failed. Make sure Python 3.12 is installed first." -ForegroundColor Red
        $Failed += "Python SDK"
    }
} else {
    Write-Host "      FAIL: requirements.txt not found at $sdkReqs" -ForegroundColor Red
    $Failed += "Python SDK"
}

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($Failed.Count -eq 0) {
    Write-Host "  Setup complete - all checks passed." -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "  1. Open the Unreal project:" -ForegroundColor White
    Write-Host "     $RepoRoot\sim\CodroneSim.uproject" -ForegroundColor White
    Write-Host "  2. Click 'Yes' when prompted to build missing modules." -ForegroundColor White
    Write-Host "  3. Once the editor loads, run a Python script from the repo root:" -ForegroundColor White
    Write-Host "     python examples\lab_01_first_flight.py" -ForegroundColor White
    Write-Host ""
    Write-Host "  To package a build run: .\package.ps1" -ForegroundColor White
} else {
    Write-Host "  Setup incomplete - fix the following:" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    foreach ($item in $Failed) {
        Write-Host "  - $item" -ForegroundColor Red
    }
}
Write-Host ""
