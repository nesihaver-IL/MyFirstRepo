# Guided Setup Checklist - Windows

Follow this checklist step-by-step. Report back after each step with the results!

## Pre-Flight Checks

### ☑️ Step 0.1: Verify Prerequisites

Open **Command Prompt** or **PowerShell** and run:

```cmd
python --version
```
**Expected:** `Python 3.9.x` or higher
**Your result:** _________

```cmd
az --version
```
**Expected:** Shows Azure CLI version
**Your result:** _________

```cmd
az account show
```
**Expected:** Shows your Azure account details (or prompts login)
**Your result:** _________

---

## Phase 1: Environment Setup

### ☑️ Step 1.1: Navigate to Project Directory

```cmd
cd C:\Users\YourUsername\path\to\MyFirstRepo\02-work\ai-foundry-agent
```

Verify you're in the right place:
```cmd
dir
```

**Expected:** You should see files like `README.md`, `requirements.txt`, `setup.py`, etc.
**Your result:** _________

### ☑️ Step 1.2: Run Setup Script

**Option A - Command Prompt:**
```cmd
setup-windows.bat
```

**Option B - PowerShell:**
```powershell
.\setup-windows.ps1
```

**Expected output:**
- ✅ Python is installed
- ✅ Azure CLI is installed
- Creating virtual environment...
- Installing dependencies...
- Setup Complete!

**Your result:** _________

**⚠️ Common Issues:**
- If PowerShell script won't run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- If Python not found: Reinstall Python and check "Add to PATH"

---

## Phase 2: Configure Azure Settings

### ☑️ Step 2.1: Check Azure Login

```cmd
az login
```

**Expected:** Browser opens, you login, see "You have logged in."
**Your result:** _________

### ☑️ Step 2.2: Verify Subscription

```cmd
az account show
```

Copy your subscription ID from the output.
**Your subscription ID:** _________

---

## Phase 3: Deploy Azure Infrastructure

### ☑️ Step 3.1: Set Configuration Variables

**Command Prompt:**
```cmd
set RESOURCE_GROUP=knowledge-hub-rg
set LOCATION=eastus
set ENVIRONMENT=dev
```

**PowerShell:**
```powershell
$RESOURCE_GROUP = "knowledge-hub-rg"
$LOCATION = "eastus"
$ENVIRONMENT = "dev"
```

**Your result:** (Just type "Done" when complete) _________

### ☑️ Step 3.2: Run Deployment Script

**Option A - Command Prompt:**
```cmd
deploy-infrastructure.bat
```

**Option B - PowerShell:**
```powershell
.\deploy-infrastructure.ps1
```

**Expected:**
- Creating resource group...
- Deploying infrastructure (10-15 minutes)...
- Deployment Complete!

**⏱️ This step takes 10-15 minutes. Go grab a coffee! ☕**

**Your result:** _________

**⚠️ If deployment fails:**
- Check if you have sufficient Azure permissions
- Verify subscription has required resource providers registered
- Check Azure region supports all services

### ☑️ Step 3.3: Check Deployment Outputs

```cmd
type infrastructure\deployment-outputs.json
```

**PowerShell:**
```powershell
Get-Content infrastructure\deployment-outputs.json
```

**Expected:** JSON file with Azure resource details
**Your result:** (Copy the JSON output) _________

---

## Phase 4: Configure Environment File

### ☑️ Step 4.1: Edit .env File

Open the `.env` file:
```cmd
notepad .env
```

### ☑️ Step 4.2: Update These Values

From your `deployment-outputs.json`, update:

```env
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_RESOURCE_GROUP=knowledge-hub-rg
AZURE_PROJECT_NAME=<from-outputs>
AZURE_OPENAI_ENDPOINT=<from-outputs>
AZURE_OPENAI_API_KEY=<from-outputs>
AZURE_SEARCH_ENDPOINT=<from-outputs>
AZURE_SEARCH_KEY=<from-outputs>
```

**Your result:** (Type "Done" when saved) _________

---

## Phase 5: Initialize Agent

### ☑️ Step 5.1: Run Initialization Script

```cmd
initialize-agent.bat
```

**PowerShell:**
```powershell
.\initialize-agent.ps1
```

**Expected output:**
- Creating vector store...
- Vector store created!
- Creating agent...
- Agent created successfully!

**Your result:** _________

**⚠️ If this fails:**
- Double-check your `.env` file values
- Verify Azure resources were created (check Azure Portal)
- Ensure you have proper RBAC permissions

---

## Phase 6: Start the API Server

### ☑️ Step 6.1: Run the Server

**Command Prompt:**
```cmd
run.bat
```

**PowerShell:**
```powershell
.\run.ps1
```

**Expected output:**
```
Starting Knowledge Hub Agent API
API will be available at:
  - Main: http://localhost:8000
  - Docs: http://localhost:8000/docs
  - Health: http://localhost:8000/health

INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Your result:** _________

**⚠️ Keep this terminal window open! The server needs to keep running.**

---

## Phase 7: Test the Agent

### ☑️ Step 7.1: Open a NEW Terminal Window

Keep the API server running in the first window, open a new Command Prompt or PowerShell.

### ☑️ Step 7.2: Test Health Check

```cmd
curl http://localhost:8000/health
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
```

**Expected:** `{"status":"healthy"}` or similar
**Your result:** _________

### ☑️ Step 7.3: Test in Browser

Open your web browser and navigate to:
```
http://localhost:8000/docs
```

**Expected:** Interactive API documentation (Swagger UI)
**Your result:** _________

### ☑️ Step 7.4: Run Test Script

In your NEW terminal (navigate to project directory first):

```cmd
cd C:\Users\YourUsername\path\to\MyFirstRepo\02-work\ai-foundry-agent
test-agent.bat
```

**Expected:** Agent responds to a test query
**Your result:** _________

---

## Phase 8: Upload Documents (Optional)

### ☑️ Step 8.1: Add Documents

1. Create or add files to the `docs` folder:
```cmd
mkdir docs
```

2. Copy your documentation files (PDF, MD, TXT) into `docs\`

**Your result:** _________

### ☑️ Step 8.2: Upload to Vector Store

```cmd
python examples\upload_documents.py
```

**Expected:** "Successfully uploaded X files"
**Your result:** _________

---

## 🎉 Success Checklist

Mark these as you complete them:

- [ ] Python and Azure CLI verified
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Azure infrastructure deployed
- [ ] .env file configured
- [ ] Agent and vector store created
- [ ] API server running
- [ ] Health check passing
- [ ] Browser docs accessible
- [ ] Test query successful
- [ ] Documents uploaded (optional)

---

## 📊 Final Verification

Your API should now be running at `http://localhost:8000`

Try this final test in browser or Postman:

**POST** `http://localhost:8000/query`
```json
{
  "question": "What can you help me with?"
}
```

**Expected:** Agent response with information
**Your result:** _________

---

## ❓ Troubleshooting Contact Points

**When you encounter an issue, provide:**
1. Which step you're on
2. The exact command you ran
3. The complete error message
4. Screenshot if helpful

I'm here to help at every step! 🚀

---

## Next Session Commands

**To restart API server later:**
1. Open Command Prompt/PowerShell
2. Navigate to project: `cd C:\Users\...\ai-foundry-agent`
3. Run: `run.bat` or `.\run.ps1`

**To stop API server:**
- Press `Ctrl+C` in the terminal where it's running

---

**Ready to begin? Start with Step 0.1 and report back with your results!**
