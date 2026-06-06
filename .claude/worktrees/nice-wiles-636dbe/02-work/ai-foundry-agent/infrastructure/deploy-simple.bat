@echo off
REM Simplified deployment script that works with limited Azure permissions
REM This version skips automatic role assignments

echo ============================================
echo Deploying AI Foundry Agent Infrastructure
echo (Simplified - No Role Assignments)
echo ============================================
echo.

REM Configuration
set RESOURCE_GROUP=knowledge-hub-rg
set LOCATION=eastus
set ENVIRONMENT=dev
set PROJECT_NAME=kb-agent

echo Resource Group: %RESOURCE_GROUP%
echo Location: %LOCATION%
echo Environment: %ENVIRONMENT%
echo Project Name: %PROJECT_NAME%
echo ============================================
echo.

REM Check Azure login
echo Checking Azure login...
az account show >nul 2>&1
if errorlevel 1 (
    echo Not logged in to Azure. Running az login...
    az login
    if errorlevel 1 (
        echo [ERROR] Azure login failed
        pause
        exit /b 1
    )
)

echo Successfully logged in to Azure
echo.

REM Create resource group if it doesn't exist
echo Creating resource group...
az group create --name %RESOURCE_GROUP% --location %LOCATION% --output table
if errorlevel 1 (
    echo [ERROR] Failed to create resource group
    pause
    exit /b 1
)
echo.

REM Deploy infrastructure using simplified template
echo Deploying infrastructure (this takes 10-15 minutes)...
echo Please be patient...
echo.

az deployment group create ^
  --resource-group %RESOURCE_GROUP% ^
  --template-file main-simple.bicep ^
  --parameters projectName=%PROJECT_NAME% ^
  --parameters environment=%ENVIRONMENT% ^
  --output table

if errorlevel 1 (
    echo.
    echo [ERROR] Deployment failed
    echo.
    echo Possible reasons:
    echo - Region quota exceeded
    echo - Service not available in region
    echo - Insufficient permissions
    echo.
    echo Check the error message above for details.
    pause
    exit /b 1
)

echo.
echo ============================================
echo Deployment Successful!
echo ============================================
echo.

REM Get deployment outputs
echo Retrieving deployment outputs...
az deployment group show ^
  --resource-group %RESOURCE_GROUP% ^
  --name main-simple ^
  --query properties.outputs ^
  --output json > deployment-outputs.json

if errorlevel 1 (
    echo [WARNING] Could not retrieve outputs, trying alternative method...
    az deployment group list ^
      --resource-group %RESOURCE_GROUP% ^
      --query "[0].properties.outputs" ^
      --output json > deployment-outputs.json
)

echo.
echo ============================================
echo Deployment Complete!
echo ============================================
echo.
echo Outputs saved to: deployment-outputs.json
echo.
echo NEXT STEPS:
echo 1. Review deployment-outputs.json
echo 2. Update your .env file with the values from deployment-outputs.json
echo 3. Run initialize-agent.bat to create the AI agent
echo.
echo IMPORTANT NOTE:
echo This deployment used a simplified template without automatic
echo role assignments. The agent will use API keys for authentication.
echo.
pause
