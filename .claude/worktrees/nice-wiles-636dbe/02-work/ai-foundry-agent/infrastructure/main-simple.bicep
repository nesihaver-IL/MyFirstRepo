// Simplified Bicep template for AI Foundry Agent deployment
// This version skips automatic role assignments to work with limited permissions
targetScope = 'resourceGroup'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Project name (used as prefix for resources)')
param projectName string

@description('Environment (dev, staging, prod)')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environment string = 'dev'

@description('AI Foundry Hub name')
param aiHubName string = '${projectName}-${environment}-hub'

@description('AI Foundry Project name')
param aiProjectName string = '${projectName}-${environment}-project'

@description('Azure OpenAI service name')
param openAIName string = '${projectName}-${environment}-openai'

@description('Azure AI Search service name')
param searchName string = '${projectName}-${environment}-search'

@description('Storage Account name')
param storageAccountName string = replace('${projectName}${environment}storage', '-', '')

@description('Application Insights name')
param appInsightsName string = '${projectName}-${environment}-insights'

@description('Key Vault name')
param keyVaultName string = '${projectName}-${environment}-kv'

@description('OpenAI model deployment name')
param modelDeploymentName string = 'gpt-4o'

@description('OpenAI model version')
param modelVersion string = '2024-08-06'

@description('OpenAI model capacity')
param modelCapacity int = 30

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    RetentionInDays: 90
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Key Vault (with access policies instead of RBAC)
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: false  // Using access policies instead
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    accessPolicies: []  // Will configure manually later
  }
}

// Azure OpenAI
resource openAI 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
  name: openAIName
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openAIName
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

// OpenAI Model Deployment
resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
  parent: openAI
  name: modelDeploymentName
  sku: {
    name: 'Standard'
    capacity: modelCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: modelVersion
    }
  }
}

// Embedding Model Deployment
resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
  parent: openAI
  name: 'text-embedding-3-large'
  sku: {
    name: 'Standard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-3-large'
      version: '1'
    }
  }
  dependsOn: [
    modelDeployment
  ]
}

// Azure AI Search
resource search 'Microsoft.Search/searchServices@2024-03-01-preview' = {
  name: searchName
  location: location
  sku: {
    name: 'standard'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    semanticSearch: 'free'
  }
}

// AI Foundry Hub
resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: aiHubName
  location: location
  kind: 'Hub'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'AI Foundry Hub - ${projectName}'
    description: 'Hub for AI agent development'
    storageAccount: storageAccount.id
    keyVault: keyVault.id
    applicationInsights: appInsights.id
    publicNetworkAccess: 'Enabled'
  }
}

// AI Foundry Project
resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: aiProjectName
  location: location
  kind: 'Project'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'Knowledge Hub Agent Project'
    description: 'AI agent for product knowledge hub with RAG'
    hubResourceId: aiHub.id
    publicNetworkAccess: 'Enabled'
  }
}

// AI Hub Connection to OpenAI
resource openAIConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-04-01' = {
  parent: aiHub
  name: '${openAIName}-connection'
  properties: {
    category: 'AzureOpenAI'
    target: openAI.properties.endpoint
    authType: 'ApiKey'
    isSharedToAll: true
    credentials: {
      key: openAI.listKeys().key1
    }
    metadata: {
      ApiVersion: '2024-08-01-preview'
      ApiType: 'azure'
      ResourceId: openAI.id
    }
  }
}

// NOTE: Role assignments removed to avoid permission errors
// You can assign roles manually via Azure Portal if needed later

// Outputs
output aiHubName string = aiHub.name
output aiProjectName string = aiProject.name
output aiProjectResourceId string = aiProject.id
output openAIEndpoint string = openAI.properties.endpoint
output openAIKey string = openAI.listKeys().key1
output searchEndpoint string = 'https://${searchName}.search.windows.net'
output searchKey string = search.listAdminKeys().primaryKey
output keyVaultName string = keyVault.name
output storageAccountName string = storageAccount.name
output subscriptionId string = subscription().subscriptionId
output resourceGroupName string = resourceGroup().name
