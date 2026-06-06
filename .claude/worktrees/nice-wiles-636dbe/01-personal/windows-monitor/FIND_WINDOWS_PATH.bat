@echo off
REM Helper script to locate your MyFirstRepo folder on Windows
echo ============================================
echo   Finding MyFirstRepo on Windows
echo ============================================
echo.

REM Method 1: Check current directory
echo Current Directory:
cd
echo.

REM Method 2: Search for the repository in common locations
echo Searching for MyFirstRepo folder...
echo.

if exist "%USERPROFILE%\MyFirstRepo" (
    echo [FOUND] %USERPROFILE%\MyFirstRepo
    echo.
    dir /b "%USERPROFILE%\MyFirstRepo\disk_analyzer.py" >nul 2>&1
    if errorlevel 1 (
        echo   - disk_analyzer.py: NOT FOUND
    ) else (
        echo   - disk_analyzer.py: FOUND
        echo   - Full path: %USERPROFILE%\MyFirstRepo\disk_analyzer.py
    )
    echo.
)

if exist "%USERPROFILE%\Documents\MyFirstRepo" (
    echo [FOUND] %USERPROFILE%\Documents\MyFirstRepo
    echo.
    dir /b "%USERPROFILE%\Documents\MyFirstRepo\disk_analyzer.py" >nul 2>&1
    if errorlevel 1 (
        echo   - disk_analyzer.py: NOT FOUND
    ) else (
        echo   - disk_analyzer.py: FOUND
        echo   - Full path: %USERPROFILE%\Documents\MyFirstRepo\disk_analyzer.py
    )
    echo.
)

if exist "%USERPROFILE%\Desktop\MyFirstRepo" (
    echo [FOUND] %USERPROFILE%\Desktop\MyFirstRepo
    echo.
    dir /b "%USERPROFILE%\Desktop\MyFirstRepo\disk_analyzer.py" >nul 2>&1
    if errorlevel 1 (
        echo   - disk_analyzer.py: NOT FOUND
    ) else (
        echo   - disk_analyzer.py: FOUND
        echo   - Full path: %USERPROFILE%\Desktop\MyFirstRepo\disk_analyzer.py
    )
    echo.
)

if exist "C:\Projects\MyFirstRepo" (
    echo [FOUND] C:\Projects\MyFirstRepo
    echo.
    dir /b "C:\Projects\MyFirstRepo\disk_analyzer.py" >nul 2>&1
    if errorlevel 1 (
        echo   - disk_analyzer.py: NOT FOUND
    ) else (
        echo   - disk_analyzer.py: FOUND
        echo   - Full path: C:\Projects\MyFirstRepo\disk_analyzer.py
    )
    echo.
)

if exist "C:\Users\%USERNAME%\MyFirstRepo" (
    echo [FOUND] C:\Users\%USERNAME%\MyFirstRepo
    echo.
    dir /b "C:\Users\%USERNAME%\MyFirstRepo\disk_analyzer.py" >nul 2>&1
    if errorlevel 1 (
        echo   - disk_analyzer.py: NOT FOUND
    ) else (
        echo   - disk_analyzer.py: FOUND
        echo   - Full path: C:\Users\%USERNAME%\MyFirstRepo\disk_analyzer.py
    )
    echo.
)

echo ============================================
echo   Alternative: Use File Explorer Search
echo ============================================
echo.
echo If the folder wasn't found above, try:
echo 1. Open File Explorer (Windows + E)
echo 2. Search for: disk_analyzer.py
echo 3. Right-click the file and select "Open file location"
echo 4. This will show you the exact Windows path
echo.

echo ============================================
echo   Or use Git to find the path
echo ============================================
echo.
echo If you have Git Bash or Git installed:
echo 1. Open Git Bash or Command Prompt
echo 2. Run: git config --global --get-regexp path
echo 3. Or navigate to your repository and run: pwd
echo.

pause
