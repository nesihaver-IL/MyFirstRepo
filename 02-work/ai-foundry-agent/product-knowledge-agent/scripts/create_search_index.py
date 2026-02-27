"""
create_search_index.py
Creates the product-docs-index in Azure AI Search.

Run once (or re-run to update the schema):
    python create_search_index.py

Fields:
    id             — chunk identifier (key)
    content        — the document text chunk (searchable)
    title          — document title (searchable, filterable)
    product_id     — e.g. "payment-gateway" (filterable, facetable)
    subsystem      — e.g. "authentication" (filterable, facetable)
    doc_type       — "operational" | "business_case" | "architecture" | "general"
    source_file    — original filename (for traceability)
    content_vector — embedding for vector search (1536 dims, ada-002)
"""

import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    SemanticConfiguration,
    SemanticSearch,
    SemanticPrioritizedFields,
    SemanticField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

# ── FILL THESE IN (or set as environment variables in .env) ───────────────────
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT", "https://srch-product-knowledge.search.windows.net")
SEARCH_ADMIN_KEY = os.getenv("SEARCH_ADMIN_KEY", "YOUR_SEARCH_ADMIN_KEY")
INDEX_NAME = "product-docs-index"
# ─────────────────────────────────────────────────────────────────────────────

credential = AzureKeyCredential(SEARCH_ADMIN_KEY)
index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=credential)

fields = [
    SimpleField(name="id",          type=SearchFieldDataType.String, key=True, filterable=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchableField(name="title",   type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="product_id",  type=SearchFieldDataType.String, filterable=True, facetable=True),
    SimpleField(name="subsystem",   type=SearchFieldDataType.String, filterable=True, facetable=True),
    SimpleField(name="doc_type",    type=SearchFieldDataType.String, filterable=True, facetable=True),
    SimpleField(name="source_file", type=SearchFieldDataType.String, retrievable=True),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,          # text-embedding-ada-002
        vector_search_profile_name="vector-profile",
    ),
]

vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="hnsw-algo")],
    profiles=[VectorSearchProfile(name="vector-profile", algorithm_configuration_name="hnsw-algo")],
)

semantic_config = SemanticConfiguration(
    name="product-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        content_fields=[SemanticField(field_name="content")],
        keywords_fields=[
            SemanticField(field_name="title"),
            SemanticField(field_name="product_id"),
        ],
    ),
)

index = SearchIndex(
    name=INDEX_NAME,
    fields=fields,
    vector_search=vector_search,
    semantic_search=SemanticSearch(configurations=[semantic_config]),
)

index_client.create_or_update_index(index)
print(f"✅ Index '{INDEX_NAME}' created (or updated) at {SEARCH_ENDPOINT}")
