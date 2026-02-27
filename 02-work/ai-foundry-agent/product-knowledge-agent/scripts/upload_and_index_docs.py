"""
upload_and_index_docs.py
Reads PDF files from knowledge-base/sample-products/, chunks them,
generates embeddings, and uploads to Azure AI Search product-docs-index.

Run after create_search_index.py:
    python upload_and_index_docs.py

Re-run whenever your product documents change.

Requirements:
    pip install -r requirements.txt
    # Also: pip install PyMuPDF (for PDF text extraction)

File naming convention (drives metadata extraction):
    {product-id}_{doc-type}_{version}.pdf
    Example: payment-gateway_operational_v2.pdf
"""

import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

load_dotenv()

# ── FILL THESE IN (or set in .env) ────────────────────────────────────────────
STORAGE_CONNECTION_STRING = os.getenv("STORAGE_CONNECTION_STRING", "YOUR_STORAGE_CONNECTION_STRING")
STORAGE_CONTAINER         = "product-docs"

SEARCH_ENDPOINT  = os.getenv("SEARCH_ENDPOINT",  "https://srch-product-knowledge.search.windows.net")
SEARCH_ADMIN_KEY = os.getenv("SEARCH_ADMIN_KEY", "YOUR_SEARCH_ADMIN_KEY")
SEARCH_INDEX     = "product-docs-index"

OPENAI_ENDPOINT       = os.getenv("OPENAI_ENDPOINT", "https://aoai-product-knowledge.openai.azure.com/")
OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY",  "YOUR_OPENAI_API_KEY")
EMBEDDING_MODEL       = "text-embedding-ada-002"

DOCS_FOLDER  = Path(__file__).parent.parent / "knowledge-base" / "sample-products"
CHUNK_SIZE   = 500   # words per chunk
CHUNK_OVERLAP = 50   # words of overlap between consecutive chunks
BATCH_SIZE   = 100   # documents per upload batch
# ─────────────────────────────────────────────────────────────────────────────

aoai_client   = AzureOpenAI(api_key=OPENAI_API_KEY, azure_endpoint=OPENAI_ENDPOINT, api_version="2024-02-01")
search_client = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, AzureKeyCredential(SEARCH_ADMIN_KEY))
blob_service  = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
container_client = blob_service.get_container_client(STORAGE_CONTAINER)


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunks.append(" ".join(words[start:end]))
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def get_embedding(text: str) -> list[float]:
    response = aoai_client.embeddings.create(input=text, model=EMBEDDING_MODEL)
    return response.data[0].embedding


def parse_metadata(filename: str) -> dict:
    """
    Extract product_id and doc_type from filename convention:
        payment-gateway_operational_v2.pdf
        → product_id=payment-gateway, doc_type=operational
    """
    stem = Path(filename).stem
    parts = stem.split("_")
    return {
        "product_id": parts[0] if len(parts) > 0 else "unknown",
        "doc_type":   parts[1] if len(parts) > 1 else "general",
    }


def extract_text_from_pdf(filepath: Path) -> str:
    """Extract text from PDF using PyMuPDF (fitz)."""
    try:
        import fitz
        doc = fitz.open(str(filepath))
        return " ".join(page.get_text() for page in doc)
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install PyMuPDF")


def extract_text_from_md(filepath: Path) -> str:
    """Read plain text from Markdown files (used for placeholder sample content)."""
    return filepath.read_text(encoding="utf-8")


# ── Main processing loop ─────────────────────────────────────────────────────
docs_to_index = []

for filepath in sorted(DOCS_FOLDER.iterdir()):
    if filepath.suffix.lower() not in (".pdf", ".md", ".txt"):
        continue

    print(f"Processing: {filepath.name}")
    meta = parse_metadata(filepath.name)

    # Upload original file to blob (for reference/audit trail)
    try:
        with open(filepath, "rb") as f:
            container_client.upload_blob(name=filepath.name, data=f, overwrite=True)
        print(f"  → Uploaded to blob storage")
    except Exception as e:
        print(f"  ⚠️  Blob upload failed (non-fatal): {e}")

    # Extract text
    if filepath.suffix.lower() == ".pdf":
        full_text = extract_text_from_pdf(filepath)
    else:
        full_text = extract_text_from_md(filepath)

    # Chunk and embed
    chunks = chunk_text(full_text)
    print(f"  → {len(chunks)} chunks")

    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        docs_to_index.append({
            "id":             f"{meta['product_id']}-chunk-{i}-{uuid.uuid4().hex[:8]}",
            "content":        chunk,
            "title":          filepath.stem,
            "product_id":     meta["product_id"],
            "subsystem":      "general",   # refine per document if needed
            "doc_type":       meta["doc_type"],
            "source_file":    filepath.name,
            "content_vector": embedding,
        })

# Upload all chunks in batches
total = len(docs_to_index)
print(f"\nUploading {total} chunks to AI Search index '{SEARCH_INDEX}'...")

for i in range(0, total, BATCH_SIZE):
    batch = docs_to_index[i : i + BATCH_SIZE]
    results = search_client.upload_documents(documents=batch)
    succeeded = sum(1 for r in results if r.succeeded)
    print(f"  Batch {i // BATCH_SIZE + 1}: {succeeded}/{len(batch)} succeeded")

print(f"\n✅ Done. Total chunks indexed: {total}")
