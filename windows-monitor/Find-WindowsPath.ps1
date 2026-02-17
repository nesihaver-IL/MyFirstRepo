# PowerShell script to locate MyFirstRepo folder on Windows
# Usage: Right-click and select "Run with PowerShell"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Finding MyFirstRepo on Windows" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Method 1: Check current directory
Write-Host "Current Directory:" -ForegroundColor Yellow
Write-Host (Get-Location)
Write-Host ""

# Method 2: Search for disk_analyzer.py
Write-Host "Searching for disk_analyzer.py file..." -ForegroundColor Yellow
Write-Host ""

$searchPaths = @(
    "$env:USERPROFILE\MyFirstRepo",
    "$env:USERPROFILE\Documents\MyFirstRepo",
    "$env:USERPROFILE\Desktop\MyFirstRepo",
    "$env:USERPROFILE\Documents\GitHub\MyFirstRepo",
    "$env:USERPROFILE\source\repos\MyFirstRepo",
    "C:\Projects\MyFirstRepo",
    "C:\Git\MyFirstRepo"
)

$foundPaths = @()

foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        Write-Host "[FOUND] $path" -ForegroundColor Green
        $scriptPath = Join-Path $path "disk_analyzer.py"
        $htmlPath = Join-Path $path "..\disk_space_map.html"

        if (Test-Path $scriptPath) {
            Write-Host "  ✓ disk_analyzer.py: FOUND" -ForegroundColor Green
            Write-Host "    Full path: $scriptPath" -ForegroundColor White
            $foundPaths += $scriptPath
        } else {
            Write-Host "  ✗ disk_analyzer.py: NOT FOUND" -ForegroundColor Red
        }

        Write-Host ""
    }
}

# Method 3: Use Windows Search to find the file
Write-Host "Performing deep search (this may take a moment)..." -ForegroundColor Yellow

$drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Free -ne $null }

foreach ($drive in $drives) {
    $searchResults = Get-ChildItem -Path "$($drive.Name):\" -Filter "disk_analyzer.py" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 5

    if ($searchResults) {
        Write-Host ""
        Write-Host "Found on $($drive.Name): drive:" -ForegroundColor Green
        foreach ($result in $searchResults) {
            Write-Host "  📁 $($result.DirectoryName)" -ForegroundColor Cyan
            Write-Host "  📄 $($result.FullName)" -ForegroundColor White
            Write-Host ""
            $foundPaths += $result.FullName
        }
    }
}

# Summary
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   SUMMARY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

if ($foundPaths.Count -eq 0) {
    Write-Host "No files found. Try these steps:" -ForegroundColor Red
    Write-Host ""
    Write-Host "1. Open File Explorer (Windows + E)" -ForegroundColor Yellow
    Write-Host "2. In the search box, type: disk_analyzer.py" -ForegroundColor Yellow
    Write-Host "3. Wait for results to appear" -ForegroundColor Yellow
    Write-Host "4. Right-click the file > 'Open file location'" -ForegroundColor Yellow
} else {
    Write-Host "Found $($foundPaths.Count) location(s):" -ForegroundColor Green
    Write-Host ""
    foreach ($path in $foundPaths | Select-Object -Unique) {
        Write-Host "📍 $path" -ForegroundColor White

        # Check for the HTML file in parent directory
        $parentDir = Split-Path (Split-Path $path -Parent) -Parent
        $htmlFile = Join-Path $parentDir "disk_space_map.html"
        if (Test-Path $htmlFile) {
            Write-Host "   HTML visualization: $htmlFile" -ForegroundColor Cyan
        }
    }
    Write-Host ""
    Write-Host "To run the analyzer on Windows:" -ForegroundColor Yellow
    Write-Host "  python `"$($foundPaths[0])`" C:\Path\To\Analyze" -ForegroundColor White
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
