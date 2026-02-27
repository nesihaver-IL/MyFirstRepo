# Start the Knowledge Hub Agent API Server (PowerShell)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Starting Knowledge Hub Agent API" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "[ERROR] Virtual environment not found. Run setup-windows.ps1 first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "[ERROR] .env file not found. Please create it from .env.example" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "API will be available at:" -ForegroundColor Green
Write-Host "  - Main: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  - Health: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
