# CLAUDE.md — Product Knowledge Agent

## What This Is

A conversational AI agent over the company product portfolio, deployed on Azure AI Foundry + Copilot Studio.

**Status**: PoC — building toward management presentation.

## Architecture

```
User question (Teams / web)
    → Copilot Studio topic
    → HTTP POST to AI Foundry Prompt Flow endpoint
    → [intent_classifier] → [rag_retrieval] → [answer_synthesizer]
                                            → [diagram_handler]
    → [response_assembler]
    → Structured Markdown response with optional colored diagram
```

## Key Capabilities

1. **Structured answers** — every response has: Answer, Business Context, Subsystem Explanation, Related Components
2. **Colored diagrams** — retrieves stored PNG from knowledge base or generates via DALL-E 3
3. **Hybrid RAG** — Azure AI Search with vector + keyword + semantic ranking
4. **Graceful degradation** — if diagram generation fails, text answer still returns

## Directory Layout

```
product-knowledge-agent/
├── flow/                        ← Prompt Flow files (export/import to AI Foundry)
│   ├── flow.dag.yaml            ← Flow definition (node graph)
│   └── nodes/
│       ├── intent_classifier.jinja2
│       ├── rag_retrieval.py
│       ├── answer_synthesizer.jinja2
│       ├── diagram_handler.py
│       └── response_assembler.py
├── knowledge-base/
│   ├── sample-products/         ← Placeholder product docs (replace with real PDFs)
│   └── sample-diagrams/         ← Diagram metadata JSON (update with real blob URLs)
├── scripts/                     ← Run locally to create indexes + upload content
│   ├── requirements.txt
│   ├── create_search_index.py   ← Creates product-docs-index in Azure AI Search
│   ├── create_diagram_index.py  ← Creates diagram-metadata-index
│   └── upload_and_index_docs.py ← Chunks PDFs, generates embeddings, uploads to index
└── tests/
    ├── test_questions.txt        ← 15 questions to validate the agent
    └── test_results.md           ← Fill in after testing
```

## Azure Resources

| Resource | Name | Notes |
|----------|------|-------|
| Resource Group | rg-product-knowledge-poc | All PoC resources here |
| AI Foundry Hub | hub-product-knowledge | East US 2 |
| AI Foundry Project | product-knowledge-agent | Inside hub |
| GPT-4o deployment | gpt-4o-product | 80K TPM |
| DALL-E 3 deployment | dalle3-diagrams | 15 img/min |
| AI Search | srch-product-knowledge | Standard S1 |
| Blob Storage | productkbstoragepoc | Containers: product-docs, diagrams |

## Connections Needed in Prompt Flow

- `aoai-product-connection` — Azure OpenAI
- `search-product-connection` — Azure AI Search

## Diagram Strategy

- **Retrieve first**: If diagram-metadata-index returns a match with score ≥ 0.3 and a blob URL exists → return that URL
- **Generate fallback**: If no match → call DALL-E 3 with a detailed colored-diagram prompt → return generated URL
- **Note**: DALL-E 3 URLs expire in 24h. For persistent diagrams, download and re-upload to blob storage.

## Running the Scripts

```bash
cd scripts
pip install -r requirements.txt

# 1. Create indexes (run once)
python create_search_index.py
python create_diagram_index.py

# 2. Upload and index product docs (re-run when docs change)
python upload_and_index_docs.py
```

## Testing

After deployment, test with `tests/test_questions.txt`.
Record results in `tests/test_results.md`.

## Plan Reference

Full implementation plan: `../../../../.plans/PLAN-product-knowledge-agent-poc-2026-02-27.md`
