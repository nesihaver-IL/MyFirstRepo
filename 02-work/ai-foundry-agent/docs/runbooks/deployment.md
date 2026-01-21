# Deployment Runbook

This runbook provides step-by-step procedures for deploying the Knowledge Hub Agent to Azure environments (Dev, Staging, Production).

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Environment Setup](#environment-setup)
- [Infrastructure Deployment](#infrastructure-deployment)
- [Application Deployment](#application-deployment)
- [Post-Deployment Validation](#post-deployment-validation)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Planning Phase

- [ ] **Environment determined**: Dev / Staging / Production
- [ ] **Azure subscription selected and validated**
- [ ] **Required permissions verified** (Contributor role minimum)
- [ ] **Budget approval obtained** (if applicable)
- [ ] **Change request approved** (for production deployments)
- [ ] **Maintenance window scheduled** (for production)
- [ ] **Stakeholders notified**

### Technical Prerequisites

- [ ] **Azure CLI installed** (version 2.50.0+)
  ```bash
  az --version
  ```

- [ ] **Logged in to Azure**
  ```bash
  az login
  az account show
  ```

- [ ] **Correct subscription selected**
  ```bash
  az account set --subscription "your-subscription-id"
  ```

- [ ] **Resource providers registered**
  ```bash
  az provider register -n Microsoft.CognitiveServices
  az provider register -n Microsoft.Search
  az provider register -n Microsoft.MachineLearningServices
  az provider register -n Microsoft.Web
  az provider register -n Microsoft.KeyVault
  ```

- [ ] **Region capacity verified** (check Azure service availability)
- [ ] **Naming convention determined** (project-env-resource)
- [ ] **Tags defined** (environment, owner, cost-center, etc.)

### Documentation

- [ ] **Deployment plan reviewed**
- [ ] **Rollback plan prepared**
- [ ] **Runbook accessible**
- [ ] **Architecture diagram available**
- [ ] **Contact list prepared** (escalation path)

---

## Environment Setup

### 1. Set Environment Variables

```bash
# Set deployment variables
export ENVIRONMENT="dev"  # or staging, prod
export PROJECT_NAME="knowledge-hub"
export RESOURCE_GROUP="${PROJECT_NAME}-${ENVIRONMENT}-rg"
export LOCATION="eastus"  # or westus2, northeurope
export DEPLOYMENT_NAME="${PROJECT_NAME}-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"

# Tag configuration
export TAGS="environment=${ENVIRONMENT} project=${PROJECT_NAME} managed-by=bicep"

# Display configuration
echo "Environment: $ENVIRONMENT"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "Deployment Name: $DEPLOYMENT_NAME"
```

### 2. Verify Parameters

```bash
# Review parameter file
cat infrastructure/parameters.json

# Update for target environment if needed
cp infrastructure/parameters.json infrastructure/parameters-${ENVIRONMENT}.json
```

### 3. Create Resource Group

```bash
# Create resource group with tags
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION \
  --tags $TAGS

# Verify creation
az group show --name $RESOURCE_GROUP
```

---

## Infrastructure Deployment

### Phase 1: Validate Bicep Template

**Estimated Time**: 2-3 minutes

```bash
# Navigate to infrastructure directory
cd infrastructure

# Validate template syntax
az bicep build --file main.bicep

# Validate deployment (dry-run)
az deployment group validate \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters projectName=$PROJECT_NAME \
  --parameters location=$LOCATION \
  --parameters environment=$ENVIRONMENT

# Check validation result
echo $?  # Should be 0 for success
```

**Expected Output**: No errors, validation succeeds

**If Validation Fails**:
1. Review error messages
2. Check parameter values
3. Verify resource name uniqueness
4. Consult [troubleshooting guide](../troubleshooting.md)

### Phase 2: Deploy Infrastructure

**Estimated Time**: 15-25 minutes

```bash
# Start deployment with What-If preview (optional)
az deployment group what-if \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters projectName=$PROJECT_NAME \
  --parameters location=$LOCATION \
  --parameters environment=$ENVIRONMENT

# Proceed with actual deployment
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --template-file main.bicep \
  --parameters projectName=$PROJECT_NAME \
  --parameters location=$LOCATION \
  --parameters environment=$ENVIRONMENT \
  --verbose

# Monitor deployment progress (in another terminal)
watch -n 10 "az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.provisioningState"
```

**Resources Created**:
1. AI Foundry Hub
2. AI Foundry Project
3. Azure OpenAI with model deployments
4. Azure AI Search
5. App Service Plan
6. Web App
7. Application Insights
8. Key Vault
9. Storage Account

**Deployment Progress**:
- 0-5 min: Creating foundational resources (Storage, Key Vault)
- 5-10 min: Creating AI services (OpenAI, Search)
- 10-15 min: Creating AI Foundry Hub and Project
- 15-20 min: Deploying models to Azure OpenAI
- 20-25 min: Creating App Service and final configurations

### Phase 3: Capture Deployment Outputs

```bash
# Get all outputs
az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs

# Save outputs to file
az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs > deployment-outputs-${ENVIRONMENT}.json

# Export specific values
export AI_HUB_NAME=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.aiHubName.value -o tsv)
export AI_PROJECT_NAME=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.aiProjectName.value -o tsv)
export OPENAI_ENDPOINT=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.openAIEndpoint.value -o tsv)
export SEARCH_ENDPOINT=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.searchEndpoint.value -o tsv)
export WEBAPP_NAME=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.webAppName.value -o tsv)
export WEBAPP_URL=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.webAppUrl.value -o tsv)
export KEYVAULT_NAME=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.keyVaultName.value -o tsv)

# Display values
echo "=== Deployment Outputs ==="
echo "AI Project: $AI_PROJECT_NAME"
echo "OpenAI Endpoint: $OPENAI_ENDPOINT"
echo "Search Endpoint: $SEARCH_ENDPOINT"
echo "Web App: $WEBAPP_URL"
echo "Key Vault: $KEYVAULT_NAME"
```

### Phase 4: Verify Infrastructure

```bash
# List all resources
az resource list --resource-group $RESOURCE_GROUP --output table

# Verify key resources
# 1. Azure OpenAI
az cognitiveservices account show \
  --name $(az cognitiveservices account list --resource-group $RESOURCE_GROUP --query "[?kind=='OpenAI'].name" -o tsv) \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, State:properties.provisioningState, Endpoint:properties.endpoint}"

# 2. Model deployments
az cognitiveservices account deployment list \
  --name $(az cognitiveservices account list --resource-group $RESOURCE_GROUP --query "[?kind=='OpenAI'].name" -o tsv) \
  --resource-group $RESOURCE_GROUP \
  --output table

# 3. AI Search
az search service show \
  --name $(az search service list --resource-group $RESOURCE_GROUP --query "[0].name" -o tsv) \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, State:provisioningState, Tier:sku.name}"

# 4. Web App
az webapp show \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, State:state, URL:defaultHostName}"
```

**Expected Results**: All resources show "Succeeded" or "Running" state

---

## Application Deployment

### Phase 5: Configure Application Settings

```bash
# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Configure Web App settings
az webapp config appsettings set \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    AZURE_SUBSCRIPTION_ID=$SUBSCRIPTION_ID \
    AZURE_RESOURCE_GROUP=$RESOURCE_GROUP \
    AZURE_PROJECT_NAME=$AI_PROJECT_NAME \
    AGENT_MODEL="gpt-4o" \
    AGENT_TEMPERATURE="0.3" \
    USE_FILE_SEARCH="true" \
    API_HOST="0.0.0.0" \
    API_PORT="8000" \
    LOG_LEVEL="INFO" \
    SEARCH_ENDPOINT=$SEARCH_ENDPOINT \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE="false"

# Verify settings
az webapp config appsettings list \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table
```

### Phase 6: Deploy Application Code

**Option A: Deploy from Git Repository**

```bash
# Configure deployment source (GitHub)
az webapp deployment source config \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --repo-url https://github.com/your-org/your-repo \
  --branch main \
  --manual-integration  # Or use --git-token for auto-sync

# Trigger deployment
az webapp deployment source sync \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP
```

**Option B: Deploy from Local Directory**

```bash
# Navigate to project root
cd /home/user/MyFirstRepo/02-work/ai-foundry-agent

# Create deployment package
zip -r deploy.zip . -x ".git/*" -x "venv/*" -x "__pycache__/*" -x "*.pyc"

# Deploy to Azure
az webapp deployment source config-zip \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --src deploy.zip

# Clean up
rm deploy.zip
```

**Option C: Use Azure CLI Quick Deploy**

```bash
# Quick deploy (builds and deploys)
az webapp up \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --runtime "PYTHON:3.11" \
  --sku B1
```

### Phase 7: Monitor Deployment

```bash
# Stream deployment logs
az webapp log tail \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP

# Check deployment status
az webapp deployment list \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table
```

**Expected**: Deployment succeeds, application starts

---

## Post-Deployment Validation

### Phase 8: Health Checks

**1. Web App Health**

```bash
# Check if app is running
az webapp show \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query state

# Expected: "Running"
```

**2. API Health Endpoint**

```bash
# Test health endpoint
curl https://${WEBAPP_URL}/health

# Expected response:
# {"status": "healthy", "agent_initialized": true}
```

**3. API Documentation**

```bash
# Verify Swagger UI is accessible
curl -I https://${WEBAPP_URL}/docs

# Expected: HTTP 200
```

### Phase 9: Functional Testing

**1. Test Agent Query**

```bash
# Simple query test
curl -X POST https://${WEBAPP_URL}/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello, are you working?"}' | jq

# Expected: Valid JSON response with "answer" field
```

**2. Test Thread Creation**

```bash
# Create thread
THREAD_ID=$(curl -X POST https://${WEBAPP_URL}/threads/create -s | jq -r '.thread_id')

echo "Created thread: $THREAD_ID"

# Query with thread
curl -X POST https://${WEBAPP_URL}/query \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Test question\", \"thread_id\": \"$THREAD_ID\"}" | jq
```

### Phase 10: Monitoring Setup Verification

```bash
# Verify Application Insights is receiving data
az monitor app-insights component show \
  --app $(az monitor app-insights component list --resource-group $RESOURCE_GROUP --query "[0].name" -o tsv) \
  --resource-group $RESOURCE_GROUP

# Check recent telemetry (wait 2-3 minutes after deployment)
az monitor app-insights query \
  --app $(az monitor app-insights component list --resource-group $RESOURCE_GROUP --query "[0].name" -o tsv) \
  --resource-group $RESOURCE_GROUP \
  --analytics-query "requests | where timestamp > ago(10m) | take 10"
```

### Phase 11: Document Deployment

```bash
# Save deployment information
cat > deployment-record-${ENVIRONMENT}-$(date +%Y%m%d).txt <<EOF
Deployment Record
=================
Date: $(date)
Environment: $ENVIRONMENT
Resource Group: $RESOURCE_GROUP
Deployment Name: $DEPLOYMENT_NAME
Web App URL: https://$WEBAPP_URL
Deployed By: $(az account show --query user.name -o tsv)

Resources:
- AI Project: $AI_PROJECT_NAME
- OpenAI Endpoint: $OPENAI_ENDPOINT
- Search Endpoint: $SEARCH_ENDPOINT
- Key Vault: $KEYVAULT_NAME

Validation:
- Health Check: $(curl -s https://${WEBAPP_URL}/health | jq -r '.status')
- Agent Initialized: $(curl -s https://${WEBAPP_URL}/health | jq -r '.agent_initialized')

Notes:
EOF

# Add any additional notes
echo "Deployment completed successfully" >> deployment-record-${ENVIRONMENT}-$(date +%Y%m%d).txt
```

---

## Rollback Procedures

### When to Rollback

Rollback if:
- Health checks fail after 15 minutes
- Critical functionality broken
- High error rate (>5% of requests)
- Performance degradation (response time >10s)
- Security vulnerability discovered

### Rollback Options

#### Option 1: Revert Application Deployment (Quick)

**Time**: 2-5 minutes

```bash
# List previous deployments
az webapp deployment list \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table

# Get previous deployment ID
PREVIOUS_DEPLOYMENT=$(az webapp deployment list \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[1].id" -o tsv)

# Rollback to previous version
az webapp deployment source config-zip \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --src previous-version.zip  # Use backup of previous deployment

# Or restore from slot (if using deployment slots)
az webapp deployment slot swap \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP \
  --slot staging \
  --target-slot production
```

#### Option 2: Revert Infrastructure Changes (Moderate)

**Time**: 10-15 minutes

```bash
# Redeploy previous Bicep template
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --name "${DEPLOYMENT_NAME}-rollback" \
  --template-file main.bicep.backup \
  --parameters parameters-previous.json
```

#### Option 3: Full Environment Restore (Last Resort)

**Time**: 20-30 minutes

```bash
# Delete current deployment
az group delete --name $RESOURCE_GROUP --yes --no-wait

# Redeploy from backup
# (Follow deployment procedures with previous configuration)
```

### Post-Rollback Steps

1. **Verify rollback succeeded**:
   ```bash
   curl https://${WEBAPP_URL}/health
   ```

2. **Notify stakeholders** of rollback

3. **Document incident**:
   - What failed
   - Why rollback was needed
   - What was rolled back
   - Current state

4. **Schedule root cause analysis**

5. **Plan remediation** before attempting deployment again

---

## Troubleshooting

### Deployment Fails at Resource Creation

**Solution**: Check deployment operations
```bash
az deployment operation group list \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query "[?properties.provisioningState=='Failed'].{Resource:properties.targetResource.resourceName, Error:properties.statusMessage.error}"
```

### Application Won't Start

**Solution**: Check application logs
```bash
az webapp log tail \
  --name $WEBAPP_NAME \
  --resource-group $RESOURCE_GROUP
```

### Health Check Fails

**Solution**:
1. Wait 5 minutes (cold start)
2. Check Application Insights for errors
3. Verify environment variables are set
4. Test Azure connectivity from app

---

## Checklist Summary

### Pre-Deployment
- [ ] Prerequisites verified
- [ ] Permissions confirmed
- [ ] Parameters configured
- [ ] Resource group created

### Deployment
- [ ] Template validated
- [ ] Infrastructure deployed
- [ ] Outputs captured
- [ ] Resources verified
- [ ] Application configured
- [ ] Code deployed

### Post-Deployment
- [ ] Health checks passed
- [ ] Functional tests passed
- [ ] Monitoring configured
- [ ] Deployment documented
- [ ] Stakeholders notified

### Rollback Plan
- [ ] Backup created
- [ ] Rollback procedure tested
- [ ] Rollback contact list ready

---

*Last Updated: 2025-01-12*
