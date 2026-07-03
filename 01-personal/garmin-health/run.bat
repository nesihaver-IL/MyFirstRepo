@echo off
REM Garmin Health Analytics Dashboard Quick-Start Script (Windows)
REM Run from project root: run.bat

setlocal enabledelayedexpansion

set ANALYTICS_DIR=%~dp0analytics
set VENV_DIR=%ANALYTICS_DIR%\.venv

echo ==========================================
echo Garmin Health Analytics Dashboard
echo ==========================================
echo.

REM Step 1: Create or verify venv
if not exist "%VENV_DIR%" (
    echo [1/4] Creating Python virtual environment...
    python -m venv "%VENV_DIR%"
) else (
    echo [1/4] Virtual environment already exists
)

REM Step 2: Activate venv and install dependencies
echo [2/4] Installing dependencies...
call "%VENV_DIR%\Scripts\activate.bat"
pip install -q --upgrade pip
pip install -q -r "%ANALYTICS_DIR%\requirements.txt"

REM Step 3: Verify .env file
if not exist "%ANALYTICS_DIR%\.env" (
    echo [3/4] Creating .env file
    (
        echo # Add your Anthropic API key here
        echo ANTHROPIC_API_KEY=sk-ant-your-key-here
    ) > "%ANALYTICS_DIR%\.env"
) else (
    echo [3/4] .env file exists
)

REM Step 4: Launch dashboard
echo [4/4] Launching Streamlit dashboard...
echo.
echo Dashboard will open at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

cd /d "%ANALYTICS_DIR%"
streamlit run app.py

pause
