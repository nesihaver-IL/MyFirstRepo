# Windows Execution Plan - Azure AI Foundry Knowledge Hub Agent

## Overview

This plan guides you through deploying and running the Azure AI Foundry Knowledge Hub Agent on your local Windows machine with Azure CLI installed.

## Prerequisites

✅ **Already Installed:**
- Windows OS
- Azure CLI

**Still Needed:**
- Python 3.9 or higher
- Git (recommended)
- Azure subscription with appropriate permissions

---

## Phase 1: Environment Setup (Windows)

### Step 1.1: Install Python

1. Download Python 3.9+ from https://www.python.org/downloads/windows/
2. During installation, check "Add Python to PATH"
3. Verify installation:
```cmd
python --version
pip --version
```

### Step 1.2: Verify Azure CLI

```cmd
az --version
az account show
```

If not logged in:
```cmd
az login
```

### Step 1.3: Set Up Project Directory

Navigate to the project directory:
```cmd
cd C:\path\to\MyFirstRepo\02-work\ai-foundry-agent
```

Or if using PowerShell:
```powershell
cd C:\path\to\MyFirstRepo\02-work\ai-foundry-agent
```

---

## Phase 2: Azure Infrastructure Deployment

### Step 2.1: Set Configuration Variables (PowerShell)

```powershell
$RESOURCE_GROUP = "knowledge-hub-rg"
$LOCATION = "eastus"
$ENVIRONMENT = "dev"
$PROJECT_NAME = "ai-foundry-kb"
```

Or in CMD:
```cmd
set RESOURCE_GROUP=knowledge-hub-rg
set LOCATION=eastus
set ENVIRONMENT=dev
set PROJECT_NAME=ai-foundry-kb
```

### Step 2.2: Create Resource Group

```cmd
az group create --name %RESOURCE_GROUP% --location %LOCATION%
```

PowerShell:
```powershell
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### Step 2.3: Deploy Infrastructure

Navigate to infrastructure directory:
```cmd
cd infrastructure
```

Deploy using Bicep template:
```cmd
az deployment group create ^
  --resource-group %RESOURCE_GROUP% ^
  --template-file main.bicep ^
  --parameters parameters.json ^
  --parameters environment=%ENVIRONMENT% ^
  --output table
```

PowerShell version:
```powershell
az deployment group create `
  --resource-group $RESOURCE_GROUP `
  --template-file main.bicep `
  --parameters parameters.json `
  --parameters environment=$ENVIRONMENT `
  --output table
```

### Step 2.4: Capture Deployment Outputs

```cmd
az deployment group show ^
  --resource-group %RESOURCE_GROUP% ^
  --name main ^
  --query properties.outputs ^
  --output json > deployment-outputs.json
```

PowerShell:
```powershell
az deployment group show `
  --resource-group $RESOURCE_GROUP `
  --name main `
  --query properties.outputs `
  --output json | Out-File -FilePath deployment-outputs.json
```

---

## Phase 3: Local Application Setup

### Step 3.1: Create Python Virtual Environment

Navigate back to project root:
```cmd
cd ..
```

Create virtual environment:
```cmd
python -m venv venv
```

Activate virtual environment:
```cmd
:: CMD
venv\Scripts\activate.bat

:: PowerShell
venv\Scripts\Activate.ps1
```

**Note:** If you get an execution policy error in PowerShell, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3.2: Install Dependencies

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3.3: Configure Environment Variables

1. Copy the example environment file:
```cmd
copy .env.example .env
```

2. Edit `.env` file with deployment outputs:

Open `.env` in Notepad or your preferred editor:
```cmd
notepad .env
```

Update these values from `deployment-outputs.json`:
```env
# Azure Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=knowledge-hub-rg
AZURE_PROJECT_NAME=your-project-name

# Azure AI Foundry
AZURE_AI_PROJECT_CONNECTION_STRING=your-connection-string

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Azure AI Search (Optional)
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=your-search-key
AZURE_SEARCH_INDEX_NAME=knowledge-base

# Agent Configuration
AGENT_MODEL=gpt-4o
AGENT_TEMPERATURE=0.3
AGENT_MAX_TOKENS=4096
USE_FILE_SEARCH=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Phase 4: Initialize Agent and Upload Documents

### Step 4.1: Prepare Documentation

Create a `docs` folder with your documentation files:
```cmd
mkdir docs
```

Add your markdown, text, or PDF files to this folder.

### Step 4.2: Run Initialization Script

Create a Windows batch script for initialization:

**File: `initialize.bat`**
```batch
@echo off
echo Initializing Knowledge Hub Agent...
echo.

python -c "from src.agent import KnowledgeHubAgent, AgentConfig; import os; from dotenv import load_dotenv; load_dotenv(); config = AgentConfig(subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'), resource_group=os.getenv('AZURE_RESOURCE_GROUP'), project_name=os.getenv('AZURE_PROJECT_NAME')); agent = KnowledgeHubAgent(config); print('Creating vector store...'); agent.create_vector_store(); print('Vector store created!'); print('Creating agent...'); agent.create_agent(); print('Agent created successfully!');"

echo.
echo Initialization complete!
pause
```

Or use PowerShell script:

**File: `initialize.ps1`**
```powershell
Write-Host "Initializing Knowledge Hub Agent..." -ForegroundColor Green

python -c @"
from src.agent import KnowledgeHubAgent, AgentConfig
import os
from dotenv import load_dotenv

load_dotenv()

config = AgentConfig(
    subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'),
    resource_group=os.getenv('AZURE_RESOURCE_GROUP'),
    project_name=os.getenv('AZURE_PROJECT_NAME')
)

agent = KnowledgeHubAgent(config)

print('Creating vector store...')
agent.create_vector_store()
print('Vector store created!')

print('Creating agent...')
agent.create_agent()
print('Agent created successfully!')
"@

Write-Host "Initialization complete!" -ForegroundColor Green
```

Run the script:
```cmd
initialize.bat
```

Or:
```powershell
.\initialize.ps1
```

### Step 4.3: Upload Documents

Use the provided example script:
```cmd
python examples\upload_documents.py
```

Or create a custom upload script:

**File: `upload_docs.py`**
```python
from src.agent import KnowledgeHubAgent, AgentConfig
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Initialize agent
config = AgentConfig(
    subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'),
    resource_group=os.getenv('AZURE_RESOURCE_GROUP'),
    project_name=os.getenv('AZURE_PROJECT_NAME')
)

agent = KnowledgeHubAgent(config)

# Get all files from docs directory
docs_dir = Path("docs")
file_paths = [str(f) for f in docs_dir.glob("**/*") if f.is_file()]

print(f"Found {len(file_paths)} files to upload")

# Upload files
file_ids = agent.upload_files(file_paths, update_vector_store=True)

print(f"Successfully uploaded {len(file_ids)} files")
print("File IDs:", file_ids)
```

Run:
```cmd
python upload_docs.py
```

---

## Phase 5: Run the Application

### Step 5.1: Start the API Server

Using the Makefile equivalent:
```cmd
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Or create a run script:

**File: `run.bat`**
```batch
@echo off
echo Starting Knowledge Hub Agent API...
echo API will be available at http://localhost:8000
echo Documentation at http://localhost:8000/docs
echo.

python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Run:
```cmd
run.bat
```

### Step 5.2: Verify API is Running

Open browser and navigate to:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

Or test with PowerShell:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health
```

---

## Phase 6: Test the Agent

### Step 6.1: Test with Python Script

**File: `test_agent.py`**
```python
from src.agent import KnowledgeHubAgent, AgentConfig
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize
config = AgentConfig(
    subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'),
    resource_group=os.getenv('AZURE_RESOURCE_GROUP'),
    project_name=os.getenv('AZURE_PROJECT_NAME')
)

agent = KnowledgeHubAgent(config)

# Query the agent
print("Querying agent...")
response = agent.query("What is this product about?")
print("\nResponse:")
print(response)

# Multi-turn conversation
print("\n--- Starting conversation ---")
thread = agent.create_thread()
print(f"Created thread: {thread.id}")

agent.add_message(thread.id, "What are the main features?")
result = agent.run_agent(thread.id)
print("\nAgent:", result["messages"][0]["content"])

agent.add_message(thread.id, "How do I get started?")
result = agent.run_agent(thread.id)
print("\nAgent:", result["messages"][0]["content"])
```

Run:
```cmd
python test_agent.py
```

### Step 6.2: Test with REST API

Using PowerShell:
```powershell
# Create a thread
$createThreadResponse = Invoke-RestMethod -Uri http://localhost:8000/threads/create -Method Post
$threadId = $createThreadResponse.thread_id

# Query the agent
$body = @{
    question = "How do I use this product?"
    thread_id = $threadId
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/query -Method Post -Body $body -ContentType "application/json"
```

Using curl (if installed):
```cmd
curl -X POST http://localhost:8000/threads/create

curl -X POST http://localhost:8000/query ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"How do I use this product?\", \"thread_id\": \"thread_abc123\"}"
```

---

## Phase 7: Monitoring and Management

### Step 7.1: View Application Insights

1. Go to Azure Portal (https://portal.azure.com)
2. Navigate to your Resource Group
3. Open Application Insights resource
4. View metrics, logs, and traces

### Step 7.2: Query with Azure CLI

View agent service resources:
```cmd
az cognitiveservices account list ^
  --resource-group %RESOURCE_GROUP% ^
  --output table
```

View AI Search indexes:
```cmd
az search service list ^
  --resource-group %RESOURCE_GROUP% ^
  --output table
```

---

## Phase 8: Development Workflow (Windows)

### Step 8.1: Install Development Tools

```cmd
pip install -r requirements-dev.txt
```

Or manually:
```cmd
pip install pytest pytest-cov black flake8 mypy
```

### Step 8.2: Run Tests

```cmd
python -m pytest tests\ -v
```

With coverage:
```cmd
python -m pytest tests\ --cov=src --cov-report=html
```

### Step 8.3: Code Formatting

```cmd
python -m black src tests examples
```

### Step 8.4: Linting

```cmd
python -m flake8 src tests examples
python -m mypy src
```

---

## Common Windows Commands Reference

| Task | CMD | PowerShell |
|------|-----|------------|
| Change directory | `cd path\to\dir` | `cd path\to\dir` |
| Create directory | `mkdir dirname` | `New-Item -ItemType Directory -Path dirname` |
| Copy file | `copy source dest` | `Copy-Item source dest` |
| Delete file | `del filename` | `Remove-Item filename` |
| View file | `type filename` | `Get-Content filename` |
| Set variable | `set VAR=value` | `$VAR = "value"` |
| Run Python script | `python script.py` | `python script.py` |
| Activate venv | `venv\Scripts\activate.bat` | `venv\Scripts\Activate.ps1` |

---

## Troubleshooting

### Issue: Cannot run PowerShell scripts

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Azure CLI not found

**Solution:**
Add Azure CLI to PATH:
1. Open System Properties → Environment Variables
2. Add `C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin` to PATH

### Issue: Python not found

**Solution:**
Reinstall Python and check "Add Python to PATH" during installation.

### Issue: Module not found errors

**Solution:**
Ensure virtual environment is activated:
```cmd
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Issue: Azure authentication errors

**Solution:**
Re-login to Azure CLI:
```cmd
az login --use-device-code
```

---

## Quick Start Summary

For a quick setup, run these commands in order:

```cmd
:: 1. Navigate to project
cd C:\path\to\MyFirstRepo\02-work\ai-foundry-agent

:: 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate.bat

:: 3. Install dependencies
pip install -r requirements.txt

:: 4. Configure Azure (one-time)
az login
set RESOURCE_GROUP=knowledge-hub-rg
set LOCATION=eastus

:: 5. Deploy infrastructure
cd infrastructure
az deployment group create --resource-group %RESOURCE_GROUP% --template-file main.bicep --parameters parameters.json
cd ..

:: 6. Configure .env file
copy .env.example .env
:: Edit .env with your values

:: 7. Run the API
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Next Steps

1. ✅ Complete Azure infrastructure deployment
2. ✅ Configure local environment
3. ✅ Upload documentation to vector store
4. ✅ Test agent with sample queries
5. ✅ Integrate with your applications via REST API
6. 📊 Monitor performance in Application Insights
7. 🚀 Deploy to production (Azure Web App or Container Apps)

---

## Resources

- **Azure CLI Documentation**: https://learn.microsoft.com/cli/azure/
- **Python on Windows**: https://docs.python.org/3/using/windows.html
- **Azure AI Foundry**: https://learn.microsoft.com/azure/ai-studio/
- **Project README**: [README.md](./README.md)
- **Status**: [STATUS.md](./STATUS.md)

---

**Last Updated**: 2026-01-13
**Platform**: Windows 10/11
**Python Version**: 3.9+
**Azure CLI Version**: 2.50+
