"""
create_diagram_index.py
Creates the diagram-metadata-index in Azure AI Search and loads initial diagram metadata.

Run once (or re-run to refresh the diagram list):
    python create_diagram_index.py

Edit the `diagrams` list at the bottom to match the PNGs you uploaded to blob storage.
One entry per diagram file.
"""

import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

# ── FILL THESE IN (or set in .env) ────────────────────────────────────────────
SEARCH_ENDPOINT  = os.getenv("SEARCH_ENDPOINT",  "https://srch-product-knowledge.search.windows.net")
SEARCH_ADMIN_KEY = os.getenv("SEARCH_ADMIN_KEY", "YOUR_SEARCH_ADMIN_KEY")
STORAGE_BASE_URL = os.getenv(
    "STORAGE_BASE_URL",
    "https://productkbstoragepoc.blob.core.windows.net/diagrams"
)
INDEX_NAME = "diagram-metadata-index"
# ─────────────────────────────────────────────────────────────────────────────

credential   = AzureKeyCredential(SEARCH_ADMIN_KEY)
index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=credential)

# ── Create the index schema ──────────────────────────────────────────────────
fields = [
    SimpleField(name="id",           type=SearchFieldDataType.String, key=True),
    SearchableField(name="description", type=SearchFieldDataType.String),
    SearchableField(name="keywords",    type=SearchFieldDataType.String),
    SimpleField(name="product_id",   type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="subsystem",    type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="diagram_url",  type=SearchFieldDataType.String, retrievable=True),
    SimpleField(name="diagram_type", type=SearchFieldDataType.String, filterable=True),
    # diagram_type: "architecture" | "sequence" | "flow" | "component"
]

index = SearchIndex(name=INDEX_NAME, fields=fields)
index_client.create_or_update_index(index)
print(f"✅ Index '{INDEX_NAME}' created (or updated).")

# ── Load diagram metadata records ────────────────────────────────────────────
# Edit this list — add one entry for each colored PNG you uploaded to blob storage.
# Naming convention: {product-id}_{subsystem}_{diagram-type}.png
diagrams = [
    {
        "id":           "payment-gateway_auth-flow_architecture",
        "product_id":   "payment-gateway",
        "subsystem":    "authentication-flow",
        "diagram_type": "architecture",
        "description":  (
            "Architecture diagram showing the authentication flow of the payment gateway. "
            "Includes token validation, OAuth2 handshake, and session management components."
        ),
        "keywords":     "payment gateway authentication auth token OAuth JWT session flow architecture",
        "diagram_url":  f"{STORAGE_BASE_URL}/payment-gateway_auth-flow_architecture.png",
    },
    {
        "id":           "order-management_fulfillment-flow_sequence",
        "product_id":   "order-management",
        "subsystem":    "fulfillment-flow",
        "diagram_type": "sequence",
        "description":  (
            "Sequence diagram showing the order fulfillment flow from order placement "
            "to delivery confirmation."
        ),
        "keywords":     "order management fulfillment delivery sequence flow warehouse shipping",
        "diagram_url":  f"{STORAGE_BASE_URL}/order-management_fulfillment-flow_sequence.png",
    },
    {
        "id":           "auth-service_overview_architecture",
        "product_id":   "auth-service",
        "subsystem":    "overview",
        "diagram_type": "architecture",
        "description":  (
            "High-level architecture overview of the authentication service. "
            "Shows identity provider integrations, token issuance, and session store."
        ),
        "keywords":     "authentication service identity provider SSO SAML OAuth token session",
        "diagram_url":  f"{STORAGE_BASE_URL}/auth-service_overview_architecture.png",
    },
    # ← ADD MORE entries here for each additional diagram you uploaded
]

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=credential,
)
result = search_client.upload_documents(documents=diagrams)
succeeded = sum(1 for r in result if r.succeeded)
print(f"✅ Uploaded {succeeded}/{len(diagrams)} diagram metadata records.")
