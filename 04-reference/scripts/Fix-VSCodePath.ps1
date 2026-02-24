# Fix-VSCodePath.ps1
# Automatically detects and adds VS Code to the user PATH on Windows
# Usage: Right-click -> "Run with PowerShell", or run from terminal:
#   powershell -ExecutionPolicy Bypass -File Fix-VSCodePath.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   VS Code PATH Fix" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Common VS Code installation paths
$candidatePaths = @(
    "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin",
    "$env:ProgramFiles\Microsoft VS Code\bin",
    "${env:ProgramFiles(x86)}\Microsoft VS Code\bin",
    "$env:USERPROFILE\AppData\Local\Programs\Microsoft VS Code\bin"
)

# Step 1: Check if 'code' is already available
Write-Host "Step 1: Checking if 'code' is already on PATH..." -ForegroundColor Yellow
$existing = Get-Command code -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "  'code' is already available at: $($existing.Source)" -ForegroundColor Green
    Write-Host ""
    code --version
    Write-Host ""
    Write-Host "No fix needed! If 'code' still doesn't open, restart your terminal." -ForegroundColor Green
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host "  'code' not found on PATH." -ForegroundColor Red
Write-Host ""

# Step 2: Find VS Code installation
Write-Host "Step 2: Searching for VS Code installation..." -ForegroundColor Yellow
$vscodeBinPath = $null

foreach ($path in $candidatePaths) {
    if (Test-Path "$path\code.cmd") {
        Write-Host "  Found VS Code at: $path" -ForegroundColor Green
        $vscodeBinPath = $path
        break
    }
}

if (-not $vscodeBinPath) {
    Write-Host "  VS Code installation not found in common locations." -ForegroundColor Red
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  1. Install VS Code from: https://code.visualstudio.com/" -ForegroundColor White
    Write-Host "     - During install, check 'Add to PATH (requires shell restart)'" -ForegroundColor White
    Write-Host "  2. Or manually find VS Code and add its 'bin' folder to PATH" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 3: Add to user PATH
Write-Host ""
Write-Host "Step 3: Adding VS Code to user PATH..." -ForegroundColor Yellow

$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($currentPath -like "*$vscodeBinPath*") {
    Write-Host "  PATH already contains VS Code directory." -ForegroundColor Green
    Write-Host "  Restart your terminal for it to take effect." -ForegroundColor Yellow
} else {
    $newPath = "$currentPath;$vscodeBinPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "  Successfully added to PATH: $vscodeBinPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "  IMPORTANT: Restart your terminal for changes to take effect." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "After restarting your terminal, verify with:" -ForegroundColor White
Write-Host "  code --version" -ForegroundColor White
Write-Host "  code ." -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
