#!/bin/bash
# Deployment script for AI Foundry Agent infrastructure

set -e

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-knowledge-hub-rg}"
LOCATION="${LOCATION:-eastus}"
ENVIRONMENT="${ENVIRONMENT:-dev}"

echo "============================================"
echo "Deploying AI Foundry Agent Infrastructure"
echo "============================================"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "Environment: $ENVIRONMENT"
echo "============================================"

# Login to Azure (if not already logged in)
echo "Checking Azure login..."
az account show &> /dev/null || az login

# Create resource group if it doesn't exist
echo "Creating resource group..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output table

# Deploy infrastructure
echo "Deploying infrastructure..."
az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file main.bicep \
  --parameters parameters.json \
  --parameters environment="$ENVIRONMENT" \
  --output table

# Get deployment outputs
echo "Getting deployment outputs..."
OUTPUTS=$(az deployment group show \
  --resource-group "$RESOURCE_GROUP" \
  --name main \
  --query properties.outputs \
  --output json)

echo "============================================"
echo "Deployment Complete!"
echo "============================================"
echo "$OUTPUTS" | jq '.'

# Save outputs to file
echo "$OUTPUTS" | jq '.' > deployment-outputs.json
echo ""
echo "Outputs saved to: deployment-outputs.json"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env"
echo "2. Update .env with the deployment outputs"
echo "3. Run 'make install' to install dependencies"
echo "4. Run 'make run' to start the API server"
