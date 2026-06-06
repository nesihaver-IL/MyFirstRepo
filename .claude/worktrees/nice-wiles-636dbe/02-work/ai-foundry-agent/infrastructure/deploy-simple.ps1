# Simplified deployment script that works with limited Azure permissions
# This version skips automatic role assignments

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Deploying AI Foundry Agent Infrastructure" -ForegroundColor Cyan
Write-Host "(Simplified - No Role Assignments)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$RESOURCE_GROUP = "knowledge-hub-rg"
$LOCATION = "eastus"
$ENVIRONMENT = "dev"
$PROJECT_NAME = "kb-agent"

Write-Host "Resource Group: $RESOURCE_GROUP"
Write-Host "Location: $LOCATION"
Write-Host "Environment: $ENVIRONMENT"
Write-Host "Project Name: $PROJECT_NAME"
Write-Host "============================================"
Write-Host ""

# Check Azure login
Write-Host "Checking Azure login..." -ForegroundColor Yellow
try {
    $account = az account show 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Not logged in"
    }
    Write-Host "Successfully logged in to Azure" -ForegroundColor Green
} catch {
    Write-Host "Not logged in to Azure. Running az login..." -ForegroundColor Yellow
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Azure login failed" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Write-Host ""

# Create resource group
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION --output table
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to create resource group" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Deploy infrastructure
Write-Host "Deploying infrastructure (this takes 10-15 minutes)..." -ForegroundColor Yellow
Write-Host "Please be patient..." -ForegroundColor Yellow
Write-Host ""

az deployment group create `
  --resource-group $RESOURCE_GROUP `
  --template-file main-simple.bicep `
  --parameters projectName=$PROJECT_NAME `
  --parameters environment=$ENVIRONMENT `
  --output table

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Deployment failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible reasons:" -ForegroundColor Yellow
    Write-Host "- Region quota exceeded"
    Write-Host "- Service not available in region"
    Write-Host "- Insufficient permissions"
    Write-Host ""
    Write-Host "Check the error message above for details."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Deployment Successful!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Get deployment outputs
Write-Host "Retrieving deployment outputs..." -ForegroundColor Yellow
az deployment group show `
  --resource-group $RESOURCE_GROUP `
  --name main-simple `
  --query properties.outputs `
  --output json | Out-File -FilePath deployment-outputs.json

if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Could not retrieve outputs, trying alternative method..." -ForegroundColor Yellow
    az deployment group list `
      --resource-group $RESOURCE_GROUP `
      --query "[0].properties.outputs" `
      --output json | Out-File -FilePath deployment-outputs.json
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Outputs saved to: deployment-outputs.json" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Review deployment-outputs.json"
Write-Host "2. Update your .env file with the values from deployment-outputs.json"
Write-Host "3. Run initialize-agent.bat to create the AI agent"
Write-Host ""
Write-Host "IMPORTANT NOTE:" -ForegroundColor Yellow
Write-Host "This deployment used a simplified template without automatic"
Write-Host "role assignments. The agent will use API keys for authentication."
Write-Host ""
Read-Host "Press Enter to exit"
