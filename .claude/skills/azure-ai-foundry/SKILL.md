---
name: azure-ai-foundry
description: Build AI agents and automation with Azure AI Foundry platform (formerly Azure AI Studio). Use when developing AI agents on Azure, implementing prompt flows, building RAG applications, or orchestrating multi-agent systems. Triggers on keywords like Azure AI Foundry, Azure AI Studio, Prompt Flow, Azure OpenAI agents.
---

# Azure AI Foundry

Master building AI agents and automation workflows on Microsoft Azure AI Foundry platform.

## Quick Start

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Initialize AI Foundry client
client = AIProjectClient(
    credential=DefaultAzureCredential(),
    subscription_id="your-subscription-id",
    resource_group_name="your-resource-group",
    project_name="your-project"
)

# Create an agent
agent = client.agents.create_agent(
    model="gpt-4o",
    name="customer-support-agent",
    instructions="You are a helpful customer support assistant.",
    tools=[{"type": "code_interpreter"}, {"type": "file_search"}]
)

# Create a thread and run
thread = client.agents.create_thread()
message = client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="How can I integrate Azure Functions with AI agents?"
)

run = client.agents.create_run(
    thread_id=thread.id,
    agent_id=agent.id
)
```

## Azure AI Foundry Components

Azure AI Foundry provides a comprehensive platform for building production AI applications:

| Component | Purpose |
|-----------|---------|
| **AI Agent Service** | Build and deploy AI agents with tools and memory |
| **Prompt Flow** | Visual designer for LLM orchestration and evaluation |
| **Model Catalog** | Access to 1,800+ models (Azure OpenAI, OSS, custom) |
| **Evaluation & Monitoring** | Test, validate, and monitor AI applications |
| **Vector Search (AI Search)** | Retrieval-Augmented Generation (RAG) infrastructure |
| **Content Safety** | Built-in guardrails and safety filters |
| **MLOps Integration** | CI/CD pipelines for AI applications |

## AI Agent Development

### Basic Agent with Tools

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool

# Define custom function tool
def get_customer_order(order_id: str) -> dict:
    """Retrieve customer order information"""
    # Your implementation
    return {"order_id": order_id, "status": "shipped"}

# Register function as tool
function_tool = FunctionTool(
    name="get_customer_order",
    description="Retrieves customer order information by order ID",
    parameters={
        "type": "object",
        "properties": {
            "order_id": {"type": "string", "description": "The order ID"}
        },
        "required": ["order_id"]
    }
)

# Create agent with custom tool
agent = client.agents.create_agent(
    model="gpt-4o",
    name="order-assistant",
    instructions="Help customers track their orders.",
    tools=[function_tool, {"type": "code_interpreter"}]
)

# Handle tool calls
run = client.agents.create_run(thread_id=thread.id, agent_id=agent.id)

# Poll for completion and handle tool calls
while run.status in ["queued", "in_progress", "requires_action"]:
    if run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        for tool_call in tool_calls:
            if tool_call.function.name == "get_customer_order":
                args = json.loads(tool_call.function.arguments)
                result = get_customer_order(args["order_id"])
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(result)
                })

        # Submit tool outputs
        run = client.agents.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

    run = client.agents.get_run(thread_id=thread.id, run_id=run.id)
```

### Multi-Agent Orchestration

```python
# Create specialized agents
research_agent = client.agents.create_agent(
    model="gpt-4o",
    name="research-specialist",
    instructions="You research and gather comprehensive information.",
    tools=[{"type": "file_search"}, {"type": "web_search"}]
)

analysis_agent = client.agents.create_agent(
    model="gpt-4o",
    name="data-analyst",
    instructions="You analyze data and provide insights.",
    tools=[{"type": "code_interpreter"}]
)

writer_agent = client.agents.create_agent(
    model="gpt-4o",
    name="content-writer",
    instructions="You create clear, professional documentation.",
    tools=[]
)

# Orchestrator pattern
def multi_agent_workflow(user_query: str):
    """Coordinate multiple agents for complex task"""

    # Step 1: Research
    research_thread = client.agents.create_thread()
    client.agents.create_message(
        thread_id=research_thread.id,
        role="user",
        content=f"Research this topic: {user_query}"
    )
    research_run = client.agents.create_and_process_run(
        thread_id=research_thread.id,
        agent_id=research_agent.id
    )
    research_results = client.agents.list_messages(thread_id=research_thread.id)

    # Step 2: Analysis
    analysis_thread = client.agents.create_thread()
    client.agents.create_message(
        thread_id=analysis_thread.id,
        role="user",
        content=f"Analyze this research: {research_results}"
    )
    analysis_run = client.agents.create_and_process_run(
        thread_id=analysis_thread.id,
        agent_id=analysis_agent.id
    )
    analysis_results = client.agents.list_messages(thread_id=analysis_thread.id)

    # Step 3: Writing
    writing_thread = client.agents.create_thread()
    client.agents.create_message(
        thread_id=writing_thread.id,
        role="user",
        content=f"Write a report based on: {analysis_results}"
    )
    writing_run = client.agents.create_and_process_run(
        thread_id=writing_thread.id,
        agent_id=writer_agent.id
    )

    return client.agents.list_messages(thread_id=writing_thread.id)
```

## Prompt Flow for Orchestration

Prompt Flow is Azure's visual tool for building LLM applications with orchestration.

### Basic Prompt Flow

```python
from promptflow import PFClient
from promptflow.entities import Run

# Initialize Prompt Flow client
pf_client = PFClient()

# Create a flow from folder
flow = "./flows/rag-chatbot"

# Test flow locally
result = pf_client.test(
    flow=flow,
    inputs={"question": "What is Azure AI Foundry?"}
)

# Create a batch run
run = pf_client.run(
    flow=flow,
    data="./data/questions.jsonl",
    column_mapping={"question": "${data.question}"},
    stream=True
)

# Deploy flow as endpoint
deployment = pf_client.deployments.create_or_update(
    name="rag-chatbot-endpoint",
    flow=flow,
    instance_type="Standard_DS3_v2",
    instance_count=1
)
```

### Prompt Flow YAML Structure

```yaml
# flow.dag.yaml
$schema: https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json
inputs:
  question:
    type: string

outputs:
  answer:
    type: string
    reference: ${answer_node.output}

nodes:
- name: retrieve_documents
  type: python
  source:
    type: code
    path: retrieve.py
  inputs:
    question: ${inputs.question}

- name: generate_prompt
  type: prompt
  source:
    type: code
    path: prompt.jinja2
  inputs:
    context: ${retrieve_documents.output}
    question: ${inputs.question}

- name: answer_node
  type: llm
  source:
    type: code
    path: answer.py
  inputs:
    prompt: ${generate_prompt.output}
  connection: azure_openai_connection
  api: chat
```

## RAG with Azure AI Search

```python
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery

# Set up vector search
index_client = SearchIndexClient(
    endpoint="https://your-search.search.windows.net",
    credential=credential
)

# Create vector index
index = {
    "name": "knowledge-base",
    "fields": [
        {"name": "id", "type": "Edm.String", "key": True},
        {"name": "content", "type": "Edm.String", "searchable": True},
        {"name": "embedding", "type": "Collection(Edm.Single)",
         "searchable": True, "dimensions": 1536,
         "vectorSearchProfile": "my-profile"}
    ],
    "vectorSearch": {
        "profiles": [{
            "name": "my-profile",
            "algorithm": "my-algorithm"
        }],
        "algorithms": [{
            "name": "my-algorithm",
            "kind": "hnsw"
        }]
    }
}

index_client.create_or_update_index(index)

# Perform vector search
search_client = SearchClient(
    endpoint="https://your-search.search.windows.net",
    index_name="knowledge-base",
    credential=credential
)

# Generate query embedding
query_embedding = get_embedding("What is AI Foundry?")

# Search with vector
results = search_client.search(
    search_text=None,
    vector_queries=[VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=5,
        fields="embedding"
    )]
)

# Use results in RAG pattern
context = "\n".join([doc["content"] for doc in results])
```

## Agent with RAG Integration

```python
# Create agent with file search (built-in RAG)
vector_store = client.agents.create_vector_store(
    name="product-docs",
    file_ids=[file1.id, file2.id, file3.id]
)

agent = client.agents.create_agent(
    model="gpt-4o",
    name="product-expert",
    instructions="Answer questions using the product documentation.",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [vector_store.id]
        }
    }
)

# Agent automatically retrieves relevant docs
thread = client.agents.create_thread()
message = client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="How do I configure authentication?"
)

run = client.agents.create_and_process_run(
    thread_id=thread.id,
    agent_id=agent.id
)
```

## Evaluation and Testing

```python
from azure.ai.evaluation import evaluate

# Define evaluation metrics
def answer_relevance(response, reference):
    # Custom relevance scoring
    return score

def groundedness(response, context):
    # Check if response is grounded in context
    return score

# Run evaluation
results = evaluate(
    evaluation_name="agent-evaluation",
    data="test_data.jsonl",
    evaluators={
        "relevance": answer_relevance,
        "groundedness": groundedness,
        "gpt_coherence": "gpt-coherence"  # Built-in AI-assisted metric
    }
)

# View results
print(f"Average relevance: {results.metrics['relevance'].mean}")
print(f"Groundedness score: {results.metrics['groundedness'].mean}")
```

## Content Safety & Guardrails

```python
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions

# Initialize Content Safety
safety_client = ContentSafetyClient(
    endpoint="https://your-content-safety.cognitiveservices.azure.com",
    credential=credential
)

# Check content before/after agent
def check_content_safety(text: str) -> bool:
    """Validate content meets safety requirements"""
    result = safety_client.analyze_text(
        AnalyzeTextOptions(text=text)
    )

    # Check severity levels
    if (result.hate_result.severity > 2 or
        result.self_harm_result.severity > 2 or
        result.sexual_result.severity > 2 or
        result.violence_result.severity > 2):
        return False
    return True

# Apply to agent workflow
user_input = "User message here"
if check_content_safety(user_input):
    # Process with agent
    response = run_agent(user_input)
    if check_content_safety(response):
        return response
    else:
        return "I cannot provide that response."
```

## Production Deployment

### Azure Container Apps Deployment

```python
# deploy.py
from azure.ai.ml import MLClient
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment

ml_client = MLClient(credential, subscription_id, resource_group, workspace)

# Create endpoint
endpoint = ManagedOnlineEndpoint(
    name="ai-agent-endpoint",
    description="Production AI agent",
    auth_mode="key"
)
ml_client.online_endpoints.begin_create_or_update(endpoint)

# Create deployment
deployment = ManagedOnlineDeployment(
    name="blue",
    endpoint_name="ai-agent-endpoint",
    model=model,
    environment=environment,
    instance_type="Standard_DS3_v2",
    instance_count=2,
    environment_variables={
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY")
    }
)
ml_client.online_deployments.begin_create_or_update(deployment)
```

### Infrastructure as Code (Bicep)

```bicep
// main.bicep
param location string = resourceGroup().location
param projectName string

// AI Foundry Hub
resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: '${projectName}-hub'
  location: location
  kind: 'Hub'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'AI Foundry Hub'
    description: 'Central hub for AI projects'
  }
}

// AI Foundry Project
resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: '${projectName}-project'
  location: location
  kind: 'Project'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'AI Agent Project'
    hubResourceId: aiHub.id
  }
}

// Azure OpenAI
resource openai 'Microsoft.CognitiveServices/accounts@2024-04-01' = {
  name: '${projectName}-openai'
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: '${projectName}-openai'
  }
}

// AI Search for RAG
resource search 'Microsoft.Search/searchServices@2024-03-01' = {
  name: '${projectName}-search'
  location: location
  sku: {
    name: 'standard'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
  }
}
```

## Monitoring and Observability

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Configure Application Insights
configure_azure_monitor(
    connection_string="your-app-insights-connection-string"
)

tracer = trace.get_tracer(__name__)

# Trace agent operations
with tracer.start_as_current_span("agent_execution") as span:
    span.set_attribute("agent.id", agent.id)
    span.set_attribute("thread.id", thread.id)

    run = client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=agent.id
    )

    span.set_attribute("run.status", run.status)
    span.set_attribute("run.tokens", run.usage.total_tokens)
```

## Best Practices

### 1. Agent Design Patterns

- **Single-purpose agents**: Keep each agent focused on one domain
- **Supervisor pattern**: Use orchestrator for multi-agent coordination
- **Tool composition**: Build complex capabilities from simple tools
- **Stateful conversations**: Use threads for maintaining context

### 2. Prompt Engineering

- **Clear instructions**: Define role, capabilities, and constraints
- **Few-shot examples**: Include examples for complex tasks
- **Output formatting**: Specify desired response structure
- **Safety guidelines**: Include content policy in instructions

### 3. Cost Optimization

- **Model selection**: Use GPT-4o-mini for simple tasks, GPT-4o for complex reasoning
- **Caching**: Enable prompt caching for repeated instructions
- **Streaming**: Stream responses for better user experience
- **Token management**: Monitor and optimize token usage

### 4. Security

- **Managed identities**: Use Azure AD authentication
- **Key Vault**: Store secrets in Azure Key Vault
- **Private endpoints**: Use VNet integration for production
- **Content filtering**: Enable Azure Content Safety

## Project Structure Template

```
azure-ai-agent-project/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── customer_support.py
│   └── research_agent.py
├── tools/
│   ├── __init__.py
│   ├── database_tools.py
│   └── api_tools.py
├── flows/
│   ├── rag-flow/
│   │   ├── flow.dag.yaml
│   │   ├── retrieve.py
│   │   └── prompt.jinja2
│   └── evaluation-flow/
├── infrastructure/
│   ├── main.bicep
│   ├── parameters.json
│   └── deploy.sh
├── tests/
│   ├── test_agents.py
│   └── evaluation_data.jsonl
├── requirements.txt
└── README.md
```

## Resources

### Official Documentation
- **Azure AI Foundry**: https://learn.microsoft.com/azure/ai-studio/
- **Azure AI Agent Service**: https://learn.microsoft.com/azure/ai-services/agents/
- **Prompt Flow**: https://microsoft.github.io/promptflow/
- **Azure OpenAI**: https://learn.microsoft.com/azure/ai-services/openai/

### Code Samples
- **Azure AI Samples**: https://github.com/Azure-Samples/azure-ai-samples
- **Contoso Chat**: https://github.com/Azure-Samples/contoso-chat
- **Multi-Agent Samples**: https://github.com/Azure-Samples/agent-openai-python-prompty

### SDKs
- **Python SDK**: `pip install azure-ai-projects azure-ai-ml azure-identity`
- **JavaScript SDK**: `npm install @azure/ai-projects`
- **Prompt Flow SDK**: `pip install promptflow promptflow-tools`

### Learning Resources
- **AI Foundry Quickstart**: https://learn.microsoft.com/azure/ai-studio/quickstarts/
- **Agent Patterns**: https://learn.microsoft.com/azure/ai-services/agents/concepts/agents
- **RAG Tutorial**: https://learn.microsoft.com/azure/ai-studio/tutorials/deploy-chat-web-app

### Community
- **GitHub Discussions**: https://github.com/Azure/azure-sdk-for-python/discussions
- **Microsoft Q&A**: https://learn.microsoft.com/answers/tags/377/azure-ai-studio
- **YouTube Channel**: https://www.youtube.com/@MicrosoftAzure
