# Quick Start Guide for Windows

This is a quick reference for getting started with the Azure AI Foundry Knowledge Hub Agent on Windows.

## Prerequisites Checklist

- [ ] Windows 10/11
- [ ] Azure CLI installed ✅ (You have this!)
- [ ] Python 3.9+ installed
- [ ] Azure subscription with appropriate permissions
- [ ] Git (optional, but recommended)

## Super Quick Start (5 Steps)

### 1. Setup Environment

Open Command Prompt or PowerShell in the project directory:

**CMD:**
```cmd
cd C:\path\to\MyFirstRepo\02-work\ai-foundry-agent
setup-windows.bat
```

**PowerShell:**
```powershell
cd C:\path\to\MyFirstRepo\02-work\ai-foundry-agent
.\setup-windows.ps1
```

### 2. Deploy Azure Infrastructure

**CMD:**
```cmd
deploy-infrastructure.bat
```

**PowerShell:**
```powershell
.\deploy-infrastructure.ps1
```

⏱️ *This takes 10-15 minutes*

### 3. Configure Environment

Edit `.env` file with values from `infrastructure\deployment-outputs.json`:

```cmd
notepad .env
```

Key values to update:
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `AZURE_PROJECT_NAME`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`

### 4. Initialize Agent

**CMD:**
```cmd
initialize-agent.bat
```

**PowerShell:**
```powershell
.\initialize-agent.ps1
```

### 5. Start API Server

**CMD:**
```cmd
run.bat
```

**PowerShell:**
```powershell
.\run.ps1
```

**🎉 Done!** API is running at http://localhost:8000

## Test Your Agent

### Option 1: Browser
Open http://localhost:8000/docs and try the interactive API.

### Option 2: Command Line

**CMD:**
```cmd
test-agent.bat
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
```

### Option 3: Python Script

```python
# test.py
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
response = agent.query("What can you help me with?")
print(response)
```

Run:
```cmd
python test.py
```

## Upload Your Documentation

1. Add files to `docs\` folder
2. Run upload script:

**CMD:**
```cmd
python examples\upload_documents.py
```

**PowerShell:**
```powershell
python examples\upload_documents.py
```

## Available Scripts

| Script | Purpose |
|--------|---------|
| `setup-windows.bat` / `.ps1` | Initial environment setup |
| `deploy-infrastructure.bat` / `.ps1` | Deploy Azure resources |
| `initialize-agent.bat` / `.ps1` | Create agent and vector store |
| `run.bat` / `.ps1` | Start API server |
| `test-agent.bat` / `.ps1` | Test agent with sample query |

## Common Tasks

### Check Azure Login
```cmd
az account show
```

### View Resource Group
```cmd
az group show --name knowledge-hub-rg
```

### View Logs (if deployed to Azure)
```cmd
az webapp log tail --name your-app-name --resource-group knowledge-hub-rg
```

### Restart API Server
Press `Ctrl+C` in the terminal running the server, then run `run.bat` or `.\run.ps1` again.

## Troubleshooting

### "Python not found"
- Install Python 3.9+ from https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

### "az is not recognized"
- Azure CLI is not in PATH
- Add `C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin` to PATH
- Or reinstall Azure CLI

### "Cannot run scripts" (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Module not found"
Activate virtual environment:
```cmd
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### "Azure authentication failed"
```cmd
az logout
az login
```

## Project Structure

```
02-work/ai-foundry-agent/
├── src/
│   ├── agent/              # Agent implementation
│   ├── api/                # REST API
│   └── vector-store/       # Vector store & RAG
├── infrastructure/         # Azure Bicep templates
├── examples/               # Example scripts
├── docs/                   # Your documentation (add here)
├── tests/                  # Unit tests
├── .env                    # Configuration (create from .env.example)
└── *.bat, *.ps1           # Windows helper scripts
```

## Next Steps

1. ✅ Upload your product documentation
2. ✅ Test with real queries
3. ✅ Integrate with your application via REST API
4. 📊 Monitor in Azure Portal → Application Insights
5. 🚀 Deploy to production (Azure Web App)

## Get Help

- **Full Documentation**: [WINDOWS-EXECUTION-PLAN.md](./WINDOWS-EXECUTION-PLAN.md)
- **Project README**: [README.md](./README.md)
- **Azure CLI Docs**: https://learn.microsoft.com/cli/azure/
- **Azure AI Foundry**: https://learn.microsoft.com/azure/ai-studio/

---

**Quick Commands Reference:**

```cmd
# Setup (one-time)
setup-windows.bat

# Deploy (one-time)
deploy-infrastructure.bat

# Initialize (one-time)
initialize-agent.bat

# Run (every time)
run.bat

# Test
test-agent.bat
```

Happy coding! 🚀
