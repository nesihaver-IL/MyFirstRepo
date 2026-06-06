"""
Node: rag_retrieval
Performs hybrid RAG retrieval against Azure AI Search.
Returns doc_chunks, diagrams, intents, product_hint, subsystem_hint.
"""

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
    openai_embedding_deployment: str = "text-embedding-ada-002",
) -> dict:
    """
    1. Parses intent classification result
    2. Generates embedding for the question
    3. Runs hybrid (vector + keyword + semantic) search on product-docs-index
    4. Runs keyword search on diagram-metadata-index
    Returns: {
        doc_chunks:    list of dicts (content, title, product_id, doc_type, score)
        diagrams:      list of dicts (id, product_id, subsystem, description, diagram_url, score)
        intents:       list of intent strings
        product_hint:  str
        subsystem_hint: str
    }
    """

    # Parse intent result — GPT-4o sometimes adds markdown, strip it
    try:
        import re
        clean = re.sub(r"```json\s*|\s*```", "", intent_json).strip()
        intent_data = json.loads(clean)
    except Exception:
        intent_data = {"intents": ["GENERAL"], "product_hint": "unknown", "subsystem_hint": "unknown"}

    intents       = intent_data.get("intents", ["GENERAL"])
    product_hint  = intent_data.get("product_hint", "unknown")
    subsystem_hint = intent_data.get("subsystem_hint", "unknown")

    # ── Generate question embedding ──────────────────────────────────────────
    aoai = AzureOpenAI(
        api_key=openai_key,
        azure_endpoint=openai_endpoint,
        api_version="2024-02-01",
    )
    embedding_response = aoai.embeddings.create(
        input=question,
        model=openai_embedding_deployment,
    )
    question_vector = embedding_response.data[0].embedding

    credential = AzureKeyCredential(search_key)

    # ── Search product-docs-index (hybrid: vector + keyword + semantic) ──────
    docs_client = SearchClient(
        endpoint=search_endpoint,
        index_name="product-docs-index",
        credential=credential,
    )

    vector_query = VectorizedQuery(
        vector=question_vector,
        k_nearest_neighbors=50,
        fields="content_vector",
    )

    doc_results = docs_client.search(
        search_text=question,
        vector_queries=[vector_query],
        query_type="semantic",
        semantic_configuration_name="product-semantic-config",
        top=5,
        select=["id", "content", "title", "product_id", "subsystem", "doc_type", "source_file"],
    )

    doc_chunks = []
    for result in doc_results:
        doc_chunks.append({
            "content":    result.get("content", ""),
            "title":      result.get("title", ""),
            "product_id": result.get("product_id", ""),
            "doc_type":   result.get("doc_type", ""),
            "score":      result.get("@search.score", 0),
        })

    # ── Search diagram-metadata-index (keyword) ──────────────────────────────
    diagrams_client = SearchClient(
        endpoint=search_endpoint,
        index_name="diagram-metadata-index",
        credential=credential,
    )

    diagram_query = f"{product_hint} {subsystem_hint}".strip()
    if diagram_query in ("unknown unknown", ""):
        diagram_query = question[:100]

    diagram_results = diagrams_client.search(
        search_text=diagram_query,
        top=3,
        select=["id", "product_id", "subsystem", "description", "diagram_url", "diagram_type"],
    )

    diagrams = []
    for result in diagram_results:
        diagrams.append({
            "id":          result.get("id", ""),
            "product_id":  result.get("product_id", ""),
            "subsystem":   result.get("subsystem", ""),
            "description": result.get("description", ""),
            "diagram_url": result.get("diagram_url", ""),
            "score":       result.get("@search.score", 0),
        })

    return {
        "doc_chunks":    doc_chunks,
        "diagrams":      diagrams,
        "intents":       intents,
        "product_hint":  product_hint,
        "subsystem_hint": subsystem_hint,
    }
