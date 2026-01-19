# PowerShell script to sync MyFirstRepo with GitHub
# Location: C:\Users\Nhaver\MyFirstRepo

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Syncing MyFirstRepo with GitHub" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Target Location: C:\Users\Nhaver\MyFirstRepo" -ForegroundColor Yellow
Write-Host ""

# Check if repository exists
if (-not (Test-Path "C:\Users\Nhaver\MyFirstRepo\.git")) {
    Write-Host "ERROR: Git repository not found at C:\Users\Nhaver\MyFirstRepo" -ForegroundColor Red
    Write-Host "Please verify the path and try again." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Navigate to repository
Set-Location "C:\Users\Nhaver\MyFirstRepo"

Write-Host "Current directory: $(Get-Location)" -ForegroundColor White
Write-Host ""

# Step 1: Check current branch
Write-Host "Step 1: Checking current branch..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
Write-Host "  Current branch: $currentBranch" -ForegroundColor Green
Write-Host ""

# Step 2: Check status
Write-Host "Step 2: Checking current status..." -ForegroundColor Yellow
$status = git status --short
if ($status) {
    Write-Host "  Uncommitted changes detected:" -ForegroundColor Yellow
    Write-Host $status -ForegroundColor White
} else {
    Write-Host "  ✓ Working tree is clean" -ForegroundColor Green
}
Write-Host ""

# Step 3: Fetch from GitHub
Write-Host "Step 3: Fetching latest changes from GitHub..." -ForegroundColor Yellow
try {
    git fetch --all 2>&1 | Out-String | Write-Host
    Write-Host "  ✓ Fetch successful" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Failed to fetch from GitHub" -ForegroundColor Red
    Write-Host "  Check your internet connection and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Step 4: Pull changes
Write-Host "Step 4: Pulling changes for branch: $currentBranch..." -ForegroundColor Yellow
$pullOutput = git pull 2>&1
Write-Host $pullOutput -ForegroundColor White

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Pull successful" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Failed to pull changes" -ForegroundColor Red
    Write-Host "  You may have local changes that conflict with remote." -ForegroundColor Red
    Write-Host "  Review the error above and resolve conflicts if needed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Summary
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Sync Complete!" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your local repository is now up to date with GitHub." -ForegroundColor Green
Write-Host ""

Write-Host "Latest commits:" -ForegroundColor Yellow
git log -3 --oneline --decorate | Write-Host -ForegroundColor White
Write-Host ""

Write-Host "Total tracked files:" -ForegroundColor Yellow
$fileCount = (git ls-files | Measure-Object).Count
Write-Host "  $fileCount files" -ForegroundColor White
Write-Host ""

# Show key files
Write-Host "Key files in repository:" -ForegroundColor Yellow
if (Test-Path "disk_analyzer.py") {
    Write-Host "  ✓ disk_analyzer.py" -ForegroundColor Green
}
if (Test-Path "FIND_WINDOWS_PATH.bat") {
    Write-Host "  ✓ FIND_WINDOWS_PATH.bat" -ForegroundColor Green
}
if (Test-Path "Find-WindowsPath.ps1") {
    Write-Host "  ✓ Find-WindowsPath.ps1" -ForegroundColor Green
}
if (Test-Path "WINDOWS_LOCATION_GUIDE.md") {
    Write-Host "  ✓ WINDOWS_LOCATION_GUIDE.md" -ForegroundColor Green
}
Write-Host ""

Write-Host "============================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
