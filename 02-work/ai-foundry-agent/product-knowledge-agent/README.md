# Product Knowledge Agent — PoC

Conversational AI agent over the company product portfolio.
Deployed on **Azure AI Foundry** (Prompt Flow) + **Copilot Studio** (Teams/web).

## What It Does

Ask it any product question in natural language. It always responds with:

```
## Answer
Direct answer to the question.

## Business Context
Why this feature/component exists — the business problem it solves.

## Subsystem Explanation
Data/control flow between components: A → B → C.

## Related Components
Other subsystems or products that interact with this.
```

If you ask for a diagram, it either retrieves a stored colored PNG from the knowledge base or generates one with DALL-E 3.

## Setup

### Prerequisites

- Azure subscription with Contributor role
- Azure OpenAI quota for GPT-4o and DALL-E 3 (request at least 1 week in advance)
- Copilot Studio license (trial works for PoC)

### Step 1 — Azure Infrastructure

Follow **Phase 1** of `.plans/PLAN-product-knowledge-agent-poc-2026-02-27.md` to create:
- Resource group: `rg-product-knowledge-poc`
- AI Foundry Hub + Project
- GPT-4o deployment (`gpt-4o-product`)
- DALL-E 3 deployment (`dalle3-diagrams`)
- Azure AI Search (`srch-product-knowledge`, Standard S1)
- Blob Storage (`productkbstoragepoc`, containers: `product-docs`, `diagrams`)

### Step 2 — Add Your Product Content

Replace placeholder files in `knowledge-base/sample-products/` with real product PDFs:
```
{product-id}_{doc-type}_{version}.pdf
Example: payment-gateway_operational_v2.pdf
```

Upload colored diagram PNGs to the `diagrams` blob container:
```
{product-id}_{subsystem}_{diagram-type}.png
Example: payment-gateway_auth-flow_architecture.png
```

### Step 3 — Run Scripts

```bash
cd scripts
pip install -r requirements.txt

# Edit each script to fill in your Azure keys (search for "FILL THESE IN")

python create_search_index.py       # Creates product-docs-index
python create_diagram_index.py      # Creates diagram-metadata-index (edit the diagrams list)
python upload_and_index_docs.py     # Chunks PDFs and indexes them
```

### Step 4 — Build the Prompt Flow

In AI Foundry (ai.azure.com):
1. Create a new Standard Flow named `product-knowledge-flow`
2. Add connections: `aoai-product-connection`, `search-product-connection`
3. Create nodes from files in `flow/nodes/` — see the plan for exact field values per node
4. Export the finished flow → replace `flow/flow.dag.yaml` with the export

See **Phase 3** of the plan for step-by-step node configuration with exact fields.

### Step 5 — Copilot Studio

See **Phase 4** of the plan for:
- Creating the copilot
- Adding the HTTP connector action pointing to your Prompt Flow endpoint
- Configuring the conversation topic with Markdown rendering enabled

### Step 6 — Test

Run all 15 questions from `tests/test_questions.txt` and record results in `tests/test_results.md`.

## Quick Reference — Azure Keys to Collect

| What | Where to find it |
|------|-----------------|
| OpenAI API key | Azure Portal → Azure OpenAI resource → Keys and Endpoint |
| Search admin key | Azure Portal → AI Search resource → Keys |
| Storage connection string | Azure Portal → Storage Account → Access keys → key1 connection string |
| Prompt Flow endpoint URL | AI Foundry → Deployments → product-knowledge-endpoint |
| Prompt Flow primary key | AI Foundry → Deployments → Authentication tab |
| Copilot demo URL | Copilot Studio → Channels → Custom website |
