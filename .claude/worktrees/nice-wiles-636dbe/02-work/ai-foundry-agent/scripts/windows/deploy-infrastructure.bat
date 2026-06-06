@echo off
REM Azure Infrastructure Deployment Script for Windows

echo ============================================
echo Azure Infrastructure Deployment
echo ============================================
echo.

REM Configuration
set RESOURCE_GROUP=knowledge-hub-rg
set LOCATION=eastus
set ENVIRONMENT=dev

echo Resource Group: %RESOURCE_GROUP%
echo Location: %LOCATION%
echo Environment: %ENVIRONMENT%
echo.

REM Check if Azure CLI is logged in
echo Checking Azure login status...
az account show >nul 2>&1
if errorlevel 1 (
    echo Please login to Azure...
    az login
    if errorlevel 1 (
        echo [ERROR] Azure login failed
        pause
        exit /b 1
    )
)

echo [OK] Azure CLI is authenticated

REM Create resource group
echo.
echo Creating resource group...
az group create ^
  --name %RESOURCE_GROUP% ^
  --location %LOCATION% ^
  --output table

if errorlevel 1 (
    echo [ERROR] Failed to create resource group
    pause
    exit /b 1
)

REM Deploy infrastructure
echo.
echo Deploying infrastructure (this may take 10-15 minutes)...
cd infrastructure

az deployment group create ^
  --resource-group %RESOURCE_GROUP% ^
  --template-file main.bicep ^
  --parameters parameters.json ^
  --parameters environment=%ENVIRONMENT% ^
  --output table

if errorlevel 1 (
    echo [ERROR] Deployment failed
    cd ..
    pause
    exit /b 1
)

REM Get deployment outputs
echo.
echo Getting deployment outputs...
az deployment group show ^
  --resource-group %RESOURCE_GROUP% ^
  --name main ^
  --query properties.outputs ^
  --output json > deployment-outputs.json

cd ..

echo.
echo ============================================
echo Deployment Complete!
echo ============================================
echo.
echo Deployment outputs saved to: infrastructure\deployment-outputs.json
echo.
echo Next steps:
echo 1. Update .env file with values from deployment-outputs.json
echo 2. Run: initialize-agent.bat (to create agent and vector store)
echo 3. Run: upload-docs.bat (to upload documentation)
echo 4. Run: run.bat (to start the API server)
echo.
pause
