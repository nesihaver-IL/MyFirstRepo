# Troubleshooting Guide

This guide provides solutions to common issues you may encounter when deploying, configuring, or operating the Knowledge Hub Agent.

## Table of Contents

- [Deployment Issues](#deployment-issues)
- [Configuration Issues](#configuration-issues)
- [Authentication Issues](#authentication-issues)
- [File Upload Issues](#file-upload-issues)
- [Agent Query Issues](#agent-query-issues)
- [Performance Issues](#performance-issues)
- [API Server Issues](#api-server-issues)
- [Vector Store Issues](#vector-store-issues)
- [Monitoring & Logging](#monitoring--logging)

---

## Deployment Issues

### Issue: Bicep Deployment Fails

**Symptom**: `az deployment group create` command fails with validation errors

**Common Causes**:

1. **Resource name conflicts** (names must be globally unique)

   ```bash
   # Error: "The storage account name 'knowledgehubstorage' is already taken"
   ```

   **Solution**: Change the `projectName` parameter to something unique
   ```bash
   az deployment group create \
     --resource-group knowledge-hub-rg \
     --template-file main.bicep \
     --parameters projectName="mycompany-kb-prod"  # Use unique prefix
   ```

2. **Region doesn't support required services**

   **Solution**: Check service availability and use supported regions
   ```bash
   # Check Azure OpenAI availability
   az cognitiveservices account list-skus \
     --location eastus \
     --query "[?name=='S0' && kind=='OpenAI']"

   # Use regions: eastus, westus2, northeurope, westeurope
   ```

3. **Insufficient permissions**

   **Solution**: Ensure you have Contributor role
   ```bash
   # Check your role assignments
   az role assignment list \
     --assignee $(az account show --query user.name -o tsv) \
     --query "[].{Role:roleDefinitionName, Scope:scope}"
   ```

4. **Quota limits exceeded**

   ```bash
   # Error: "Operation could not be completed as it results in exceeding quota limits"
   ```

   **Solution**: Request quota increase or delete unused resources
   ```bash
   # Check current usage
   az vm list-usage --location eastus --output table

   # Request quota increase via Azure Portal
   ```

### Issue: Deployment Takes Too Long

**Symptom**: Deployment running for >30 minutes

**Possible Causes**:
- Resource creation is waiting for dependencies
- Network issues
- Azure service slowdown

**Solution**:

1. **Check deployment status**:
   ```bash
   az deployment group show \
     --resource-group knowledge-hub-rg \
     --name main-deployment \
     --query properties.provisioningState
   ```

2. **View deployment operations**:
   ```bash
   az deployment operation group list \
     --resource-group knowledge-hub-rg \
     --name main-deployment \
     --query "[].{Resource:properties.targetResource.resourceName, State:properties.provisioningState, Status:properties.statusMessage}"
   ```

3. **If stuck, cancel and retry**:
   ```bash
   # Cancel deployment
   az deployment group cancel \
     --resource-group knowledge-hub-rg \
     --name main-deployment

   # Clean up and retry
   az group delete --name knowledge-hub-rg --yes
   az group create --name knowledge-hub-rg --location eastus
   # Re-run deployment
   ```

### Issue: Resource Not Found After Deployment

**Symptom**: Deployment succeeds but resources can't be found

**Solution**:

1. **List all resources**:
   ```bash
   az resource list \
     --resource-group knowledge-hub-rg \
     --output table
   ```

2. **Check specific resource**:
   ```bash
   # Check AI Foundry Project
   az ml workspace show \
     --name your-project-name \
     --resource-group knowledge-hub-rg

   # Check Azure OpenAI
   az cognitiveservices account show \
     --name your-openai-name \
     --resource-group knowledge-hub-rg
   ```

3. **Verify deployment outputs**:
   ```bash
   az deployment group show \
     --resource-group knowledge-hub-rg \
     --name main-deployment \
     --query properties.outputs
   ```

---

## Configuration Issues

### Issue: Invalid Configuration Variables

**Symptom**: Application fails to start with configuration errors

**Common Errors**:

1. **Missing required variables**

   ```
   ERROR: AZURE_SUBSCRIPTION_ID environment variable is required
   ```

   **Solution**: Ensure all required variables are set in `.env`
   ```bash
   # Check .env file
   cat .env | grep -E "AZURE_SUBSCRIPTION_ID|AZURE_RESOURCE_GROUP|AZURE_PROJECT_NAME"

   # Verify no placeholder values remain
   # Bad: AZURE_PROJECT_NAME="<from-deployment-output>"
   # Good: AZURE_PROJECT_NAME="knowledge-hub-dev-project"
   ```

2. **Incorrect format**

   **Solution**: Verify format matches requirements
   ```ini
   # Correct format (.env file)
   AZURE_SUBSCRIPTION_ID="12345678-1234-1234-1234-123456789abc"  # UUID format
   AZURE_RESOURCE_GROUP="knowledge-hub-rg"  # String
   AGENT_TEMPERATURE="0.3"  # Float as string
   API_PORT="8000"  # Integer as string
   ```

3. **Special characters in values**

   **Solution**: Quote values with special characters
   ```ini
   # If password contains special chars
   DATABASE_PASSWORD="P@ssw0rd!123"  # Quoted
   ```

### Issue: Configuration Validation Script Fails

**Symptom**: `python scripts/validate_config.py` reports errors

**Solution**:

Create and run a validation script:

```python
# scripts/validate_config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Required variables
required = {
    'AZURE_SUBSCRIPTION_ID': 'UUID format (12345678-1234-...)',
    'AZURE_RESOURCE_GROUP': 'Resource group name',
    'AZURE_PROJECT_NAME': 'AI Foundry project name'
}

errors = []
warnings = []

for var, desc in required.items():
    value = os.getenv(var)
    if not value:
        errors.append(f"❌ {var} is not set ({desc})")
    elif value.startswith('<') or value == '':
        errors.append(f"❌ {var} has placeholder value: {value}")

# Optional but recommended
optional = ['AGENT_MODEL', 'AGENT_TEMPERATURE', 'USE_FILE_SEARCH']
for var in optional:
    if not os.getenv(var):
        warnings.append(f"⚠️  {var} not set (will use default)")

if errors:
    print("\n".join(errors))
    exit(1)
elif warnings:
    print("\n".join(warnings))
    print("\n✅ Configuration valid (with warnings)")
else:
    print("✅ Configuration valid")
```

---

## Authentication Issues

### Issue: Azure Authentication Fails

**Symptom**: `AuthenticationError`, `DefaultAzureCredential failed to retrieve a token`

**Common Causes**:

1. **Not logged in to Azure CLI**

   **Solution**:
   ```bash
   # Login
   az login

   # Verify login
   az account show

   # If multiple tenants, specify tenant
   az login --tenant your-tenant-id
   ```

2. **Wrong subscription selected**

   **Solution**:
   ```bash
   # List subscriptions
   az account list --output table

   # Set correct subscription
   az account set --subscription "your-subscription-id"

   # Verify
   az account show
   ```

3. **Expired token**

   **Solution**:
   ```bash
   # Clear cached credentials
   rm -rf ~/.azure/

   # Re-login
   az login
   ```

4. **Insufficient permissions**

   **Solution**:
   ```bash
   # Check permissions
   az role assignment list \
     --assignee $(az account show --query user.name -o tsv) \
     --scope /subscriptions/your-sub-id
   ```

   Required roles:
   - Contributor (for resource management)
   - Cognitive Services Contributor (for Azure OpenAI)

5. **Managed Identity not configured** (Azure-hosted scenarios)

   **Solution**:
   ```bash
   # Enable system-assigned managed identity
   az webapp identity assign \
     --name your-webapp \
     --resource-group knowledge-hub-rg

   # Grant permissions to managed identity
   az role assignment create \
     --assignee $(az webapp identity show --name your-webapp --resource-group knowledge-hub-rg --query principalId -o tsv) \
     --role "Cognitive Services User" \
     --scope /subscriptions/your-sub-id/resourceGroups/knowledge-hub-rg
   ```

### Issue: API Key Authentication Fails

**Symptom**: 401 Unauthorized errors when calling Azure services

**Solution**:

1. **Retrieve API keys**:
   ```bash
   # Azure OpenAI key
   az cognitiveservices account keys list \
     --name your-openai-name \
     --resource-group knowledge-hub-rg

   # Azure AI Search key
   az search admin-key show \
     --service-name your-search-name \
     --resource-group knowledge-hub-rg
   ```

2. **Update configuration** with actual keys:
   ```ini
   # .env
   AZURE_OPENAI_API_KEY="your-actual-key-here"
   AZURE_SEARCH_API_KEY="your-actual-key-here"
   ```

---

## File Upload Issues

### Issue: File Upload Fails

**Symptom**: Error during `agent.upload_files()`

**Common Causes**:

1. **File doesn't exist**

   ```python
   FileNotFoundError: [Errno 2] No such file or directory: 'docs/guide.md'
   ```

   **Solution**: Verify file paths
   ```python
   from pathlib import Path

   file_paths = ["docs/guide.md"]
   for path in file_paths:
       if not Path(path).exists():
           print(f"❌ File not found: {path}")
       else:
           print(f"✅ Found: {path}")
   ```

2. **File too large** (>512 MB)

   **Solution**: Check file sizes
   ```python
   import os

   for file_path in file_paths:
       size_mb = os.path.getsize(file_path) / (1024 * 1024)
       print(f"{file_path}: {size_mb:.2f} MB")
       if size_mb > 512:
           print(f"  ❌ File exceeds 512 MB limit")
   ```

   Split large files if needed.

3. **Unsupported file format**

   **Solution**: Check file extensions
   ```python
   supported = ['.md', '.txt', '.pdf', '.html', '.docx']

   for path in file_paths:
       ext = Path(path).suffix.lower()
       if ext not in supported:
           print(f"❌ Unsupported format: {path} ({ext})")
   ```

4. **Azure OpenAI quota exceeded**

   **Solution**: Check and increase quota
   ```bash
   # Check usage
   az cognitiveservices account list-usage \
     --name your-openai-name \
     --resource-group knowledge-hub-rg

   # Request quota increase via Azure Portal
   # Portal → Azure OpenAI → Quotas → Request Increase
   ```

5. **Network timeout**

   **Solution**: Upload in smaller batches
   ```python
   # Upload in batches of 10 files
   batch_size = 10
   for i in range(0, len(file_paths), batch_size):
       batch = file_paths[i:i+batch_size]
       try:
           file_ids = agent.upload_files(batch, update_vector_store=True)
           print(f"✅ Uploaded batch {i//batch_size + 1}: {len(file_ids)} files")
       except Exception as e:
           print(f"❌ Batch {i//batch_size + 1} failed: {e}")
   ```

### Issue: Files Uploaded But Not Searchable

**Symptom**: Files show as uploaded but agent can't find information

**Solution**:

1. **Check indexing status**:
   ```python
   vector_store = agent.vector_store
   print(f"Total: {vector_store.file_counts.total}")
   print(f"Completed: {vector_store.file_counts.completed}")
   print(f"In Progress: {vector_store.file_counts.in_progress}")
   print(f"Failed: {vector_store.file_counts.failed}")
   ```

   Wait for `in_progress` to reach 0.

2. **Check for failed files**:
   ```python
   # List files in vector store
   files = agent.client.agents.list_vector_store_files(
       vector_store_id=vector_store.id
   )

   for file in files.data:
       if file.status == "failed":
           print(f"❌ Failed: {file.id} - {file.last_error}")
   ```

3. **Recreate agent** after indexing completes:
   ```python
   # Wait for indexing
   import time
   while vector_store.file_counts.in_progress > 0:
       print(f"Indexing... ({vector_store.file_counts.in_progress} remaining)")
       time.sleep(10)
       vector_store = agent.client.agents.get_vector_store(vector_store.id)

   # Recreate agent
   agent.create_agent()
   ```

---

## Agent Query Issues

### Issue: Poor or Irrelevant Answers

**Symptom**: Agent returns answers that don't match the documentation

**Common Causes**:

1. **Documents not properly indexed**

   **Solution**: Verify upload and indexing
   ```python
   # Check vector store status
   vs = agent.vector_store
   if vs.file_counts.failed > 0:
       print(f"❌ {vs.file_counts.failed} files failed to index")
   if vs.file_counts.in_progress > 0:
       print(f"⏳ {vs.file_counts.in_progress} files still indexing")
   ```

2. **Query too vague**

   **Bad**: "How does it work?"
   **Good**: "How do I configure OAuth 2.0 authentication?"

   **Solution**: Encourage specific questions with context.

3. **Temperature too high** (more creative but less accurate)

   **Solution**: Lower temperature for more focused answers
   ```python
   config = AgentConfig(
       ...
       temperature=0.1  # Lower = more deterministic (0.0-2.0)
   )
   ```

4. **Chunk size too small/large**

   **Solution**: Adjust chunking strategy
   ```python
   from src.vector_store import DocumentProcessor

   # Experiment with different sizes
   processor = DocumentProcessor(
       chunk_size=1500,   # Try 800-2000
       chunk_overlap=300  # Try 100-400
   )
   ```

5. **Agent instructions not specific enough**

   **Solution**: Customize agent instructions
   ```python
   config = AgentConfig(
       ...
       instructions=(
           "You are a technical support assistant for [Product Name]. "
           "Always cite the documentation source when providing answers. "
           "If you cannot find the answer in the documentation, clearly state that. "
           "Focus on providing accurate, step-by-step instructions."
       )
   )
   ```

### Issue: Agent Returns "I Don't Know"

**Symptom**: Agent can't answer questions despite documentation being uploaded

**Solution**:

1. **Test with simple question**:
   ```python
   # Test if agent can access documents
   response = agent.query("What topics are covered in the documentation?")
   print(response)
   ```

2. **Check file search tool is enabled**:
   ```python
   # Verify agent configuration
   agent_info = agent.client.agents.get_agent(agent.agent.id)
   print(f"Tools: {[tool.type for tool in agent_info.tools]}")
   # Should include: 'file_search'
   ```

3. **Verify vector store is attached**:
   ```python
   print(f"Tool Resources: {agent.agent.tool_resources}")
   # Should show vector_store_ids
   ```

4. **Try different phrasing**:
   ```python
   questions = [
       "How do I configure authentication?",
       "What are the authentication options?",
       "Tell me about authentication setup",
       "Show me authentication documentation"
   ]

   for q in questions:
       response = agent.query(q)
       print(f"Q: {q}\nA: {response[:200]}...\n")
   ```

### Issue: Agent Provides Outdated Information

**Symptom**: Agent returns information from old documentation

**Solution**:

1. **Delete old files**:
   ```python
   # List files in vector store
   files = agent.client.agents.list_vector_store_files(
       vector_store_id=agent.vector_store.id
   )

   # Delete specific files
   for file in files.data:
       if "old" in file.id or file.created_at < cutoff_date:
           agent.client.agents.delete_vector_store_file(
               vector_store_id=agent.vector_store.id,
               file_id=file.id
           )
   ```

2. **Upload updated documentation**:
   ```python
   # Upload new versions
   agent.upload_files([
       "docs/updated-guide-v2.md"
   ], update_vector_store=True)
   ```

3. **Create fresh vector store** (for major updates):
   ```python
   # Create new vector store
   new_vs = agent.create_vector_store()

   # Upload all current docs
   agent.upload_files(current_doc_list, update_vector_store=True)

   # Recreate agent with new vector store
   agent.create_agent()
   ```

---

## Performance Issues

### Issue: Slow Response Times

**Symptom**: Queries taking >10 seconds to complete

**Common Causes**:

1. **Azure OpenAI throttling** (429 errors)

   **Solution**: Check Application Insights for throttling
   ```kusto
   // Application Insights Query
   requests
   | where resultCode == 429
   | summarize count() by bin(timestamp, 5m)
   ```

   Increase quota or implement retry logic.

2. **Large vector store** (>10,000 files)

   **Solution**: Optimize vector store
   ```python
   # Check size
   vs = agent.vector_store
   print(f"Total files: {vs.file_counts.total}")

   # If too large, split by category
   # Create separate vector stores for different doc types
   ```

3. **Network latency**

   **Solution**: Test latency
   ```bash
   # Test latency to Azure endpoint
   ping your-openai-endpoint.openai.azure.com

   # Consider deploying in same region as users
   ```

4. **App Service tier too low** (Basic tier)

   **Solution**: Upgrade App Service plan
   ```bash
   # Check current tier
   az appservice plan show \
     --name your-app-plan \
     --resource-group knowledge-hub-rg \
     --query sku.name

   # Upgrade to Standard or Premium
   az appservice plan update \
     --name your-app-plan \
     --resource-group knowledge-hub-rg \
     --sku S1  # or P1V2
   ```

5. **Cold start** (first request after idle)

   **Solution**: Enable Always On
   ```bash
   az webapp config set \
     --name your-webapp \
     --resource-group knowledge-hub-rg \
     --always-on true
   ```

### Issue: High Memory Usage

**Symptom**: App Service running out of memory

**Solution**:

1. **Monitor memory**:
   ```bash
   # View metrics
   az monitor metrics list \
     --resource $(az webapp show --name your-webapp --resource-group knowledge-hub-rg --query id -o tsv) \
     --metric "MemoryWorkingSet"
   ```

2. **Optimize code**:
   ```python
   # Clear thread history periodically
   # Don't keep all threads in memory

   # Limit batch sizes
   batch_size = 10  # Instead of 100
   ```

3. **Upgrade tier**:
   ```bash
   # Upgrade to tier with more memory
   az appservice plan update \
     --name your-app-plan \
     --resource-group knowledge-hub-rg \
     --sku P1V2  # 3.5 GB RAM
   ```

---

## API Server Issues

### Issue: Server Won't Start

**Symptom**: `make run` fails or server exits immediately

**Common Causes**:

1. **Port already in use**

   ```
   Error: [Errno 48] Address already in use
   ```

   **Solution**:
   ```bash
   # Find process using port 8000
   lsof -i :8000

   # Kill the process
   kill -9 <PID>

   # Or use different port
   export API_PORT=8001
   make run
   ```

2. **Missing dependencies**

   **Solution**:
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt

   # Verify key packages
   pip list | grep -E "fastapi|uvicorn|azure"
   ```

3. **Configuration errors**

   **Solution**: Check logs for specific error
   ```bash
   # Run with verbose logging
   LOG_LEVEL=DEBUG python -m src.api.main
   ```

4. **Import errors**

   **Solution**: Verify PYTHONPATH
   ```bash
   # Set PYTHONPATH
   export PYTHONPATH=/home/user/MyFirstRepo/02-work/ai-foundry-agent:$PYTHONPATH

   # Or install as package
   pip install -e .
   ```

### Issue: API Returns 503 Service Unavailable

**Symptom**: `/health` endpoint returns 503

**Solution**:

1. **Check if agent initialized**:
   ```bash
   curl http://localhost:8000/health
   # Look for: "agent_initialized": false
   ```

2. **Check server logs**:
   ```bash
   # Look for initialization errors
   tail -f logs/app.log
   ```

3. **Verify Azure resources are accessible**:
   ```bash
   # Test connectivity
   az ml workspace show \
     --name your-project-name \
     --resource-group knowledge-hub-rg
   ```

4. **Restart server** with debug logging:
   ```bash
   LOG_LEVEL=DEBUG make run
   ```

### Issue: CORS Errors

**Symptom**: Browser shows CORS errors when calling API

**Solution**:

Update CORS configuration in `src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Your frontend
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## Vector Store Issues

### Issue: Vector Store Not Found

**Symptom**: `VectorStoreNotFoundError`

**Solution**:

1. **List existing vector stores**:
   ```python
   stores = agent.client.agents.list_vector_stores()
   for store in stores.data:
       print(f"ID: {store.id}, Name: {store.name}")
   ```

2. **Create if missing**:
   ```python
   agent.create_vector_store()
   ```

3. **Update agent configuration** with correct ID:
   ```python
   config = AgentConfig(
       ...
       vector_store_name="product-docs"  # Must match existing name
   )
   ```

### Issue: Cannot Delete Vector Store

**Symptom**: Error when trying to delete vector store

**Solution**:

1. **Check if vector store is in use**:
   ```python
   # List agents using this vector store
   agents = agent.client.agents.list_agents()
   for a in agents.data:
       if hasattr(a, 'tool_resources') and a.tool_resources:
           print(f"Agent {a.id} uses vector store")
   ```

2. **Delete agent first**:
   ```python
   agent.client.agents.delete_agent(agent.agent.id)
   ```

3. **Then delete vector store**:
   ```python
   agent.client.agents.delete_vector_store(vector_store.id)
   ```

---

## Monitoring & Logging

### Enable Debug Logging

```python
# In your script
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### View Application Insights Logs

```bash
# Recent errors
az monitor app-insights query \
  --app your-app-insights \
  --resource-group knowledge-hub-rg \
  --analytics-query "traces | where severityLevel >= 3 | order by timestamp desc | take 50"

# Agent query performance
az monitor app-insights query \
  --app your-app-insights \
  --resource-group knowledge-hub-rg \
  --analytics-query "customEvents | where name == 'agent_query' | summarize avg(duration), count() by bin(timestamp, 1h)"
```

### Enable Diagnostic Logging

```bash
# Enable diagnostic logs for Web App
az webapp log config \
  --name your-webapp \
  --resource-group knowledge-hub-rg \
  --application-logging filesystem \
  --level information

# Stream logs
az webapp log tail \
  --name your-webapp \
  --resource-group knowledge-hub-rg
```

---

## Getting Help

If you can't resolve an issue:

1. **Check documentation**:
   - [Quick Start Guide](./operations/quick-start-guide.md)
   - [Architecture](./architecture.md)
   - [API Specification](./api-spec.md)

2. **Review logs**:
   - Application Insights → Logs
   - Azure Portal → Resource → Diagnostic Logs

3. **Search existing issues**:
   - GitHub Issues
   - Azure Community Forums

4. **Contact support**:
   - Azure Support (for Azure-specific issues)
   - Internal team (for application issues)

---

*Last Updated: 2025-01-12*
