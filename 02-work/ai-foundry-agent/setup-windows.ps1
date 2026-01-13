# Windows Setup Script for AI Foundry Knowledge Hub Agent (PowerShell)
# Run this script to set up the local development environment

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "AI Foundry Knowledge Hub Agent Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Azure CLI is installed
try {
    $azVersion = az --version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Azure CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Azure CLI is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install from https://learn.microsoft.com/cli/azure/install-azure-cli-windows" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists, skipping creation" -ForegroundColor Gray
} else {
    python -m venv venv
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip | Out-Null

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# Create .env file if it doesn't exist
Write-Host ""
if (Test-Path ".env") {
    Write-Host "[OK] .env file already exists" -ForegroundColor Green
} else {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "[IMPORTANT] Please edit .env file with your Azure configuration" -ForegroundColor Yellow
}

# Create docs directory if it doesn't exist
if (-not (Test-Path "docs")) {
    New-Item -ItemType Directory -Path "docs" | Out-Null
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your Azure configuration"
Write-Host "2. Run: .\deploy-infrastructure.ps1 (to deploy Azure resources)"
Write-Host "3. Run: .\run.ps1 (to start the API server)"
Write-Host ""
Write-Host "For detailed instructions, see: WINDOWS-EXECUTION-PLAN.md" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
