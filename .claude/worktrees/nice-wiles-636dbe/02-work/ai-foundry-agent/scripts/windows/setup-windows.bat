@echo off
REM Windows Setup Script for AI Foundry Knowledge Hub Agent
REM Run this script to set up the local development environment

echo ============================================
echo AI Foundry Knowledge Hub Agent Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python is installed

REM Check if Azure CLI is installed
az --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Azure CLI is not installed or not in PATH
    echo Please install from https://learn.microsoft.com/cli/azure/install-azure-cli-windows
    pause
    exit /b 1
)

echo [OK] Azure CLI is installed

REM Create virtual environment
echo.
echo Creating Python virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping creation
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed

REM Create .env file if it doesn't exist
echo.
if exist .env (
    echo [OK] .env file already exists
) else (
    echo Creating .env file from template...
    copy .env.example .env
    echo [IMPORTANT] Please edit .env file with your Azure configuration
)

REM Create docs directory if it doesn't exist
if not exist docs mkdir docs

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file with your Azure configuration
echo 2. Run: deploy-infrastructure.bat (to deploy Azure resources)
echo 3. Run: run.bat (to start the API server)
echo.
echo For detailed instructions, see: WINDOWS-EXECUTION-PLAN.md
echo.
pause
