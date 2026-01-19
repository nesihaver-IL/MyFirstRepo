@echo off
REM Script to pull latest changes from GitHub to your local repository
REM Location: C:\Users\Nhaver\MyFirstRepo

echo ============================================
echo   Syncing MyFirstRepo with GitHub
echo ============================================
echo.
echo Target Location: C:\Users\Nhaver\MyFirstRepo
echo.

REM Check if we're in the correct directory
if not exist "C:\Users\Nhaver\MyFirstRepo\.git" (
    echo ERROR: Git repository not found at C:\Users\Nhaver\MyFirstRepo
    echo Please verify the path and try again.
    echo.
    pause
    exit /b 1
)

REM Navigate to repository
cd /d "C:\Users\Nhaver\MyFirstRepo"

echo Current directory: %CD%
echo.

echo Step 1: Checking current branch...
git branch --show-current
echo.

echo Step 2: Checking current status...
git status --short
echo.

echo Step 3: Fetching latest changes from GitHub...
git fetch --all
if errorlevel 1 (
    echo ERROR: Failed to fetch from GitHub
    echo Check your internet connection and try again.
    pause
    exit /b 1
)
echo.

echo Step 4: Pulling changes for current branch...
git pull
if errorlevel 1 (
    echo ERROR: Failed to pull changes
    echo You may have local changes that conflict with remote.
    echo Review the error above and resolve conflicts if needed.
    pause
    exit /b 1
)
echo.

echo ============================================
echo   Sync Complete!
echo ============================================
echo.
echo Your local repository is now up to date with GitHub.
echo.
echo Latest commits:
git log -3 --oneline --decorate
echo.
echo Total files in repository:
git ls-files | find /c /v ""
echo.
pause
