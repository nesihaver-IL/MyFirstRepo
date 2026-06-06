@echo off
REM Sync Commands Script for Windows
REM Automatically syncs slash commands from the repository

setlocal enabledelayedexpansion

echo.
echo ================================================
echo   Slash Commands Sync Tool
echo ================================================
echo.

cd /d "%~dp0..\.."

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

REM Get current branch
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
echo Current branch: %CURRENT_BRANCH%
echo.

REM Fetch updates
echo Checking for updates...
git fetch origin

REM Check for changes in command directories
git diff origin/%CURRENT_BRANCH% --name-only > temp_changes.txt
findstr /C:".claude\skills" /C:".cursor\commands" temp_changes.txt > command_changes.txt 2>nul

if %errorlevel% equ 0 (
    echo.
    echo Updates found! Pulling changes...
    git pull origin %CURRENT_BRANCH%

    echo.
    echo Updated files:
    type command_changes.txt

    echo.
    echo [SUCCESS] Commands synced successfully!
    echo [INFO] Restart your editor to load new commands
) else (
    echo.
    echo [OK] Commands are already up to date!
)

REM Clean up temp files
if exist temp_changes.txt del temp_changes.txt
if exist command_changes.txt del command_changes.txt

REM Count available commands
set SKILL_COUNT=0
set CURSOR_COUNT=0

for /r .claude\skills %%f in (SKILL.md) do (
    set /a SKILL_COUNT+=1
)

for /r .cursor\commands %%f in (*.md) do (
    set /a CURSOR_COUNT+=1
)

echo.
echo ================================================
echo Available Commands:
echo   - Claude Code Skills: %SKILL_COUNT%
echo   - Cursor Commands: %CURSOR_COUNT%
echo ================================================
echo.
echo Usage:
echo   - Natural language: "explore the codebase"
echo   - Direct (Cursor): /create-issue
echo   - View all: type .claude\COMMAND_REGISTRY.md
echo.

pause
