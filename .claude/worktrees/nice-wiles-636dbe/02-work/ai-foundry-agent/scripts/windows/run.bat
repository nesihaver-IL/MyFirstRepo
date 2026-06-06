@echo off
REM Start the Knowledge Hub Agent API Server

echo ============================================
echo Starting Knowledge Hub Agent API
echo ============================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found. Run setup-windows.bat first.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found. Please create it from .env.example
    pause
    exit /b 1
)

echo API will be available at:
echo   - Main: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo   - Health: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
