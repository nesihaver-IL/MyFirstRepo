#!/bin/bash
# Simplified deployment script for Linux that works with limited Azure permissions
# This version skips automatic role assignments

set -e

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-knowledge-hub-rg}"
LOCATION="${LOCATION:-eastus}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
PROJECT_NAME="${PROJECT_NAME:-kb-agent}"

echo "============================================"
echo "Deploying AI Foundry Agent Infrastructure"
echo "(Simplified - No Role Assignments)"
echo "============================================"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "Environment: $ENVIRONMENT"
echo "Project Name: $PROJECT_NAME"
echo "============================================"
echo ""

# Check Azure login
echo "Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "Not logged in to Azure. Please run: az login"
    exit 1
fi

echo "Successfully logged in to Azure"
echo ""

# Create resource group if it doesn't exist
echo "Creating resource group..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output table

echo ""

# Deploy infrastructure using simplified template
echo "Deploying infrastructure (this takes 10-15 minutes)..."
echo "Please be patient..."
echo ""

az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file main-simple.bicep \
  --parameters projectName="$PROJECT_NAME" \
  --parameters environment="$ENVIRONMENT" \
  --output table

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Deployment failed"
    echo ""
    echo "Possible reasons:"
    echo "- Region quota exceeded"
    echo "- Service not available in region"
    echo "- Insufficient permissions"
    echo ""
    exit 1
fi

echo ""
echo "============================================"
echo "Deployment Successful!"
echo "============================================"
echo ""

# Get deployment outputs
echo "Retrieving deployment outputs..."
az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main-simple \
  --query properties.outputs \
  --output json > deployment-outputs.json

if [ $? -ne 0 ]; then
    echo "[WARNING] Could not retrieve outputs, trying alternative method..."
    az deployment group list \
      --resource-group "$RESOURCE_GROUP" \
      --query "[0].properties.outputs" \
      --output json > deployment-outputs.json
fi

echo ""
echo "============================================"
echo "Deployment Complete!"
echo "============================================"
echo ""
echo "Outputs saved to: deployment-outputs.json"
echo ""
echo "NEXT STEPS:"
echo "1. Review deployment-outputs.json"
echo "2. Update your .env file with the values from deployment-outputs.json"
echo "3. Run initialize-agent script to create the AI agent"
echo ""
echo "IMPORTANT NOTE:"
echo "This deployment used a simplified template without automatic"
echo "role assignments. The agent will use API keys for authentication."
echo ""
