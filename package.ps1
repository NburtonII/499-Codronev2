# CoDrone Simulator - Package Script
# Run from the repo root on the golden machine to produce a Windows build.
# Usage: .\package.ps1
#        .\package.ps1 -UERoot "D:\Epic Games\UE_5.7"
#        .\package.ps1 -OutputDir "C:\MyBuilds\CodroneSim"

param(
    [string]$UERoot = "C:\Program Files\Epic Games\UE_5.7",
    [string]$OutputDir = "$PSScriptRoot\sim\Windows"
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$UProjectPath = Join-Path $RepoRoot "sim\CodroneSim.uproject"
$UAT = Join-Path $UERoot "Engine\Build\BatchFiles\RunUAT.bat"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CoDrone Simulator - Package Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ── Preflight checks ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Running preflight checks..." -ForegroundColor Yellow

if (-not (Test-Path $UAT)) {
    Write-Host "FAIL: RunUAT.bat not found at: $UAT" -ForegroundColor Red
    Write-Host "      Make sure Unreal Engine 5.7 is installed and rerun with:" -ForegroundColor Red
    Write-Host "      .\package.ps1 -UERoot 'C:\path\to\UE_5.7'" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS: Unreal Engine 5.7 found." -ForegroundColor Green

if (-not (Test-Path $UProjectPath)) {
    Write-Host "FAIL: Project file not found at: $UProjectPath" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS: Project file found." -ForegroundColor Green

Write-Host "  Output directory: $OutputDir" -ForegroundColor White

# ── Package ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Starting packaging — this will take 20-40 minutes..." -ForegroundColor Yellow
Write-Host ""

$UATArgs = @(
    "BuildCookRun",
    "-project=`"$UProjectPath`"",
    "-platform=Win64",
    "-configuration=Development",
    "-build",
    "-cook",
    "-stage",
    "-package",
    "-archive",
    "-archivedirectory=`"$OutputDir`"",
    "-noP4",
    "-utf8output"
)

& $UAT $UATArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Packaging complete." -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Build output: $OutputDir" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: .pak and .ucas files exceed GitHub's 100 MB limit." -ForegroundColor Yellow
    Write-Host "      Upload the full output folder to OneDrive for distribution." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Packaging FAILED (exit code $LASTEXITCODE)." -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Check the logs at:" -ForegroundColor White
    Write-Host "  $UERoot\Engine\Programs\AutomationTool\Saved\Logs\" -ForegroundColor White
    Write-Host ""
    exit 1
}
