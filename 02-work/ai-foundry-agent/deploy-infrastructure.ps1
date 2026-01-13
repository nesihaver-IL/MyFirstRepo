# Azure Infrastructure Deployment Script for Windows (PowerShell)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Azure Infrastructure Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$RESOURCE_GROUP = "knowledge-hub-rg"
$LOCATION = "eastus"
$ENVIRONMENT = "dev"

Write-Host "Resource Group: $RESOURCE_GROUP" -ForegroundColor Yellow
Write-Host "Location: $LOCATION" -ForegroundColor Yellow
Write-Host "Environment: $ENVIRONMENT" -ForegroundColor Yellow
Write-Host ""

# Check if Azure CLI is logged in
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
try {
    az account show 2>&1 | Out-Null
    Write-Host "[OK] Azure CLI is authenticated" -ForegroundColor Green
} catch {
    Write-Host "Please login to Azure..." -ForegroundColor Yellow
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Azure login failed" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Create resource group
Write-Host ""
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create `
  --name $RESOURCE_GROUP `
  --location $LOCATION `
  --output table

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to create resource group" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Deploy infrastructure
Write-Host ""
Write-Host "Deploying infrastructure (this may take 10-15 minutes)..." -ForegroundColor Yellow
Push-Location infrastructure

az deployment group create `
  --resource-group $RESOURCE_GROUP `
  --template-file main.bicep `
  --parameters parameters.json `
  --parameters environment=$ENVIRONMENT `
  --output table

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Deployment failed" -ForegroundColor Red
    Pop-Location
    Read-Host "Press Enter to exit"
    exit 1
}

# Get deployment outputs
Write-Host ""
Write-Host "Getting deployment outputs..." -ForegroundColor Yellow
az deployment group show `
  --resource-group $RESOURCE_GROUP `
  --name main `
  --query properties.outputs `
  --output json | Out-File -FilePath "deployment-outputs.json"

Pop-Location

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployment outputs saved to: infrastructure\deployment-outputs.json" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update .env file with values from deployment-outputs.json"
Write-Host "2. Run: .\initialize-agent.ps1 (to create agent and vector store)"
Write-Host "3. Run: .\upload-docs.ps1 (to upload documentation)"
Write-Host "4. Run: .\run.ps1 (to start the API server)"
Write-Host ""
Read-Host "Press Enter to exit"
