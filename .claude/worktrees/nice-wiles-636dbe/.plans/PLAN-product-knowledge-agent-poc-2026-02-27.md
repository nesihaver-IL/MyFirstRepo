# Implementation Plan: Product Knowledge Agent — PoC on Azure AI Foundry
## DETAILED TECHNICAL EDITION

**Author**: AI Champion Team Lead
**Created**: 2026-02-27
**Target Platform**: Azure AI Foundry + Copilot Studio
**Audience**: Management PoC Presentation
**Status**: Draft — Awaiting Review

---

## What We Are Building

A conversational AI agent that:
1. Accepts natural language questions about your products
2. Returns a structured answer: direct response + business context + subsystem reasoning
3. Detects when the user wants a diagram and returns a **colored** architecture image
4. Runs entirely inside your Microsoft tenant (AI Foundry + Copilot Studio)

---

## Architecture (End-to-End)

```
User (Teams / Web)
        │
        ▼
┌─────────────────────────────┐
│     Copilot Studio          │  ← Conversation management, channel routing
│  Topic: "Product Question"  │
│  Action: HTTP POST          │
└──────────────┬──────────────┘
               │ POST /score  { "question": "..." }
               ▼
┌─────────────────────────────────────────────────────┐
│         Azure AI Foundry — Prompt Flow              │
│                                                     │
│  [1] intent_classifier  (LLM node / GPT-4o)        │
│       → detects: PRODUCT_OPERATION, DIAGRAM_REQUEST │
│                                                     │
│  [2] rag_retrieval  (Python node)                   │
│       → Azure AI Search: hybrid vector+keyword      │
│       → returns: doc chunks + diagram metadata      │
│                                                     │
│  [3] answer_synthesizer  (LLM node / GPT-4o)       │
│       → structured answer: Answer + Business +      │
│         Subsystem + Related Components              │
│                                                     │
│  [4] diagram_handler  (Python node)                 │
│       → if diagram found: return blob URL           │
│       → if not found: call DALL-E 3 → new image    │
│                                                     │
│  [5] response_assembler  (Python node)              │
│       → combine text answer + image URL             │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
Azure AI Search      Azure Blob Storage
  - product-docs       - product-docs/
  - diagram-metadata   - diagrams/ (colored PNGs)
```

---

## PHASE 0 — Preparation (Do This First, ~2 hours)

### 0.1 — Collect Your Product Content

You need at minimum for a credible PoC:
- **3–5 product documents** (PDF or Word or plain text)
- **2–4 architecture diagrams** saved as PNG (colored — not screenshots of Visio in B&W)

**Document format rules** (important for AI Search chunking):
- Convert Word → PDF if possible (better text extraction)
- Each document should have clear section headers (H1, H2 in Word or Markdown)
- Recommended max file size: 10 MB per file

**Name your files using this convention** (so metadata can be extracted):
```
{product-id}_{doc-type}_{version}.pdf

Examples:
  payment-gateway_operational_v2.pdf
  payment-gateway_architecture_v2.pdf
  auth-service_business-case_v1.pdf
  order-management_operational_v1.pdf
```

**Name your diagrams** using this convention:
```
{product-id}_{subsystem}_{diagram-type}.png

Examples:
  payment-gateway_auth-flow_architecture.png
  order-management_fulfillment-flow_sequence.png
  auth-service_overview_architecture.png
```

### 0.2 — Prepare Your Azure Subscription

You need one person with **Owner or Contributor** role on the Azure subscription.

Check access:
1. Go to: `portal.azure.com`
2. Click top-right avatar → "My permissions"
3. Confirm you have Contributor or Owner on the subscription

Check OpenAI quota availability:
1. Go to: `portal.azure.com` → search "Azure OpenAI" → "Quotas"
2. Look for: `gpt-4o` and `dall-e-3` in your region (East US 2 or Sweden Central)
3. If quota shows 0, submit a quota increase request via the "Request quota" button

### 0.3 — Prepare Your 15 Test Questions

Write down 15 specific questions based on your real products.
Use this template and save as a file called `test_questions.txt`:
```
# PRODUCT_OPERATION (5 questions)
1. How does [Product A] process [main function]?
2. What happens step by step when [action] occurs in [Product B]?
3. Walk me through the [workflow] in [Product C].
4. What does [component] do inside [Product A]?
5. How does [Product B] handle [edge case]?

# BUSINESS_CASE (4 questions)
6. Why does [Product A] have a separate [component]?
7. What business problem does [Product B] solve?
8. What is the value of the [feature] in [Product C]?
9. Why was [architectural decision] made in [Product A]?

# SUBSYSTEM_REASONING (3 questions)
10. How does [subsystem X] relate to [subsystem Y] in [Product A]?
11. What is the flow between [component A] and [component B]?
12. Explain the data flow from [input point] to [output point] in [Product B].

# DIAGRAM_REQUEST (3 questions)
13. Show me the architecture of [Product A].
14. Give me a diagram of the [subsystem] in [Product B].
15. I want to see how the components of [Product C] connect.
```

---

## PHASE 1 — Azure Infrastructure Setup (~3 hours)

Work through these steps in order. Each has exact fields to fill.

### STEP 1.1 — Create Resource Group

Every Azure resource needs a resource group (a logical container).

```
1. Go to: portal.azure.com
2. Search: "Resource groups" in top search bar
3. Click: "+ Create"
4. Fill in:
   Subscription:      [select your subscription]
   Resource group:    rg-product-knowledge-poc
   Region:            East US 2
5. Click "Review + create"
6. Click "Create"
```

### STEP 1.2 — Create Azure AI Foundry Hub

The Hub is the top-level workspace. You create one Hub, then Projects inside it.

```
1. Go to: portal.azure.com
2. Search: "Azure AI Foundry" in top search bar
3. Click "Azure AI Foundry" (the service, not the external site)
4. Click: "+ Create" → "Hub"
5. Fill in:
   Subscription:           [your subscription]
   Resource group:         rg-product-knowledge-poc
   Hub name:               hub-product-knowledge
   Region:                 East US 2
   Storage account:        (leave — auto-creates: storehubproductknowledge)
   Key vault:              (leave — auto-creates: kv-product-knowledge)
   Application Insights:   (leave — auto-creates)
   Container Registry:     (leave as None for PoC)
6. Click "Next: AI Services"
7. Under "AI Services":
   Select existing or create new: Create new
   Azure OpenAI resource name:    aoai-product-knowledge
8. Click "Next: Networking"
   Network access: Public (for PoC — change to private for production)
9. Click "Review + create"
10. Click "Create"
    ⏳ Wait 3–5 minutes for deployment to complete.
```

### STEP 1.3 — Create AI Foundry Project

```
1. After Hub is created, click: "Go to resource"
2. Inside the Hub view, click: "+ New project"
3. Fill in:
   Project name:   product-knowledge-agent
   Hub:            hub-product-knowledge (auto-selected)
4. Click "Create"
   ⏳ Wait ~2 minutes
5. You are now inside your AI Foundry Project.
   Save this URL — you'll return here many times:
   https://ai.azure.com/  → your project
```

### STEP 1.4 — Deploy GPT-4o Model

```
Inside AI Foundry Project:
1. Left sidebar → "Deployments"
2. Click: "+ Deploy model" → "Deploy base model"
3. Search: "gpt-4o"
4. Select: "gpt-4o" (pick latest version shown, e.g., 2024-11-20)
5. Click: "Confirm"
6. Fill in:
   Deployment name:          gpt-4o-product
   Deployment type:          Standard
   Tokens per minute (TPM):  80,000   ← plenty for PoC
   Content filter:           DefaultV2
7. Click: "Deploy"
   ⏳ Wait ~1 minute
8. COPY AND SAVE:
   - Deployment name: gpt-4o-product
   - Target URI (endpoint): shown on the deployment page
   - API Key: shown under "Keys and Endpoint" in the Azure OpenAI resource
```

### STEP 1.5 — Deploy DALL-E 3 Model

```
Inside AI Foundry Project:
1. Left sidebar → "Deployments"
2. Click: "+ Deploy model" → "Deploy base model"
3. Search: "dall-e-3"
4. Select: "dall-e-3"
5. Click: "Confirm"
6. Fill in:
   Deployment name:    dalle3-diagrams
   Deployment type:    Standard
   Images per minute:  15   ← default for DALL-E 3
7. Click: "Deploy"
8. COPY AND SAVE: Deployment name: dalle3-diagrams
```

### STEP 1.6 — Create Azure AI Search

Azure AI Search is separate from AI Foundry. Create it via Azure Portal.

```
1. Go to: portal.azure.com
2. Search: "AI Search" in top search bar
3. Click: "+ Create"
4. Fill in:
   Subscription:     [your subscription]
   Resource group:   rg-product-knowledge-poc
   Service name:     srch-product-knowledge   ← must be globally unique
   Region:           East US 2                ← MUST match your OpenAI region
   Pricing tier:     Standard S1              ← click "Change Tier" to select
5. Click "Review + create"
6. Click "Create"
   ⏳ Wait ~3 minutes
7. After creation, go to the resource.
8. COPY AND SAVE:
   - Url: https://srch-product-knowledge.search.windows.net
   - Admin key: Left sidebar → "Keys" → copy "Primary admin key"
```

**Enable Semantic Ranking** (free tier: 1000 queries/month):
```
Inside AI Search resource:
1. Left sidebar → "Semantic ranker"
2. Click: "Enable semantic ranker"   ← free tier is sufficient for PoC
```

### STEP 1.7 — Create Azure Blob Storage

```
1. Go to: portal.azure.com
2. Search: "Storage accounts"
3. Click: "+ Create"
4. Fill in:
   Subscription:       [your subscription]
   Resource group:     rg-product-knowledge-poc
   Storage account:    productkbstoragepoc    ← 3–24 chars, lowercase only
   Region:             East US 2
   Performance:        Standard
   Redundancy:         LRS (Locally-redundant storage)
5. Click "Review + create" → "Create"
6. After creation, go to the resource.
7. COPY AND SAVE:
   - Storage account name: productkbstoragepoc
   - Connection string: Left sidebar → "Access keys" → "Connection string" (key1)
```

**Create Containers:**
```
Inside Storage Account:
1. Left sidebar → "Containers"
2. Click: "+ Container"
   Name: product-docs
   Public access level: Private
   Click "Create"

3. Click: "+ Container" again
   Name: diagrams
   Public access level: Blob (read access for blobs only)
   ← IMPORTANT: diagrams must be publicly readable so Copilot Studio can display them
   Click "Create"
```

---

## PHASE 2 — Knowledge Base Setup (~4 hours)

### STEP 2.1 — Upload Documents to Blob Storage

```
Inside Storage Account → Containers → product-docs:
1. Click "Upload"
2. Select all your product PDF/Word files
3. Click "Upload"
   Each file should appear in the list when done.

Inside Storage Account → Containers → diagrams:
1. Click "Upload"
2. Select all your colored PNG diagram files
3. Click "Upload"
```

After uploading diagrams, **get the public URL for each**:
```
Click on a diagram file (e.g., payment-gateway_auth-flow_architecture.png)
Copy the "URL" field — it looks like:
https://productkbstoragepoc.blob.core.windows.net/diagrams/payment-gateway_auth-flow_architecture.png

Save all diagram URLs in a spreadsheet. You'll need them in Step 2.3.
```

### STEP 2.2 — Create the Product Docs Search Index

The index tells Azure AI Search what fields each document has. We create it with the exact JSON schema below.

**Option A — Via Azure Portal (easier for PoC):**
```
Inside AI Foundry Project:
1. Left sidebar → "Indexes"
2. Click: "+ New index"
3. Select data source:
   Data source type: Azure Blob Storage
   Connection: (click "New connection")
     Storage account: productkbstoragepoc
     Container: product-docs
   Click "Next"
4. Configure search settings:
   ✅ Enable semantic search
   ✅ Add vector search   (choose: text-embedding-ada-002)
5. Index name: product-docs-index
6. Click "Create"
```

AI Foundry automatically:
- Reads all documents from blob
- Chunks them into ~500-token pieces
- Generates vector embeddings for each chunk
- Creates the searchable index

**This process takes 5–20 minutes** depending on document count. You can watch progress under "Indexes."

**Option B — Via Python Script** (gives you more control over field schema):

Save this as `scripts/create_search_index.py` and run locally:

```python
# scripts/create_search_index.py
# Run: pip install azure-search-documents azure-storage-blob openai
# Run: python create_search_index.py

import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType,
    SimpleField, SearchableField,
    SemanticConfiguration, SemanticSearch, SemanticPrioritizedFields,
    SemanticField, VectorSearch, HnswAlgorithmConfiguration,
    VectorSearchProfile, SearchIndex
)
from azure.core.credentials import AzureKeyCredential

# ── FILL THESE IN ────────────────────────────────────────────
SEARCH_ENDPOINT = "https://srch-product-knowledge.search.windows.net"
SEARCH_ADMIN_KEY = "YOUR_SEARCH_ADMIN_KEY"
INDEX_NAME = "product-docs-index"
# ─────────────────────────────────────────────────────────────

credential = AzureKeyCredential(SEARCH_ADMIN_KEY)
index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=credential)

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchableField(name="title", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="product_id", type=SearchFieldDataType.String, filterable=True, facetable=True),
    SimpleField(name="subsystem", type=SearchFieldDataType.String, filterable=True, facetable=True),
    SimpleField(name="doc_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
    # "operational" | "business_case" | "architecture" | "general"
    SimpleField(name="source_file", type=SearchFieldDataType.String, retrievable=True),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,   # ada-002 dimension
        vector_search_profile_name="vector-profile"
    ),
]

vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="hnsw-algo")],
    profiles=[VectorSearchProfile(name="vector-profile", algorithm_configuration_name="hnsw-algo")]
)

semantic_config = SemanticConfiguration(
    name="product-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        content_fields=[SemanticField(field_name="content")],
        keywords_fields=[SemanticField(field_name="title"), SemanticField(field_name="product_id")]
    )
)

index = SearchIndex(
    name=INDEX_NAME,
    fields=fields,
    vector_search=vector_search,
    semantic_search=SemanticSearch(configurations=[semantic_config])
)

index_client.create_or_update_index(index)
print(f"Index '{INDEX_NAME}' created successfully.")
```

### STEP 2.3 — Create the Diagram Metadata Index

This is a second, smaller index that holds metadata about each diagram (not the image itself — just a description and URL).

Save as `scripts/create_diagram_index.py`:

```python
# scripts/create_diagram_index.py

import os, json
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType,
    SimpleField, SearchableField
)
from azure.core.credentials import AzureKeyCredential

# ── FILL THESE IN ────────────────────────────────────────────
SEARCH_ENDPOINT = "https://srch-product-knowledge.search.windows.net"
SEARCH_ADMIN_KEY = "YOUR_SEARCH_ADMIN_KEY"
INDEX_NAME = "diagram-metadata-index"
# ─────────────────────────────────────────────────────────────

credential = AzureKeyCredential(SEARCH_ADMIN_KEY)
index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=credential)

# Define the index schema
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="description", type=SearchFieldDataType.String),
    SearchableField(name="keywords", type=SearchFieldDataType.String),
    SimpleField(name="product_id", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="subsystem", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="diagram_url", type=SearchFieldDataType.String, retrievable=True),
    SimpleField(name="diagram_type", type=SearchFieldDataType.String, filterable=True),
    # "architecture" | "sequence" | "flow" | "component"
]

index = SearchIndex(name=INDEX_NAME, fields=fields)
index_client.create_or_update_index(index)
print(f"Index '{INDEX_NAME}' created.")

# ── Now load your diagram metadata ───────────────────────────
# Edit this list — one entry per diagram PNG you uploaded
diagrams = [
    {
        "id": "payment-gateway_auth-flow_architecture",
        "product_id": "payment-gateway",
        "subsystem": "authentication-flow",
        "diagram_type": "architecture",
        "description": "Architecture diagram showing the authentication flow of the payment gateway. Includes token validation, OAuth2 handshake, and session management components.",
        "keywords": "payment gateway authentication auth token OAuth JWT session flow architecture",
        "diagram_url": "https://productkbstoragepoc.blob.core.windows.net/diagrams/payment-gateway_auth-flow_architecture.png"
    },
    {
        "id": "order-management_fulfillment-flow_sequence",
        "product_id": "order-management",
        "subsystem": "fulfillment-flow",
        "diagram_type": "sequence",
        "description": "Sequence diagram showing the order fulfillment flow from order placement to delivery confirmation.",
        "keywords": "order management fulfillment delivery sequence flow warehouse shipping",
        "diagram_url": "https://productkbstoragepoc.blob.core.windows.net/diagrams/order-management_fulfillment-flow_sequence.png"
    },
    # ← ADD MORE ENTRIES HERE for each diagram you uploaded
]

# Upload metadata to the index
search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=credential
)
result = search_client.upload_documents(documents=diagrams)
print(f"Uploaded {len(diagrams)} diagram metadata records.")
```

Run both scripts from your local machine:
```bash
pip install azure-search-documents azure-storage-blob openai
python scripts/create_search_index.py
python scripts/create_diagram_index.py
```

### STEP 2.4 — Upload and Chunk Product Documents

Save as `scripts/upload_and_index_docs.py`:

```python
# scripts/upload_and_index_docs.py
# Reads PDFs from local folder, splits into chunks, generates embeddings, indexes them

import os, uuid, json
from pathlib import Path
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

# ── FILL THESE IN ────────────────────────────────────────────
STORAGE_CONNECTION_STRING = "YOUR_STORAGE_CONNECTION_STRING"
STORAGE_CONTAINER = "product-docs"

SEARCH_ENDPOINT = "https://srch-product-knowledge.search.windows.net"
SEARCH_ADMIN_KEY = "YOUR_SEARCH_ADMIN_KEY"
SEARCH_INDEX = "product-docs-index"

OPENAI_ENDPOINT = "https://aoai-product-knowledge.openai.azure.com/"
OPENAI_API_KEY  = "YOUR_OPENAI_API_KEY"
EMBEDDING_MODEL = "text-embedding-ada-002"

DOCS_FOLDER = "./knowledge-base/sample-products/"
# ─────────────────────────────────────────────────────────────

openai_client = AzureOpenAI(api_key=OPENAI_API_KEY, azure_endpoint=OPENAI_ENDPOINT, api_version="2024-02-01")
search_client = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, AzureKeyCredential(SEARCH_ADMIN_KEY))
blob_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks

def get_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(input=text, model=EMBEDDING_MODEL)
    return response.data[0].embedding

def parse_metadata_from_filename(filename: str) -> dict:
    """
    Extract product_id, doc_type from filename convention:
    payment-gateway_operational_v2.pdf → product_id=payment-gateway, doc_type=operational
    """
    stem = Path(filename).stem  # remove .pdf
    parts = stem.split("_")
    return {
        "product_id": parts[0] if len(parts) > 0 else "unknown",
        "doc_type":   parts[1] if len(parts) > 1 else "general",
    }

# Process each document
docs_to_index = []
for filepath in Path(DOCS_FOLDER).glob("*.pdf"):
    print(f"Processing: {filepath.name}")
    meta = parse_metadata_from_filename(filepath.name)

    # Upload original file to blob (for reference)
    with open(filepath, "rb") as f:
        blob_client.get_container_client(STORAGE_CONTAINER).upload_blob(
            name=filepath.name, data=f, overwrite=True
        )

    # Extract text — use Azure Document Intelligence for real PDFs
    # For PoC with text-based PDFs, use PyMuPDF:
    try:
        import fitz  # pip install PyMuPDF
        doc = fitz.open(str(filepath))
        full_text = " ".join(page.get_text() for page in doc)
    except ImportError:
        print("Install PyMuPDF: pip install PyMuPDF")
        continue

    # Chunk and embed
    chunks = chunk_text(full_text)
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        docs_to_index.append({
            "id": f"{meta['product_id']}-chunk-{i}-{uuid.uuid4().hex[:8]}",
            "content": chunk,
            "title": filepath.stem,
            "product_id": meta["product_id"],
            "subsystem": "general",   # can be refined per document
            "doc_type": meta["doc_type"],
            "source_file": filepath.name,
            "content_vector": embedding,
        })
    print(f"  → {len(chunks)} chunks created")

# Upload all chunks to AI Search
batch_size = 100
for i in range(0, len(docs_to_index), batch_size):
    batch = docs_to_index[i:i+batch_size]
    search_client.upload_documents(documents=batch)
    print(f"Uploaded batch {i//batch_size + 1} ({len(batch)} documents)")

print(f"\nDone. Total chunks indexed: {len(docs_to_index)}")
```

---

## PHASE 3 — Build the Prompt Flow (~6 hours)

This is the core of the agent. You work inside AI Foundry's visual Prompt Flow editor.

### STEP 3.1 — Create the Flow

```
Inside AI Foundry Project (ai.azure.com):
1. Left sidebar → "Prompt flow"
2. Click: "+ Create"
3. Select: "Standard flow"  ← not Chat flow, not Evaluation flow
4. Flow name: product-knowledge-flow
5. Click: "Create"

You now see a visual canvas with:
  - "inputs" node (top)
  - one default LLM node
  - "outputs" node (bottom)

We will replace/add nodes to build our 5-node pipeline.
```

### STEP 3.2 — Configure Flow Inputs

```
Click "inputs" node:
1. Delete the default input if any
2. Add input:
   Name: question
   Type: string
   Description: The user's question about a product
3. Click: "Save"
```

### STEP 3.3 — Configure Flow Outputs

```
Click "outputs" node:
1. Add output:
   Name: final_response
   Type: string
   Value: ${response_assembler.output}   ← references node we'll create
2. Click: "Save"
```

### STEP 3.4 — Set Up Connections

Before building nodes, set up the connections to OpenAI and AI Search.

**OpenAI Connection:**
```
Left sidebar → "Settings" → "Connections"
Click: "+ New connection" → "Azure OpenAI"
Fill in:
  Connection name:  aoai-product-connection
  API Key:          [your Azure OpenAI API key]
  API Base:         https://aoai-product-knowledge.openai.azure.com/
  API Version:      2024-02-01
Click: "Save"
```

**AI Search Connection:**
```
Left sidebar → "Settings" → "Connections"
Click: "+ New connection" → "Azure AI Search"
Fill in:
  Connection name:  search-product-connection
  API Key:          [your Search admin key]
  API Base:         https://srch-product-knowledge.search.windows.net
Click: "Save"
```

### STEP 3.5 — NODE 1: Intent Classifier (LLM Node)

```
On the canvas:
1. Click: "+ Add node" → "LLM"
2. Name this node: intent_classifier
3. Connection: aoai-product-connection
4. Deployment:  gpt-4o-product
5. Max tokens:  300
6. Temperature: 0   ← we want consistent, deterministic classification
```

Click the node → click "Prompt" tab → paste this exact template:

```jinja2
system:
You are an intent classifier for a Product Knowledge Agent.

Classify the user question into one or more categories:
- PRODUCT_OPERATION  : questions about how something works, what it does, step-by-step processes
- BUSINESS_CASE      : questions about WHY something exists, business value, business problem solved
- SUBSYSTEM_REASONING: questions about relationships between components, flows, dependencies
- DIAGRAM_REQUEST    : explicit requests for a diagram, architecture view, visual representation
- GENERAL            : anything else

Also extract:
- product_hint: the product name mentioned (or "unknown")
- subsystem_hint: the subsystem/component mentioned (or "unknown")

Return ONLY valid JSON. No explanation. No markdown. Just JSON.

Example output:
{"intents": ["PRODUCT_OPERATION", "DIAGRAM_REQUEST"], "product_hint": "payment gateway", "subsystem_hint": "authentication"}

user:
{{question}}
```

**Connect this node:**
```
In the "Inputs" section of the node:
  question = ${inputs.question}
```

### STEP 3.6 — NODE 2: RAG Retrieval (Python Node)

```
On the canvas:
1. Click: "+ Add node" → "Python"
2. Name this node: rag_retrieval
```

Paste this complete Python code:

```python
# Node: rag_retrieval
# pip install azure-search-documents openai (installed in flow runtime)

import json
from promptflow.core import tool
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

@tool
def rag_retrieval(
    question: str,
    intent_json: str,
    search_endpoint: str,
    search_key: str,
    openai_endpoint: str,
    openai_key: str,
    openai_embedding_deployment: str = "text-embedding-ada-002"
) -> dict:
    """
    Performs hybrid RAG retrieval:
    1. Generates embedding for the question
    2. Runs hybrid (vector + keyword) search on product-docs-index
    3. Runs keyword search on diagram-metadata-index
    Returns: { "doc_chunks": [...], "diagrams": [...], "intents": [...], "product_hint": ..., "subsystem_hint": ... }
    """

    # Parse intent classification result
    try:
        intent_data = json.loads(intent_json)
    except:
        intent_data = {"intents": ["GENERAL"], "product_hint": "unknown", "subsystem_hint": "unknown"}

    intents = intent_data.get("intents", ["GENERAL"])
    product_hint = intent_data.get("product_hint", "unknown")
    subsystem_hint = intent_data.get("subsystem_hint", "unknown")

    # ── Generate question embedding ──────────────────────────
    aoai = AzureOpenAI(api_key=openai_key, azure_endpoint=openai_endpoint, api_version="2024-02-01")
    embedding_response = aoai.embeddings.create(
        input=question,
        model=openai_embedding_deployment
    )
    question_vector = embedding_response.data[0].embedding

    # ── Search product-docs-index (hybrid: vector + keyword) ─
    doc_credential = AzureKeyCredential(search_key)
    docs_client = SearchClient(
        endpoint=search_endpoint,
        index_name="product-docs-index",
        credential=doc_credential
    )

    # Build optional filter for product_id
    filter_expr = None
    if product_hint != "unknown":
        # Fuzzy match on product_id — search within content instead
        filter_expr = None  # skip filter for PoC; let semantic ranking handle it

    vector_query = VectorizedQuery(
        vector=question_vector,
        k_nearest_neighbors=50,
        fields="content_vector"
    )

    doc_results = docs_client.search(
        search_text=question,           # keyword component
        vector_queries=[vector_query],  # vector component
        query_type="semantic",
        semantic_configuration_name="product-semantic-config",
        top=5,
        select=["id", "content", "title", "product_id", "subsystem", "doc_type", "source_file"],
        filter=filter_expr
    )

    doc_chunks = []
    for result in doc_results:
        doc_chunks.append({
            "content": result["content"],
            "title": result.get("title", ""),
            "product_id": result.get("product_id", ""),
            "doc_type": result.get("doc_type", ""),
            "score": result.get("@search.score", 0)
        })

    # ── Search diagram-metadata-index (keyword only) ─────────
    diagrams_client = SearchClient(
        endpoint=search_endpoint,
        index_name="diagram-metadata-index",
        credential=doc_credential
    )

    diagram_search_text = f"{product_hint} {subsystem_hint}".strip()
    if diagram_search_text == "unknown unknown":
        diagram_search_text = question[:100]  # fallback: use question text

    diagram_results = diagrams_client.search(
        search_text=diagram_search_text,
        top=3,
        select=["id", "product_id", "subsystem", "description", "diagram_url", "diagram_type", "keywords"]
    )

    diagrams = []
    for result in diagram_results:
        diagrams.append({
            "id": result.get("id", ""),
            "product_id": result.get("product_id", ""),
            "subsystem": result.get("subsystem", ""),
            "description": result.get("description", ""),
            "diagram_url": result.get("diagram_url", ""),
            "score": result.get("@search.score", 0)
        })

    return {
        "doc_chunks": doc_chunks,
        "diagrams": diagrams,
        "intents": intents,
        "product_hint": product_hint,
        "subsystem_hint": subsystem_hint
    }
```

**Connect this node inputs:**
```
question         = ${inputs.question}
intent_json      = ${intent_classifier.output}
search_endpoint  = (type as literal) https://srch-product-knowledge.search.windows.net
search_key       = (type as literal) YOUR_SEARCH_ADMIN_KEY
openai_endpoint  = (type as literal) https://aoai-product-knowledge.openai.azure.com/
openai_key       = (type as literal) YOUR_OPENAI_API_KEY
```

> **Security note**: For production, use Azure Key Vault references instead of literal keys. For PoC, literals are acceptable.

### STEP 3.7 — NODE 3: Answer Synthesizer (LLM Node)

```
On the canvas:
1. Click: "+ Add node" → "LLM"
2. Name this node: answer_synthesizer
3. Connection: aoai-product-connection
4. Deployment:  gpt-4o-product
5. Max tokens:  1500
6. Temperature: 0.3   ← slight creativity for natural language, still focused
```

Paste this prompt template:

```jinja2
system:
You are the Product Knowledge Agent for our company. You have expert-level knowledge of our product portfolio.

Your job is to answer questions about our products clearly, completely, and with business context.

ALWAYS structure EVERY response using exactly these four sections:

## Answer
Provide a clear, direct answer to the question. Be specific and accurate.
If the question is procedural (how does X work), describe the steps.
If the question is about a feature, explain what it does.

## Business Context
Explain the business rationale:
- What business problem does this solve?
- What value does it deliver to the organization or end users?
- Why was this approach chosen over alternatives?
Be concrete — avoid generic statements like "it improves efficiency."

## Subsystem Explanation
If the question involves components, flows, or relationships:
- List the components/units involved
- Describe the direction of data or control flow (use arrows: A → B → C)
- Explain what each unit does in the context of this feature
- Note any key dependencies or integrations
If the question doesn't involve subsystem reasoning, write: "N/A for this question."

## Related Components
List 2–5 other components, subsystems, or products that are directly related to or interact with what was asked.

RULES:
- Use ONLY information from the provided context
- If information is not in the context, say: "This information is not available in the current knowledge base."
- NEVER invent facts, numbers, or behaviors
- Keep language professional and precise
- Do not add a conclusion or summary section

---
CONTEXT FROM KNOWLEDGE BASE:
{{doc_context}}

---
USER QUESTION: {{question}}
DETECTED INTENT: {{intents}}

user:
Please answer based on the context above.
```

**Connect this node inputs:**
```
question    = ${inputs.question}
intents     = ${rag_retrieval.output.intents}
doc_context = ${rag_retrieval.output.doc_chunks}
```

### STEP 3.8 — NODE 4: Diagram Handler (Python Node)

```
On the canvas:
1. Click: "+ Add node" → "Python"
2. Name this node: diagram_handler
```

Paste this complete Python code:

```python
# Node: diagram_handler

import json
from promptflow.core import tool
from openai import AzureOpenAI

@tool
def diagram_handler(
    intents: list,
    diagrams: list,
    product_hint: str,
    subsystem_hint: str,
    openai_endpoint: str,
    openai_key: str,
    dalle_deployment: str = "dalle3-diagrams",
    score_threshold: float = 0.3
) -> dict:
    """
    Handles diagram retrieval or generation.
    Returns: { "diagram_url": str|None, "diagram_mode": str|None, "diagram_description": str }
    """

    # Only run if the user asked for a diagram
    if "DIAGRAM_REQUEST" not in intents:
        return {
            "diagram_url": None,
            "diagram_mode": None,
            "diagram_description": ""
        }

    # ── MODE 1: Return pre-built diagram if found ────────────
    if diagrams and len(diagrams) > 0:
        best = diagrams[0]
        score = best.get("score", 0)
        if score >= score_threshold and best.get("diagram_url"):
            return {
                "diagram_url": best["diagram_url"],
                "diagram_mode": "retrieved",
                "diagram_description": best.get("description", "Architecture diagram from knowledge base")
            }

    # ── MODE 2: Generate new diagram with DALL-E 3 ───────────
    product_label  = product_hint  if product_hint  != "unknown" else "the product"
    subsystem_label = subsystem_hint if subsystem_hint != "unknown" else "its main components"

    dalle_prompt = f"""Create a professional software architecture diagram for:
Product: {product_label}
Subsystem / Focus: {subsystem_label}

Diagram requirements:
- Style: clean, modern enterprise architecture diagram (similar to Microsoft Azure or AWS diagrams)
- Background: white
- Use DISTINCT COLORS for each component type:
    * Blue (#0078D4) = services and APIs
    * Green (#107C10) = databases and data stores
    * Orange (#CA5010) = message queues and async components
    * Purple (#8764B8) = external systems and third-party integrations
    * Gray (#605E5C) = infrastructure (load balancers, gateways)
- Draw directional arrows between components showing the data/control flow
- Label every component with its name and role
- Include a color legend in the bottom-right corner
- Include a title at the top: "{product_label} — {subsystem_label} Architecture"
- Do NOT use black and white only
- Aspect ratio: landscape (wider than tall)
- Include at least 5 distinct components"""

    try:
        aoai = AzureOpenAI(
            api_key=openai_key,
            azure_endpoint=openai_endpoint,
            api_version="2024-02-01"
        )

        response = aoai.images.generate(
            model=dalle_deployment,
            prompt=dalle_prompt,
            size="1792x1024",   # landscape, best for architecture diagrams
            quality="hd",
            style="natural",    # "natural" gives more realistic/precise rendering than "vivid"
            n=1
        )

        generated_url = response.data[0].url

        return {
            "diagram_url": generated_url,
            "diagram_mode": "generated",
            "diagram_description": f"AI-generated architecture diagram: {product_label} — {subsystem_label}"
        }

    except Exception as e:
        # Graceful fallback — diagram generation failed but don't crash the whole flow
        return {
            "diagram_url": None,
            "diagram_mode": "failed",
            "diagram_description": f"Diagram generation failed: {str(e)}"
        }
```

**Connect this node inputs:**
```
intents          = ${rag_retrieval.output.intents}
diagrams         = ${rag_retrieval.output.diagrams}
product_hint     = ${rag_retrieval.output.product_hint}
subsystem_hint   = ${rag_retrieval.output.subsystem_hint}
openai_endpoint  = (literal) https://aoai-product-knowledge.openai.azure.com/
openai_key       = (literal) YOUR_OPENAI_API_KEY
```

### STEP 3.9 — NODE 5: Response Assembler (Python Node)

```
On the canvas:
1. Click: "+ Add node" → "Python"
2. Name this node: response_assembler
```

Paste this code:

```python
# Node: response_assembler

from promptflow.core import tool

@tool
def response_assembler(
    answer: str,
    diagram_url: str,
    diagram_mode: str,
    diagram_description: str
) -> str:
    """
    Combines the text answer with the diagram (if any) into the final response.
    """

    response = answer.strip()

    if diagram_url and diagram_mode in ("retrieved", "generated"):
        if diagram_mode == "retrieved":
            source_label = "From knowledge base"
        else:
            source_label = "Generated for this request"

        response += f"""

---

## Architecture Diagram
*{source_label}*

![Architecture Diagram]({diagram_url})

_{diagram_description}_
"""

    elif diagram_mode == "failed":
        response += f"""

---

> **Note**: Diagram generation was not available for this request. Try again or contact the AI team.
"""

    return response
```

**Connect this node inputs:**
```
answer               = ${answer_synthesizer.output}
diagram_url          = ${diagram_handler.output.diagram_url}
diagram_mode         = ${diagram_handler.output.diagram_mode}
diagram_description  = ${diagram_handler.output.diagram_description}
```

### STEP 3.10 — Connect Outputs Node

```
Click "outputs" node:
Verify: final_response = ${response_assembler.output}
```

### STEP 3.11 — Test the Flow in AI Foundry

```
Top of canvas → click "Run" button (▶)
Input:
  question: "How does the payment gateway authenticate transactions?"

Expected: You see the output in the "Outputs" panel with:
  - A structured Answer section
  - Business Context section
  - Subsystem Explanation section
  - (If diagram match found) An image URL at the bottom

If it works → click "Deploy" to create an endpoint.
```

### STEP 3.12 — Deploy the Flow as an Endpoint

```
Top of canvas → click "Deploy"
Fill in:
  Endpoint name:  product-knowledge-endpoint
  Deployment:     prod-v1
  Instance type:  Standard_DS3_v2 (2 cores, 14 GB — sufficient for PoC)
  Instance count: 1
Click: "Review + create" → "Create"
⏳ Wait 5–10 minutes for deployment.

After deployment, go to: Left sidebar → "Deployments"
Click on: product-knowledge-endpoint
Copy:
  - REST endpoint URL (looks like: https://product-knowledge-endpoint.eastus2.inference.ml.azure.com/score)
  - Primary key (under "Authentication" tab)

SAVE BOTH — you'll need them in Phase 4.
```

---

## PHASE 4 — Copilot Studio Configuration (~3 hours)

### STEP 4.1 — Create the Copilot

```
1. Go to: copilotstudio.microsoft.com
2. Sign in with your Microsoft 365 / Azure AD account
3. Click: "+ New copilot"
4. Fill in:
   Name:     Product Knowledge Assistant
   Language: English (United States)
   Icon:     (upload your company logo or leave default)
5. Click: "Create"
   ⏳ Wait ~30 seconds
```

### STEP 4.2 — Disable Default Boosted Answers (Optional but Recommended)

The default Copilot Studio uses general web search. Disable it so only your knowledge base is used.

```
Left sidebar → "Settings" → "Generative AI"
Set: "Generative answers" → OFF  (or leave ON if you want fallback to web)
Click: "Save"
```

### STEP 4.3 — Create the HTTP Connector Action

This action calls your AI Foundry Prompt Flow endpoint.

```
Left sidebar → "Actions"
Click: "+ Add an action"
Select: "New action" → "HTTP request"

Fill in:
  Action name:   Call Product Knowledge Agent
  Endpoint URL:  https://product-knowledge-endpoint.eastus2.inference.ml.azure.com/score
  Method:        POST

Headers:
  Click "+ Add header"
  Name:  Authorization
  Value: Bearer YOUR_PROMPT_FLOW_PRIMARY_KEY

  Click "+ Add header"
  Name:  Content-Type
  Value: application/json

Body (JSON template):
{
  "inputs": {
    "question": "{question_input}"
  }
}

Output mapping:
  Add output:
    Name:  agent_response
    Path:  $.outputs.final_response   ← this is the JSON path in the response

Click: "Save"
```

### STEP 4.4 — Create the Main Conversation Topic

```
Left sidebar → "Topics"
Click: "+ Add a topic" → "From blank"
Name: Product Knowledge Question
```

**Configure the Trigger:**
```
In the topic editor, click "Trigger" node:
Type: "Phrases"
Add these example phrases (5–10 minimum, more = better):
  - "tell me about [product]"
  - "how does [product] work"
  - "explain [feature]"
  - "what is the business case for"
  - "show me the architecture"
  - "give me a diagram"
  - "how does [subsystem] relate to"
  - "walk me through the flow"
  - "why do we have"
  - "what happens when"
Click: "Save"
```

**Add a Question node** (to capture the user's full question):
```
Click "+" below the trigger → "Ask a question"
Message to user: "What would you like to know about our products?"
  (or leave empty if you want to directly use what they typed)
Save the answer to variable: user_question (type: Text)
```

**Add an Action node** (call your HTTP connector):
```
Click "+" → "Call an action"
Select: "Call Product Knowledge Agent" (the action you created)
Map inputs:
  question_input → user_question (the variable from above)
Save output:
  agent_response → agent_response_var (create new variable, type: Text)
```

**Add a Message node** (show the response):
```
Click "+" → "Send a message"
Message content: {agent_response_var}
  ← Click the {x} variable picker, select agent_response_var

IMPORTANT — Enable Markdown rendering:
  In the message node, click "..." (options)
  Enable: "Markdown"
  This allows the ## headers and ![image] to render properly.
```

**Add an End Conversation node:**
```
Click "+" → "End conversation"
  (or "Ask another question" if you want to loop)
```

Click **"Save"** on the topic.

### STEP 4.5 — Test Inside Copilot Studio

```
Top right → click "Test your copilot" (chat panel opens on right)
Type: "How does the payment gateway authenticate users?"
Expected:
  - Structured response with 4 sections
  - If diagram requested: image appears inline in the chat
```

**If image does not appear:**
- Verify the blob container "diagrams" has public read access (Step 1.7)
- Verify the diagram URL is HTTPS (not HTTP)
- Check that Markdown rendering is enabled in the message node

### STEP 4.6 — Publish the Copilot

```
Top right → click "Publish"
Click: "Publish" to confirm
⏳ Wait ~2 minutes

After publishing, you can access:
  Left sidebar → "Channels"
```

### STEP 4.7 — Add Channels

**Demo Website (fastest, best for PoC demo):**
```
Left sidebar → "Channels"
Click: "Custom website"
Copy the iframe embed code or the direct URL
Open the URL in a browser — this is your live PoC demo link
```

**Microsoft Teams (for management audience):**
```
Left sidebar → "Channels"
Click: "Microsoft Teams"
Click: "Add to Teams"
Follow the prompts to create a Teams app package
Upload to Teams Admin Center or install directly for yourself
In Teams: search for "Product Knowledge Assistant" in Apps
```

---

## PHASE 5 — Testing & Validation (~3 hours)

### STEP 5.1 — Run Each Test Question

Open the Copilot Studio test panel or the Demo Website URL.

For each of your 15 questions from Phase 0, paste it and verify:

| Check | Expected |
|-------|---------|
| Response has `## Answer` section | Yes — always |
| Response has `## Business Context` section | Yes — always |
| Response has `## Subsystem Explanation` | Yes when relevant |
| Response has `## Related Components` | Yes — always |
| Diagram question shows an image | Yes — either retrieved or generated |
| Image is colored (not B&W) | Yes |
| No hallucinated content | Verify against your source docs |
| Response under 15 seconds | Yes for most questions |

### STEP 5.2 — Debug Common Issues

**Issue: "I don't have information about that"**
- Cause: Document was not indexed or chunk didn't match
- Fix: Go to AI Search → Indexes → product-docs-index → Search explorer
  Run: `search=your question text` and verify documents appear
- If nothing returns: re-run `upload_and_index_docs.py`

**Issue: Diagram appears as broken link `![](url)`**
- Cause: Image URL is not publicly accessible
- Fix: Go to Storage Account → Containers → diagrams → Access policy
  Change to: Blob (anonymous read for blobs only)
- For DALL-E 3 generated URLs: these expire after 24 hours
  Fix: Download the image and re-upload to your blob container, return blob URL instead

**Issue: Response doesn't have the 4-section structure**
- Cause: GPT-4o not following the system prompt exactly
- Fix: In answer_synthesizer node, set Temperature to 0 (not 0.3)
  Also verify the system prompt is in the "system:" section of the Jinja template

**Issue: Intent classifier returns invalid JSON**
- Cause: Model occasionally adds markdown or explanation
- Fix: Add a Python node after intent_classifier to sanitize:
```python
import json, re
def sanitize_json(raw: str) -> str:
    # Strip markdown code fences if present
    clean = re.sub(r"```json\s*|\s*```", "", raw).strip()
    parsed = json.loads(clean)  # validates it's real JSON
    return json.dumps(parsed)
```

### STEP 5.3 — Performance Baseline

Run these timing checks and record results:
```
Question type               | Target  | Actual (fill in)
Product operation (no diag) | < 8s    | ___
Business case (no diag)     | < 8s    | ___
Subsystem reasoning (no diag)| < 10s  | ___
Diagram retrieved           | < 10s   | ___
Diagram generated (DALL-E)  | < 25s   | ___
```

---

## PHASE 6 — PoC Demo Preparation (~2 hours)

### STEP 6.1 — Prepare the Demo Environment

The day before your presentation:
1. Open the Demo Website URL in Chrome (full screen)
2. Have the Teams channel ready on a second tab
3. Test all 5 demo questions — confirm they all work
4. Record a 3-minute screen capture video as fallback (use OBS or Windows Game Bar: Win+G)

### STEP 6.2 — The 5-Question Demo Script

Practice this exact flow:

```
Step 1 — Operational question:
  Type: "How does [your core product] process [main function]?"
  Wait for response. Point out: "Notice the four sections — direct answer, business context,
  subsystem explanation, and related components."

Step 2 — Business case question:
  Type: "Why does [Product A] use a separate authentication service?"
  Wait. Point out: "The agent explains not just what, but WHY — the business rationale."

Step 3 — Subsystem reasoning:
  Type: "How does the notification service relate to the order management system?"
  Wait. Point out: "The agent maps the flow: A → B → C — and explains the dependencies."

Step 4 — Diagram retrieval:
  Type: "Show me the architecture of [Product A]."
  Wait. Point out: "It returned a colored, labeled diagram directly from our knowledge base."

Step 5 — Diagram generation (the wow moment):
  Type: "Give me an architecture diagram for [new subsystem not in knowledge base]."
  Wait. Point out: "This subsystem wasn't in our library — the AI generated a professional
  colored diagram on-the-fly, in real time."
```

### STEP 6.3 — Slide Deck Structure (7 slides)

```
Slide 1 — The Problem (1 min)
  "Our product knowledge lives in PDFs, SharePoint, and tribal knowledge.
   Sales, support, and new engineers spend hours finding answers.
   There's no way to ask a question and get the business WHY."

Slide 2 — The Solution (1 min)
  [Show the architecture diagram from the plan]
  "We built a conversational agent that knows our products deeply.
   It runs entirely inside our Microsoft tenant — AI Foundry + Copilot Studio."

Slide 3 — Live Demo (5 min)
  Run the 5-question script above.

Slide 4 — Key Capabilities (1 min)
  • Structured answers with business context — always
  • Subsystem flow reasoning — explains relationships between components
  • Colored architectural diagrams — retrieved or AI-generated
  • Runs in Microsoft Teams — no new tools for end users

Slide 5 — Technology Stack (30 sec)
  • Azure AI Foundry (Prompt Flow) — orchestration + RAG
  • Azure OpenAI GPT-4o — reasoning and knowledge synthesis
  • DALL-E 3 — colored diagram generation
  • Azure AI Search — intelligent document retrieval
  • Copilot Studio — Teams integration and conversation management

Slide 6 — PoC vs. Production (1 min)
  PoC scope:
    ✅ 3–5 products, manual document upload, 1 language
  Production additions:
    → SharePoint auto-sync for document refresh
    → Azure AD authentication (role-based access)
    → Multi-language support
    → Feedback loop to improve retrieval quality
    → Caching for frequent questions

Slide 7 — Next Steps (30 sec)
  If approved: 3 sprints to production
    Sprint 1: Expand to full product portfolio + SharePoint integration
    Sprint 2: Feedback loop + caching + monitoring
    Sprint 3: Multi-language + mobile + Teams bot with rich cards
```

---

## Full File Structure in This Repository

After completing this PoC, your local files should look like this:

```
02-work/ai-foundry-agent/
└── product-knowledge-agent/
    ├── CLAUDE.md
    ├── README.md
    ├── flow/                              ← Export from AI Foundry
    │   ├── flow.dag.yaml
    │   └── nodes/
    │       ├── intent_classifier.jinja2
    │       ├── rag_retrieval.py
    │       ├── answer_synthesizer.jinja2
    │       ├── diagram_handler.py
    │       └── response_assembler.py
    ├── knowledge-base/
    │   ├── sample-products/
    │   │   ├── payment-gateway_operational_v2.pdf
    │   │   └── auth-service_business-case_v1.pdf
    │   └── sample-diagrams/
    │       ├── payment-gateway_auth-flow_architecture.png
    │       └── order-management_fulfillment-flow_sequence.png
    ├── scripts/
    │   ├── requirements.txt
    │   ├── create_search_index.py
    │   ├── create_diagram_index.py
    │   └── upload_and_index_docs.py
    └── tests/
        ├── test_questions.txt
        └── test_results.md
```

`scripts/requirements.txt`:
```
azure-search-documents==11.4.0
azure-storage-blob==12.19.0
openai==1.12.0
PyMuPDF==1.23.8
promptflow==1.10.0
```

---

## Key Reference Values (Fill In As You Go)

| Variable | Value |
|----------|-------|
| Resource Group | rg-product-knowledge-poc |
| AI Foundry Hub | hub-product-knowledge |
| AI Foundry Project | product-knowledge-agent |
| GPT-4o deployment name | gpt-4o-product |
| DALL-E 3 deployment name | dalle3-diagrams |
| OpenAI endpoint | https://aoai-product-knowledge.openai.azure.com/ |
| OpenAI API key | [copy from Azure Portal] |
| Search service name | srch-product-knowledge |
| Search endpoint | https://srch-product-knowledge.search.windows.net |
| Search admin key | [copy from Azure Portal] |
| Storage account name | productkbstoragepoc |
| Storage connection string | [copy from Azure Portal] |
| Prompt Flow endpoint URL | [copy after deployment] |
| Prompt Flow primary key | [copy after deployment] |
| Copilot Studio demo URL | [copy from Channels] |

---

## Risk Register

| Risk | Trigger | Mitigation |
|------|---------|-----------|
| GPT-4o quota = 0 | Model deployment fails | Request 1 week in advance; fallback: GPT-4-turbo |
| DALL-E 3 not in region | Deployment not found | Try Sweden Central or East US; fallback: diagram retrieval only |
| Diagram URL expires | Links broken next day | DALL-E URLs expire in 24h — save images to blob; return blob URL |
| Markdown doesn't render in Teams | Images show as raw text | Test in Teams 3 days before demo; use Adaptive Cards if needed |
| Document chunking misses content | Agent says "not found" | Tune chunk_size in upload script (try 300 instead of 500) |
| Live demo fails | Connection error | Fallback video + screenshots ready; Prompt Flow test console |
| Response > 30 seconds | Timeout in Copilot Studio | Add caching for top 10 questions; reduce max_tokens |

---

**Status**: Approved — In Execution
**Confirmed**: Hybrid diagram mode (retrieve + DALL-E 3) | Placeholder sample content | Azure subscription exists
**Next Action**: Phase 3 code execution — local repo scaffolding in progress
**Estimated Total**: ~3 working days to live PoC demo
