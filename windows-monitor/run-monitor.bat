@echo off
REM Windows System Monitor - Quick Start Launcher
REM Run this file to launch the system monitor with one click

echo ========================================
echo    Windows System Monitor
echo ========================================
echo.
echo Choose your monitoring option:
echo.
echo [1] PowerShell Monitor (Quick Snapshot)
echo [2] Python Monitor (Real-time Live Updates)
echo [3] Exit
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto powershell
if "%choice%"=="2" goto python
if "%choice%"=="3" goto end

:powershell
echo.
echo Starting PowerShell monitor...
echo.
powershell.exe -ExecutionPolicy Bypass -File "Get-WindowsSystemMonitor.ps1" -OpenBrowser
goto end

:python
echo.
echo Starting Python live monitor...
echo.
echo Make sure you have Python installed and psutil package:
echo   pip install psutil
echo.
python system_monitor.py --live
goto end

:end
echo.
echo Thank you for using Windows System Monitor!
pause
