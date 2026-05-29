#!/bin/bash
# Register required Azure resource providers for AI Foundry deployment

echo "============================================"
echo "Registering Azure Resource Providers"
echo "============================================"
echo ""

# List of required resource providers
PROVIDERS=(
    "Microsoft.MachineLearningServices"
    "Microsoft.CognitiveServices"
    "Microsoft.Search"
    "Microsoft.Storage"
    "Microsoft.KeyVault"
    "Microsoft.Insights"
    "Microsoft.OperationalInsights"
    "Microsoft.Web"
)

echo "Registering resource providers (this may take a few minutes)..."
echo ""

for provider in "${PROVIDERS[@]}"; do
    echo "Registering: $provider"
    az provider register --namespace "$provider" --wait

    if [ $? -eq 0 ]; then
        echo "  ✓ Successfully registered: $provider"
    else
        echo "  ✗ Failed to register: $provider"
    fi
    echo ""
done

echo "============================================"
echo "Checking Registration Status"
echo "============================================"
echo ""

for provider in "${PROVIDERS[@]}"; do
    status=$(az provider show --namespace "$provider" --query "registrationState" -o tsv)
    echo "$provider: $status"
done

echo ""
echo "============================================"
echo "Registration Complete!"
echo "============================================"
echo ""
echo "You can now proceed with the deployment."
echo ""
