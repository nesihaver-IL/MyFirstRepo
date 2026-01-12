# Quick Start Operations Guide

## Overview

This guide provides step-by-step instructions for deploying, configuring, and operating the Knowledge Hub Agent with Azure AI Foundry. Follow each phase in order for a successful setup.

**Total Time**: ~1-2 hours for initial setup

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Azure subscription** with Contributor or Owner permissions
- [ ] **Azure CLI** installed (version 2.50.0 or higher)
  - Install: https://docs.microsoft.com/cli/azure/install-azure-cli
- [ ] **Python 3.9 or higher** installed
  - Verify: `python --version`
- [ ] **Git** installed for cloning the repository
- [ ] **Text editor** (VS Code, Sublime, etc.)
- [ ] **Estimated cost**: $150-300/month for dev environment, $500-1000/month for production
  - GPT-4o: ~$100-200/month
  - Azure AI Search: ~$30-150/month
  - App Service: ~$15-70/month
  - Other services: ~$5-80/month

### Required Azure Permissions

Your Azure account needs these role assignments:
- **Contributor** role on the subscription or resource group
- **Cognitive Services Contributor** for Azure OpenAI
- **Search Service Contributor** for Azure AI Search
- **Web Plan Contributor** for App Service

Verify permissions:
```bash
az role assignment list --assignee $(az account show --query user.name -o tsv)
```

---

## Phase 1: Infrastructure Deployment (30-45 minutes)

### Step 1.1: Validate Azure Access

```bash
# Login to Azure
az login

# List available subscriptions
az account list --output table

# Set the subscription you want to use
az account set --subscription "<your-subscription-id>"

# Verify current subscription
az account show

# Check resource provider registrations
az provider show -n Microsoft.CognitiveServices --query "registrationState"
az provider show -n Microsoft.Search --query "registrationState"
az provider show -n Microsoft.MachineLearningServices --query "registrationState"

# Register providers if not registered (returns "Registered")
az provider register -n Microsoft.CognitiveServices
az provider register -n Microsoft.Search
az provider register -n Microsoft.MachineLearningServices
```

**Expected Output**: All providers should show `"Registered"`

### Step 1.2: Choose Azure Region

Select a region that supports all required services:

**Recommended Regions**:
- `eastus` (US East Coast)
- `westus2` (US West Coast)
- `northeurope` (Europe - Ireland)
- `westeurope` (Europe - Netherlands)
- `uksouth` (UK - London)

**Check availability**:
```bash
# Check Azure OpenAI availability
az cognitiveservices account list-skus --location eastus --query "[?name=='S0' && kind=='OpenAI']"

# Check AI Search availability
az search service list-query-keys --resource-group test --name test 2>&1 | grep -i available
```

### Step 1.3: Set Environment Variables

```bash
# Navigate to project directory
cd /home/user/MyFirstRepo/02-work/ai-foundry-agent

# Set deployment variables
export RESOURCE_GROUP="knowledge-hub-rg"
export LOCATION="eastus"  # Choose your region
export PROJECT_NAME="knowledge-hub"  # Must be globally unique
export DEPLOYMENT_NAME="main-deployment"
```

### Step 1.4: Create Resource Group

```bash
# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Verify creation
az group show --name $RESOURCE_GROUP
```

### Step 1.5: Deploy Infrastructure

```bash
# Navigate to infrastructure directory
cd infrastructure

# Validate Bicep template first
az deployment group validate \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters projectName=$PROJECT_NAME \
  --parameters location=$LOCATION \
  --parameters environment=dev

# Deploy infrastructure (takes 15-20 minutes)
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --template-file main.bicep \
  --parameters projectName=$PROJECT_NAME \
  --parameters location=$LOCATION \
  --parameters environment=dev
```

**What This Creates**:
1. **AI Foundry Hub** - Central hub for AI projects
2. **AI Foundry Project** - Project workspace for the agent
3. **Azure OpenAI** - GPT-4o and text-embedding-3-large deployments
4. **Azure AI Search** - Vector store for RAG
5. **App Service** - Web app for API hosting
6. **Application Insights** - Monitoring and telemetry
7. **Key Vault** - Secrets management
8. **Storage Account** - File storage

**Deployment Duration**: 15-20 minutes

### Step 1.6: Capture Deployment Outputs

After deployment completes, capture the output values:

```bash
# Get deployment outputs
az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs

# Save specific outputs to variables
export AI_HUB_NAME=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.aiHubName.value -o tsv)
export AI_PROJECT_NAME=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.aiProjectName.value -o tsv)
export OPENAI_ENDPOINT=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.openAIEndpoint.value -o tsv)
export SEARCH_ENDPOINT=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.searchEndpoint.value -o tsv)
export WEBAPP_URL=$(az deployment group show --resource-group $RESOURCE_GROUP --name $DEPLOYMENT_NAME --query properties.outputs.webAppUrl.value -o tsv)

# Display values
echo "AI Hub: $AI_HUB_NAME"
echo "AI Project: $AI_PROJECT_NAME"
echo "OpenAI Endpoint: $OPENAI_ENDPOINT"
echo "Search Endpoint: $SEARCH_ENDPOINT"
echo "Web App URL: $WEBAPP_URL"
```

**💾 Save these values** - you'll need them in the next phase.

### Step 1.7: Verify Deployment

```bash
# List all resources in the resource group
az resource list --resource-group $RESOURCE_GROUP --output table

# Verify Azure OpenAI deployment
az cognitiveservices account deployment list \
  --resource-group $RESOURCE_GROUP \
  --name $(az cognitiveservices account list --resource-group $RESOURCE_GROUP --query "[?kind=='OpenAI'].name" -o tsv)

# Verify AI Search
az search service show \
  --resource-group $RESOURCE_GROUP \
  --name $(az search service list --resource-group $RESOURCE_GROUP --query "[0].name" -o tsv)
```

**Expected**: All resources should be listed and show "Succeeded" provisioning state.

---

## Phase 2: Environment Configuration (10 minutes)

### Step 2.1: Navigate to Project Root

```bash
# Go back to project root
cd /home/user/MyFirstRepo/02-work/ai-foundry-agent
```

### Step 2.2: Create Environment File

```bash
# Copy environment template
cp .env.example .env

# Verify file was created
ls -la .env
```

### Step 2.3: Configure Required Variables

Edit the `.env` file with your deployment values:

```bash
# Open in your preferred editor
nano .env
# or
vi .env
# or
code .env  # If using VS Code
```

**Required Configuration**:

```ini
# ===== AZURE SETTINGS (REQUIRED) =====
AZURE_SUBSCRIPTION_ID="<your-subscription-id>"
AZURE_RESOURCE_GROUP="knowledge-hub-rg"
AZURE_PROJECT_NAME="<AI_PROJECT_NAME from deployment>"

# ===== AGENT SETTINGS =====
AGENT_MODEL="gpt-4o"
AGENT_TEMPERATURE="0.3"
USE_FILE_SEARCH="true"

# ===== API SETTINGS =====
API_HOST="0.0.0.0"
API_PORT="8000"
LOG_LEVEL="INFO"

# ===== OPTIONAL: AZURE AI SEARCH =====
# Only needed if using custom vector store
# SEARCH_ENDPOINT="<SEARCH_ENDPOINT from deployment>"
# SEARCH_INDEX="product-knowledge-base"
```

**Get your subscription ID**:
```bash
az account show --query id -o tsv
```

### Step 2.4: Validate Configuration

```bash
# Check if all required variables are set
python3 -c "
import os
from pathlib import Path

# Load .env file
env_file = Path('.env')
if not env_file.exists():
    print('❌ .env file not found')
    exit(1)

required_vars = [
    'AZURE_SUBSCRIPTION_ID',
    'AZURE_RESOURCE_GROUP',
    'AZURE_PROJECT_NAME'
]

with open(env_file) as f:
    content = f.read()

missing = []
for var in required_vars:
    if var not in content or f'{var}=\"\"' in content or f'{var}=<' in content:
        missing.append(var)

if missing:
    print(f'❌ Missing or incomplete variables: {missing}')
    exit(1)
else:
    print('✅ All required configuration variables are set')
"
```

**Expected Output**: `✅ All required configuration variables are set`

---

## Phase 3: Install Dependencies (5 minutes)

### Step 3.1: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac

# For Windows:
# venv\Scripts\activate

# Verify activation (should show venv path)
which python
```

### Step 3.2: Upgrade pip

```bash
# Upgrade pip to latest version
pip install --upgrade pip setuptools wheel
```

### Step 3.3: Install Requirements

```bash
# Install all dependencies
pip install -r requirements.txt

# This installs:
# - azure-ai-projects (Azure AI Foundry SDK)
# - azure-search-documents (Azure AI Search)
# - fastapi & uvicorn (REST API)
# - pydantic (Configuration)
# - And other dependencies
```

**Duration**: 2-3 minutes

### Step 3.4: Verify Installation

```bash
# Verify key packages
python -c "import azure.ai.projects; print('✅ Azure AI Projects SDK:', azure.ai.projects.__version__)"
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)"
python -c "import azure.search.documents; print('✅ Azure Search:', azure.search.documents.__version__)"
python -c "import pydantic; print('✅ Pydantic:', pydantic.__version__)"
```

**Expected Output**: All packages should show version numbers without errors.

---

## Phase 4: Upload Product Documentation (15-30 minutes)

### Step 4.1: Prepare Documentation Files

**Supported Formats**:
- ✅ Markdown (`.md`)
- ✅ Plain text (`.txt`)
- ✅ PDF (`.pdf`)
- ✅ HTML (`.html`)
- ✅ Microsoft Word (`.docx`) - requires additional setup

**File Requirements**:
- **Maximum size per file**: 512 MB
- **Maximum total files**: 10,000 files per vector store
- **Recommended chunk size**: 1000 characters (configurable)
- **Recommended chunk overlap**: 200 characters (configurable)

**Best Practices**:
1. **Organize by category**: Create folders like `getting-started/`, `api-reference/`, `troubleshooting/`
2. **Use descriptive filenames**: `authentication-setup.md` instead of `doc1.md`
3. **Keep files focused**: One topic per file for better retrieval
4. **Include metadata**: Add frontmatter in markdown files if available
5. **Remove duplicates**: Avoid uploading the same content multiple times
6. **Update strategy**: Plan how you'll refresh documentation periodically

**Example Documentation Structure**:
```
docs/
├── getting-started/
│   ├── overview.md
│   ├── quick-start.md
│   └── installation.md
├── api-reference/
│   ├── authentication.md
│   ├── endpoints.md
│   └── examples.md
├── guides/
│   ├── integration-guide.md
│   ├── best-practices.md
│   └── advanced-features.md
└── troubleshooting/
    ├── common-issues.md
    ├── error-codes.md
    └── faq.md
```

### Step 4.2: Upload Using Python SDK (Recommended)

Create a Python script to upload your documentation:

**Option A: Upload Individual Files**

```python
from src.agent import KnowledgeHubAgent, AgentConfig

# Initialize agent configuration
config = AgentConfig(
    subscription_id="your-subscription-id",  # From .env
    resource_group="knowledge-hub-rg",       # From .env
    project_name="your-project-name"         # From .env
)

# Create agent instance
agent = KnowledgeHubAgent(config)

# Create vector store (one-time setup)
print("Creating vector store...")
agent.create_vector_store()

# Upload documentation files
print("Uploading documentation...")
file_paths = [
    "docs/product-overview.md",
    "docs/getting-started.md",
    "docs/api-reference.md",
    "docs/troubleshooting.md",
    "docs/faq.md"
]

file_ids = agent.upload_files(file_paths, update_vector_store=True)
print(f"✅ Successfully uploaded {len(file_ids)} files")
print(f"File IDs: {file_ids}")
```

**Option B: Batch Directory Upload**

```python
from src.agent import KnowledgeHubAgent, AgentConfig
from pathlib import Path

# Initialize agent
config = AgentConfig(
    subscription_id="your-subscription-id",
    resource_group="knowledge-hub-rg",
    project_name="your-project-name"
)

agent = KnowledgeHubAgent(config)
agent.create_vector_store()

# Get all markdown files in docs directory
docs_dir = Path("docs")
file_paths = list(docs_dir.rglob("*.md"))

print(f"Found {len(file_paths)} markdown files")

# Upload in batches (recommended for large sets)
batch_size = 20
for i in range(0, len(file_paths), batch_size):
    batch = [str(p) for p in file_paths[i:i+batch_size]]
    print(f"Uploading batch {i//batch_size + 1}...")
    file_ids = agent.upload_files(batch, update_vector_store=True)
    print(f"  Uploaded {len(file_ids)} files")

print("✅ All files uploaded successfully")
```

**Option C: Using the Upload Example Script**

```bash
# Use the provided example script
python examples/upload_documents.py
```

### Step 4.3: Verify Upload

```python
# Check vector store status
vector_store = agent.vector_store

print(f"Vector Store ID: {vector_store.id}")
print(f"Vector Store Name: {vector_store.name}")
print(f"Total Files: {vector_store.file_counts.total}")
print(f"In Progress: {vector_store.file_counts.in_progress}")
print(f"Completed: {vector_store.file_counts.completed}")
print(f"Failed: {vector_store.file_counts.failed}")
```

**Expected Output**:
```
Vector Store ID: vs_abc123...
Vector Store Name: product-docs
Total Files: 25
In Progress: 0
Completed: 25
Failed: 0
```

### Step 4.4: Using the REST API (Alternative)

If API is already running:

```bash
curl -X POST http://localhost:8000/upload-files \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": [
      "docs/product-overview.md",
      "docs/getting-started.md"
    ]
  }'
```

---

## Phase 5: Start API Server (2 minutes)

### Step 5.1: Start Server Locally

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Start the API server
make run

# Or manually:
# python -m src.api.main
```

**Expected Output**:
```
INFO:     Will watch for changes in these directories: ['/home/user/MyFirstRepo/02-work/ai-foundry-agent']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
2025-01-12 10:30:15,123 - __main__ - INFO - Initialized KnowledgeHubAgent for project: your-project-name
2025-01-12 10:30:16,456 - __main__ - INFO - Found existing vector store: vs_abc123
2025-01-12 10:30:18,789 - __main__ - INFO - Created agent: asst_xyz789 with model gpt-4o
INFO:     Application startup complete.
```

The server is now running on **http://localhost:8000**

### Step 5.2: Verify Server Health

Open a new terminal and test:

```bash
# Health check
curl http://localhost:8000/health

# Or using httpie
http http://localhost:8000/health

# Or open in browser
# http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "agent_initialized": true
}
```

### Step 5.3: Access API Documentation

The API server automatically generates interactive documentation:

**Swagger UI** (Interactive API testing):
- **URL**: http://localhost:8000/docs
- Features: Try out endpoints, see request/response schemas

**ReDoc** (Beautiful API documentation):
- **URL**: http://localhost:8000/redoc
- Features: Clean, responsive API documentation

Open these URLs in your browser to explore the API.

---

## Phase 6: Query the Agent (Ongoing Operations)

### Single Query (Stateless)

**Using cURL**:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I configure authentication?"
  }'
```

**Response**:
```json
{
  "answer": "To configure authentication in our system, you need to...",
  "thread_id": "thread_abc123xyz",
  "status": "success"
}
```

**Using Python requests**:

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"question": "How do I configure authentication?"}
)

data = response.json()
print(f"Answer: {data['answer']}")
```

### Multi-Turn Conversation (Stateful)

For conversations where context matters:

**Step 1: Create a Conversation Thread**

```bash
curl -X POST http://localhost:8000/threads/create
```

**Response**:
```json
{
  "thread_id": "thread_xyz789"
}
```

**Step 2: Ask First Question**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the pricing tiers?",
    "thread_id": "thread_xyz789"
  }'
```

**Step 3: Ask Follow-up Question (Context Maintained)**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which tier is best for startups?",
    "thread_id": "thread_xyz789"
  }'
```

The agent remembers the previous context about pricing tiers!

**Step 4: View Conversation History**

```bash
curl http://localhost:8000/threads/thread_xyz789/history
```

**Response**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What are the pricing tiers?",
      "created_at": "2025-01-12T10:35:00Z"
    },
    {
      "role": "assistant",
      "content": "We offer three pricing tiers: Basic, Pro, and Enterprise...",
      "created_at": "2025-01-12T10:35:02Z"
    },
    {
      "role": "user",
      "content": "Which tier is best for startups?",
      "created_at": "2025-01-12T10:35:10Z"
    },
    {
      "role": "assistant",
      "content": "For startups, we recommend the Pro tier because...",
      "created_at": "2025-01-12T10:35:12Z"
    }
  ]
}
```

### Using Python SDK

**Single Query**:

```python
from src.agent import KnowledgeHubAgent, AgentConfig

# Initialize agent
config = AgentConfig(
    subscription_id="your-subscription-id",
    resource_group="knowledge-hub-rg",
    project_name="your-project-name"
)

agent = KnowledgeHubAgent(config)
agent.create_agent()

# Ask a question
response = agent.query("How do I reset my password?")
print(response)
```

**Multi-Turn Conversation**:

```python
# Create a new conversation thread
thread = agent.create_thread()
print(f"Thread ID: {thread.id}")

# First question
agent.add_message(thread.id, "What integrations are available?")
result = agent.run_agent(thread.id)
print(f"Assistant: {result['messages'][0]['content']}")

# Follow-up question (context maintained)
agent.add_message(thread.id, "How do I set up the Slack integration?")
result = agent.run_agent(thread.id)
print(f"Assistant: {result['messages'][0]['content']}")

# Get full conversation history
history = agent.get_thread_history(thread.id)
for msg in history:
    print(f"{msg['role'].upper()}: {msg['content'][:100]}...")
```

### Using the Example API Client

```bash
# Run the example client
python examples/api_client.py

# This demonstrates:
# - Health checks
# - Single queries
# - Multi-turn conversations
# - History retrieval
```

---

## Phase 7: Monitoring & Maintenance

### Monitor Application Insights

**Access Application Insights**:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Resource Group (`knowledge-hub-rg`)
3. Click on the Application Insights resource
4. Explore metrics and logs

**Key Metrics to Monitor**:

1. **Request Rate**
   - Path: Application Insights → Metrics → Server requests
   - Target: Monitor for unusual spikes or drops

2. **Response Time**
   - Path: Application Insights → Metrics → Server response time
   - Target: Keep average under 5 seconds

3. **Failure Rate**
   - Path: Application Insights → Metrics → Failed requests
   - Target: Keep under 1%

4. **Custom Events**
   - Path: Application Insights → Logs → Custom Events
   - Query agent interactions, errors, etc.

**Useful Log Queries** (Application Insights → Logs):

```kusto
// Recent errors
traces
| where severityLevel >= 3
| order by timestamp desc
| take 50

// Agent query performance
customEvents
| where name == "agent_query"
| summarize avg(duration), count() by bin(timestamp, 1h)

// Failed requests
requests
| where success == false
| order by timestamp desc
| project timestamp, name, resultCode, duration
```

### Update Documentation

When your product documentation changes:

**Add New Files**:

```python
# Upload new or updated files
new_file_ids = agent.upload_files([
    "docs/new-feature-guide.md",
    "docs/updated-api-reference.md"
], update_vector_store=True)

print(f"Uploaded {len(new_file_ids)} new files")
```

**Delete Old Files**:

```python
# Delete outdated files from vector store
agent.client.agents.delete_vector_store_file(
    vector_store_id=agent.vector_store.id,
    file_id="file_old123"
)
```

**Complete Refresh**:

```python
# For major updates, create a new vector store
new_vector_store = agent.create_vector_store()

# Upload all current documentation
file_paths = list(Path("docs").rglob("*.md"))
agent.upload_files([str(p) for p in file_paths], update_vector_store=True)

# Delete old vector store after verifying new one works
# (Keep old one as backup for a while)
```

### Backup Vector Store

Create backups of your vector store metadata:

```python
# Export vector store information
vector_store_info = {
    "id": agent.vector_store.id,
    "name": agent.vector_store.name,
    "file_counts": agent.vector_store.file_counts,
    "created_at": agent.vector_store.created_at
}

# Save to file
import json
from datetime import datetime

backup_file = f"backup-{datetime.now().strftime('%Y%m%d')}.json"
with open(backup_file, 'w') as f:
    json.dump(vector_store_info, f, indent=2)

print(f"Backup saved to {backup_file}")
```

### Restart API Server

If you need to restart the server:

```bash
# Stop the server (Ctrl+C in terminal)

# Restart
make run
```

For production (Azure Web App):

```bash
# Restart the web app
az webapp restart \
  --name your-webapp-name \
  --resource-group knowledge-hub-rg
```

---

## Troubleshooting Common Issues

### Issue 1: Agent Not Initializing

**Symptom**:
```json
{"status": "healthy", "agent_initialized": false}
```

**Possible Causes & Solutions**:

1. **Invalid Configuration**
   ```bash
   # Check .env file
   cat .env | grep AZURE_

   # Verify values are not placeholders
   # Bad: AZURE_PROJECT_NAME="<from-deployment-output>"
   # Good: AZURE_PROJECT_NAME="knowledge-hub-dev-project"
   ```

2. **Authentication Issues**
   ```bash
   # Re-authenticate with Azure
   az login
   az account show

   # Check if correct subscription is set
   az account set --subscription "your-subscription-id"
   ```

3. **Missing Resources**
   ```bash
   # Verify AI Foundry project exists
   az ml workspace show \
     --name your-project-name \
     --resource-group knowledge-hub-rg
   ```

4. **Restart Server**
   ```bash
   # Stop server (Ctrl+C)
   # Clear any cached credentials
   rm -rf ~/.azure/
   az login
   # Restart
   make run
   ```

### Issue 2: File Upload Fails

**Symptom**: Error during `agent.upload_files()`

**Possible Causes & Solutions**:

1. **File Too Large**
   ```python
   # Check file sizes
   import os
   for file_path in file_paths:
       size_mb = os.path.getsize(file_path) / (1024 * 1024)
       print(f"{file_path}: {size_mb:.2f} MB")
   ```

   Solution: Files must be under 512 MB. Split large files if needed.

2. **Invalid File Format**
   ```python
   # Verify file extensions
   supported = ['.md', '.txt', '.pdf', '.html', '.docx']
   for path in file_paths:
       ext = Path(path).suffix
       if ext not in supported:
           print(f"Warning: {path} has unsupported extension {ext}")
   ```

3. **Azure OpenAI Quota Exceeded**
   ```bash
   # Check quota usage
   az cognitiveservices account list-usage \
     --name your-openai-account \
     --resource-group knowledge-hub-rg
   ```

   Solution: Request quota increase or wait for reset.

4. **Network/Permissions Issues**
   ```bash
   # Test connectivity
   curl https://your-openai-endpoint.openai.azure.com/

   # Verify permissions
   az role assignment list \
     --assignee $(az account show --query user.name -o tsv) \
     --scope /subscriptions/your-sub-id/resourceGroups/knowledge-hub-rg
   ```

### Issue 3: Poor Search Results

**Symptom**: Agent returns irrelevant or incorrect answers

**Possible Causes & Solutions**:

1. **Documents Not Indexed**
   ```python
   # Verify documents were uploaded
   print(f"Files in vector store: {agent.vector_store.file_counts.completed}")
   ```

   Wait a few minutes for indexing to complete.

2. **Check Chunk Settings**
   ```python
   # Review chunking configuration
   from src.vector_store import DocumentProcessor
   processor = DocumentProcessor(
       chunk_size=1000,  # Try adjusting
       chunk_overlap=200
   )
   ```

   Larger chunks = more context but less precision
   Smaller chunks = more precision but less context

3. **Temperature Too High**
   ```python
   # Lower temperature for more focused answers
   config = AgentConfig(
       ...
       temperature=0.1  # Lower = more deterministic
   )
   ```

4. **Query Too Vague**
   - Bad: "How does it work?"
   - Good: "How do I configure OAuth authentication?"

   Encourage users to ask specific questions.

5. **Document Quality Issues**
   - Ensure documentation is well-structured
   - Use clear headings and sections
   - Avoid duplicate content
   - Keep information up-to-date

### Issue 4: Slow Response Times

**Symptom**: Queries taking >10 seconds

**Possible Causes & Solutions**:

1. **Azure OpenAI Throttling**
   ```bash
   # Check for 429 errors in Application Insights
   # Increase quota or add retry logic
   ```

2. **Large Vector Store**
   ```python
   # Check vector store size
   print(f"Total files: {agent.vector_store.file_counts.total}")
   ```

   Solution: If >10,000 files, consider splitting into multiple stores.

3. **Network Latency**
   ```bash
   # Test network latency to Azure
   curl -w "@curl-format.txt" -o /dev/null -s https://your-openai-endpoint.openai.azure.com/
   ```

   Solution: Deploy in the same region as your users.

4. **App Service Tier Too Low**
   ```bash
   # Check current tier
   az appservice plan show \
     --name your-app-plan \
     --resource-group knowledge-hub-rg \
     --query sku
   ```

   Solution: Upgrade to S1 or P1V2 tier.

### Issue 5: Authentication Errors

**Symptom**: `AuthenticationError` or 401/403 responses

**Solutions**:

```bash
# Clear cached credentials
az account clear
rm -rf ~/.azure/

# Re-login
az login

# Verify token
az account get-access-token --resource https://cognitiveservices.azure.com/

# Check managed identity (if using in Azure)
az webapp identity show \
  --name your-webapp \
  --resource-group knowledge-hub-rg
```

---

## Production Deployment Considerations

### Security Hardening Checklist

Before deploying to production:

- [ ] **Change CORS settings** from `"*"` to specific origins
  ```python
  # In src/api/main.py
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://yourdomain.com"],  # Not "*"
      allow_credentials=True,
      allow_methods=["GET", "POST"],
      allow_headers=["*"],
  )
  ```

- [ ] **Implement API authentication** (Azure AD, API keys)
- [ ] **Enable HTTPS only** in App Service
- [ ] **Configure network security groups**
- [ ] **Enable Azure Private Link** for AI services
- [ ] **Review and restrict Key Vault access**
- [ ] **Enable Azure Defender** for threat protection
- [ ] **Set up WAF** (Web Application Firewall)
- [ ] **Implement rate limiting**
- [ ] **Enable audit logging**

### Scaling Checklist

- [ ] **Upgrade App Service Plan** (B1 → S1 or P1V2)
- [ ] **Configure auto-scaling rules**
- [ ] **Increase Azure OpenAI quota** (default 240K tokens/min)
- [ ] **Upgrade Azure AI Search tier** if needed
- [ ] **Enable Azure CDN** for static assets
- [ ] **Implement caching** (Redis) for frequent queries
- [ ] **Configure load balancing** if multiple regions

### Monitoring Setup

- [ ] **Set up availability tests** in Application Insights
- [ ] **Configure alert rules**:
  - Response time > 5 seconds
  - Error rate > 1%
  - Server CPU > 80%
  - Memory usage > 85%
- [ ] **Create Azure Monitor dashboard**
- [ ] **Enable diagnostic logging** for all services
- [ ] **Configure log retention** (30-90 days)
- [ ] **Set up Azure Monitor Workbooks**

---

## Quick Reference Commands

### Development

```bash
make install          # Install dependencies
make run             # Start API server
make test            # Run tests
make lint            # Check code quality
make format          # Format code
make clean           # Clean build artifacts
```

### Deployment

```bash
# Deploy infrastructure
cd infrastructure && ./deploy.sh

# Deploy application to Azure
az webapp up \
  --name your-webapp \
  --resource-group knowledge-hub-rg \
  --runtime "PYTHON:3.11"
```

### Monitoring

```bash
# View Application Insights metrics
az monitor app-insights metrics show \
  --app your-app-insights \
  --resource-group knowledge-hub-rg \
  --metric requests/count

# Stream logs
az webapp log tail \
  --name your-webapp \
  --resource-group knowledge-hub-rg

# Check deployment status
az deployment group show \
  --resource-group knowledge-hub-rg \
  --name main-deployment
```

### Maintenance

```bash
# Restart API server locally
# Ctrl+C, then: make run

# Restart Azure Web App
az webapp restart \
  --name your-webapp \
  --resource-group knowledge-hub-rg

# Update configuration
az webapp config appsettings set \
  --name your-webapp \
  --resource-group knowledge-hub-rg \
  --settings AGENT_TEMPERATURE=0.2
```

---

## Support & Resources

### Documentation
- **Project README**: `/02-work/ai-foundry-agent/README.md`
- **API Reference**: http://localhost:8000/docs (when running)
- **Examples**: `/02-work/ai-foundry-agent/examples/`
- **Troubleshooting**: `/02-work/ai-foundry-agent/docs/troubleshooting.md`
- **Architecture**: `/02-work/ai-foundry-agent/docs/architecture.md`

### Azure Resources
- **Azure AI Foundry**: https://learn.microsoft.com/azure/ai-studio/
- **Azure OpenAI**: https://learn.microsoft.com/azure/ai-services/openai/
- **Azure AI Search**: https://learn.microsoft.com/azure/search/
- **Application Insights**: https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview

### Community
- **GitHub Issues**: Report bugs and request features
- **Azure Community**: https://techcommunity.microsoft.com/t5/azure-ai/bd-p/AzureAI

---

## Next Steps

After completing this guide, you should:

✅ Have a fully deployed Knowledge Hub Agent
✅ Be able to upload and manage documentation
✅ Query the agent via API or Python SDK
✅ Monitor performance in Application Insights

**What's Next?**
1. Review [docs/operations/document-management.md](./document-management.md) for advanced document strategies
2. Check [docs/operations/production-checklist.md](./production-checklist.md) before going live
3. Set up monitoring and alerts following [docs/operations/monitoring-guide.md](./monitoring-guide.md)
4. Read [docs/troubleshooting.md](../troubleshooting.md) for additional help

---

*Last Updated: 2025-01-12*
