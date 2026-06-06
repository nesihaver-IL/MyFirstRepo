# Windows Scripts Guide

This document explains all the Windows helper scripts available for the Azure AI Foundry Knowledge Hub Agent project.

## Available Scripts

### Setup & Installation

#### `setup-windows.bat` / `setup-windows.ps1`
**Purpose:** Initial one-time setup of your local development environment

**What it does:**
- ✅ Checks Python installation
- ✅ Checks Azure CLI installation
- ✅ Creates Python virtual environment
- ✅ Installs all dependencies
- ✅ Creates `.env` file from template

**When to use:** Run this first before anything else

**Usage:**
```cmd
setup-windows.bat
```
or
```powershell
.\setup-windows.ps1
```

---

### Azure Deployment

#### `deploy-infrastructure.bat` / `deploy-infrastructure.ps1`
**Purpose:** Deploy Azure infrastructure resources

**What it does:**
- ✅ Authenticates with Azure
- ✅ Creates resource group
- ✅ Deploys Bicep template (AI Foundry, OpenAI, Search, etc.)
- ✅ Saves deployment outputs to JSON file

**When to use:** After setup, to create Azure resources (one-time, ~10-15 minutes)

**Configuration:**
Edit these variables at the top of the script:
```batch
set RESOURCE_GROUP=knowledge-hub-rg
set LOCATION=eastus
set ENVIRONMENT=dev
```

**Usage:**
```cmd
deploy-infrastructure.bat
```
or
```powershell
.\deploy-infrastructure.ps1
```

---

### Agent Initialization

#### `initialize-agent.bat` / `initialize-agent.ps1`
**Purpose:** Create the AI agent and vector store in Azure

**What it does:**
- ✅ Creates vector store for document storage
- ✅ Creates AI agent with file search capability

**When to use:** After infrastructure deployment and `.env` configuration (one-time)

**Prerequisites:**
- Infrastructure deployed
- `.env` file configured with Azure details

**Usage:**
```cmd
initialize-agent.bat
```
or
```powershell
.\initialize-agent.ps1
```

---

### Running the Application

#### `run.bat` / `run.ps1`
**Purpose:** Start the FastAPI server locally

**What it does:**
- ✅ Activates virtual environment
- ✅ Starts API server on port 8000
- ✅ Enables auto-reload for development

**When to use:** Every time you want to run the API server

**Access points:**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

**Usage:**
```cmd
run.bat
```
or
```powershell
.\run.ps1
```

**Stop:** Press `Ctrl+C` in the terminal

---

### Testing

#### `test-agent.bat` / `test-agent.ps1`
**Purpose:** Quick test of the agent with a sample query

**What it does:**
- ✅ Runs a test query against your agent
- ✅ Displays the response

**When to use:** To verify your agent is working correctly

**Usage:**
```cmd
test-agent.bat
```
or
```powershell
.\test-agent.ps1
```

---

## Script Execution Order

For a fresh setup, run scripts in this order:

```
1. setup-windows.bat          ← Install dependencies
2. deploy-infrastructure.bat  ← Create Azure resources
3. (Edit .env file)          ← Configure with Azure details
4. initialize-agent.bat      ← Create agent & vector store
5. (Add docs to docs/)       ← Add your documentation
6. run.bat                   ← Start the API server
7. test-agent.bat           ← Verify it works
```

## CMD vs PowerShell

Each script has two versions:

| Version | Extension | Shell | Features |
|---------|-----------|-------|----------|
| CMD | `.bat` | Command Prompt | Universal, older syntax |
| PowerShell | `.ps1` | PowerShell | Modern, colored output |

**Which to use?**
- Use `.bat` for maximum compatibility
- Use `.ps1` for better user experience (colors, formatting)

## PowerShell Execution Policy

If you get an error running `.ps1` scripts:

```
File cannot be loaded because running scripts is disabled on this system.
```

**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This is safe and only affects your user account.

## Script Customization

### Changing Azure Region

Edit `deploy-infrastructure.bat` or `.ps1`:
```batch
set LOCATION=westus2
```

### Changing Resource Group Name

Edit `deploy-infrastructure.bat` or `.ps1`:
```batch
set RESOURCE_GROUP=my-custom-rg
```

### Changing API Port

Edit `run.bat` or `.ps1`:
```batch
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 9000 --reload
```

## Troubleshooting Scripts

### Script doesn't run
**CMD:**
- Make sure you're in the correct directory
- Run: `dir` to see if the `.bat` file is there

**PowerShell:**
- Check execution policy (see above)
- Run: `ls` to see if the `.ps1` file is there

### "Command not found" errors

| Error | Solution |
|-------|----------|
| `python is not recognized` | Install Python 3.9+, add to PATH |
| `az is not recognized` | Install Azure CLI, add to PATH |
| `pip is not recognized` | Run: `python -m pip install ...` instead |

### Virtual environment not activating

**CMD:**
```cmd
venv\Scripts\activate.bat
```

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

If still issues, delete `venv` folder and run `setup-windows.bat` again.

### Azure authentication fails

```cmd
az logout
az login --use-device-code
```

Or use:
```cmd
az login --tenant your-tenant-id
```

## Manual Alternatives

If scripts don't work, you can run commands manually:

### Setup
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
```

### Deploy
```cmd
az login
az group create --name knowledge-hub-rg --location eastus
cd infrastructure
az deployment group create --resource-group knowledge-hub-rg --template-file main.bicep --parameters parameters.json
cd ..
```

### Run
```cmd
venv\Scripts\activate.bat
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Advanced Usage

### Background Execution (PowerShell)

Run API in background:
```powershell
Start-Job -ScriptBlock { python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 }
```

Check status:
```powershell
Get-Job
```

Stop:
```powershell
Stop-Job -Name Job1
```

### Scheduled Tasks (Windows)

Create a scheduled task to start the API on boot:
```cmd
schtasks /create /tn "AI Agent API" /tr "C:\path\to\run.bat" /sc onstart /ru SYSTEM
```

### Multiple Environments

Create environment-specific scripts:
- `deploy-infrastructure-dev.bat`
- `deploy-infrastructure-prod.bat`

Each with different configuration.

## Script Maintenance

### Updating Scripts

Scripts are version-controlled. To get latest:
```cmd
git pull origin claude/update-azure-cli-plan-FkT2S
```

### Custom Scripts

Create your own scripts in the same directory:

**my-custom-script.bat:**
```batch
@echo off
call venv\Scripts\activate.bat
python my_script.py
pause
```

## Best Practices

1. ✅ **Always activate virtual environment** before running Python commands
2. ✅ **Keep `.env` secure** - never commit it to git
3. ✅ **Run scripts from project root** directory
4. ✅ **Check Azure costs** regularly when resources are deployed
5. ✅ **Use descriptive resource group names** for easy identification

## Getting Help

- **Full Plan:** [WINDOWS-EXECUTION-PLAN.md](./WINDOWS-EXECUTION-PLAN.md)
- **Quick Start:** [QUICKSTART-WINDOWS.md](./QUICKSTART-WINDOWS.md)
- **Project README:** [README.md](./README.md)

## Script Reference Summary

| Script | One-Time? | Duration | Requires Internet |
|--------|-----------|----------|-------------------|
| `setup-windows` | ✅ Yes | 2-5 min | Yes (pip packages) |
| `deploy-infrastructure` | ✅ Yes | 10-15 min | Yes (Azure) |
| `initialize-agent` | ✅ Yes | 1-2 min | Yes (Azure) |
| `run` | ❌ No | Ongoing | No (local) |
| `test-agent` | ❌ No | 10-30 sec | Yes (Azure) |

---

**Last Updated:** 2026-01-13

Need more help? Check the troubleshooting section in [WINDOWS-EXECUTION-PLAN.md](./WINDOWS-EXECUTION-PLAN.md)
