# AI Foundry Knowledge Hub Agent

Enterprise knowledge hub agent built on Azure AI Foundry with RAG (Retrieval-Augmented Generation) for product documentation.

## Overview

This project implements an intelligent agent that retrieves and answers questions about your product documentation using Azure AI Foundry's agent service with file search and vector search capabilities.

## Features

- ✅ **AI Agent with RAG**: Azure AI Foundry agent with file search for accurate answers
- ✅ **Vector Store**: Azure AI Search integration for custom vector search
- ✅ **Document Processing**: Automatic chunking and embedding of documentation
- ✅ **REST API**: FastAPI endpoints for easy integration
- ✅ **Production Ready**: Full infrastructure as code with Bicep templates
- ✅ **Monitoring**: Application Insights integration for observability

## Architecture

The solution uses Azure AI Foundry's agent service with built-in file search capabilities:

```
User Query → FastAPI → Knowledge Hub Agent → Azure AI Foundry
                                ↓
                         Vector Store (file_search)
                                ↓
                         Product Documentation
                                ↓
                         GPT-4o Response
```

Key components:
- **Knowledge Hub Agent**: Main agent using Azure AI Foundry's agent service
- **Vector Store**: File search with automatic RAG using uploaded documents
- **API Layer**: FastAPI for REST endpoints
- **Infrastructure**: Complete Azure deployment with Bicep

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Azure subscription
- Azure CLI installed and configured

### 1. Deploy Infrastructure

```bash
# Login to Azure
az login

# Deploy infrastructure
cd infrastructure
export RESOURCE_GROUP="knowledge-hub-rg"
export LOCATION="eastus"
./deploy.sh
```

This creates:
- Azure AI Foundry Hub and Project
- Azure OpenAI with GPT-4o
- Azure AI Search
- Web App for API hosting
- Application Insights
- Key Vault

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Azure details from deployment outputs
# Required variables:
# - AZURE_SUBSCRIPTION_ID
# - AZURE_RESOURCE_GROUP
# - AZURE_PROJECT_NAME
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install
```

### 4. Upload Documentation

Upload your product documentation files (markdown, text, PDF, etc.):

```python
from src.agent import KnowledgeHubAgent, AgentConfig

# Initialize agent
config = AgentConfig(
    subscription_id="your-subscription-id",
    resource_group="your-resource-group",
    project_name="your-project-name"
)

agent = KnowledgeHubAgent(config)

# Upload documentation files
file_paths = [
    "docs/product-guide.md",
    "docs/api-reference.md",
    "docs/troubleshooting.md"
]

file_ids = agent.upload_files(file_paths, update_vector_store=True)
print(f"Uploaded {len(file_ids)} files")
```

### 5. Run the API

```bash
# Start the API server
make run

# Or manually:
python -m src.api.main
```

API will be available at `http://localhost:8000`

## Usage Examples

### Using the Python SDK

```python
from src.agent import KnowledgeHubAgent, AgentConfig

# Initialize
config = AgentConfig(
    subscription_id="your-subscription-id",
    resource_group="your-resource-group",
    project_name="your-project-name",
    temperature=0.3
)

agent = KnowledgeHubAgent(config)

# Create vector store and upload docs
agent.create_vector_store()
agent.upload_files(["docs/product-guide.md"])

# Create agent
agent.create_agent()

# Query the agent
response = agent.query("How do I configure authentication?")
print(response)

# Multi-turn conversation
thread = agent.create_thread()
agent.add_message(thread.id, "What are the pricing tiers?")
result = agent.run_agent(thread.id)
print(result["messages"][0]["content"])

# Continue conversation
agent.add_message(thread.id, "Which tier is best for startups?")
result = agent.run_agent(thread.id)
print(result["messages"][0]["content"])
```

### Using the REST API

```bash
# Health check
curl http://localhost:8000/health

# Create a new thread
curl -X POST http://localhost:8000/threads/create

# Query the agent
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I integrate the API?",
    "thread_id": "thread_abc123"
  }'

# Upload files
curl -X POST http://localhost:8000/upload-files \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": ["docs/integration-guide.md"]
  }'

# Get conversation history
curl http://localhost:8000/threads/thread_abc123/history
```

### Using the Vector Store Directly

```python
from src.vector_store import VectorStoreManager, DocumentProcessor

# Initialize vector store
vector_store = VectorStoreManager(
    search_endpoint="https://your-search.search.windows.net",
    index_name="product-knowledge-base",
    openai_endpoint="https://your-openai.openai.azure.com",
    openai_api_key="your-api-key"
)

# Create index
vector_store.create_index()

# Process and upload documents
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
documents = processor.process_file(
    "docs/product-guide.md",
    category="product-docs"
)

vector_store.upload_documents(documents)

# Search
results = vector_store.search("authentication setup", top_k=5)
for result in results:
    print(f"Title: {result['title']}")
    print(f"Content: {result['content'][:200]}...")
    print(f"Score: {result['score']}\n")
```

## Development

```bash
# Install development dependencies
make dev-install

# Run tests
make test

# Lint code
make lint

# Format code
make format

# Clean build artifacts
make clean
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment

### Deploy to Azure Web App

```bash
# Build and deploy
az webapp up \
  --name your-webapp-name \
  --resource-group your-resource-group \
  --runtime "PYTHON:3.11"
```

### Using GitHub Actions

See `.github/workflows/deploy.yml` for CI/CD pipeline example.

## Configuration

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | Required |
| `AZURE_RESOURCE_GROUP` | Resource group name | Required |
| `AZURE_PROJECT_NAME` | AI Foundry project name | Required |
| `AGENT_MODEL` | Model deployment name | `gpt-4o` |
| `AGENT_TEMPERATURE` | Response temperature | `0.3` |
| `USE_FILE_SEARCH` | Enable file search | `true` |

## Monitoring

Application Insights provides:
- Request/response tracking
- Performance metrics
- Error logging
- Custom telemetry

View in Azure Portal → Application Insights → your-insights-name

## Troubleshooting

See [docs/troubleshooting.md](./docs/troubleshooting.md) for common issues and solutions.

## Documentation

- [Architecture](./docs/architecture.md) - Detailed architecture overview
- [API Specification](./docs/api-spec.md) - API endpoints and schemas
- [Runbooks](./docs/runbooks/) - Operational procedures
- [Onboarding](./docs/onboarding.md) - Team onboarding guide

## Status

See [STATUS.md](./STATUS.md) for current implementation status.

## Decisions

See [DECISIONS.md](./DECISIONS.md) for architectural decision records.

## License

Copyright (c) 2025. All rights reserved.
