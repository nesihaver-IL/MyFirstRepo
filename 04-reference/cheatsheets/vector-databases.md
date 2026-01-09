# Vector Databases Cheatsheet

## Quick Comparison

| Database | Type | Best For |
|----------|------|----------|
| Pinecone | Managed | Production, scalability |
| Azure AI Search | Managed | Azure ecosystem |
| OpenSearch | Managed/Self | AWS ecosystem |
| Weaviate | Managed/Self | Hybrid search |
| Chroma | Self-hosted | Development, local |
| FAISS | Library | Prototyping |

## Pinecone

### Setup

```python
from pinecone import Pinecone

pc = Pinecone(api_key="YOUR_API_KEY")
index = pc.Index("my-index")
```

### Upsert

```python
index.upsert(vectors=[
    {"id": "vec1", "values": [0.1, 0.2, ...], "metadata": {"text": "..."}},
    {"id": "vec2", "values": [0.3, 0.4, ...], "metadata": {"text": "..."}}
])
```

### Query

```python
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=5,
    include_metadata=True,
    filter={"category": "docs"}
)
```

## Azure AI Search

### Setup

```python
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

client = SearchClient(
    endpoint="https://xxx.search.windows.net",
    index_name="my-index",
    credential=AzureKeyCredential("key")
)
```

### Vector Search

```python
from azure.search.documents.models import VectorizedQuery

results = client.search(
    search_text=None,
    vector_queries=[
        VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=5,
            fields="contentVector"
        )
    ]
)
```

## Chroma (Local Development)

### Setup

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("my-collection")
```

### Add Documents

```python
collection.add(
    documents=["doc1", "doc2"],
    metadatas=[{"source": "a"}, {"source": "b"}],
    ids=["id1", "id2"]
)
```

### Query

```python
results = collection.query(
    query_texts=["search query"],
    n_results=5,
    where={"source": "a"}
)
```

## FAISS (In-Memory)

### Setup

```python
import faiss
import numpy as np

d = 1536  # dimension
index = faiss.IndexFlatL2(d)
```

### Add Vectors

```python
vectors = np.array([[0.1, 0.2, ...]], dtype='float32')
index.add(vectors)
```

### Search

```python
D, I = index.search(query_vector, k=5)  # D=distances, I=indices
```

## Embedding Models

| Provider | Model | Dimensions |
|----------|-------|------------|
| OpenAI | text-embedding-3-small | 1536 |
| OpenAI | text-embedding-3-large | 3072 |
| AWS | amazon.titan-embed-text-v1 | 1536 |
| Azure | text-embedding-ada-002 | 1536 |
| Cohere | embed-english-v3.0 | 1024 |

## Best Practices

1. **Chunking**: 500-1000 tokens with 10-20% overlap
2. **Metadata**: Store source, date, category for filtering
3. **Indexing**: Use appropriate index type (HNSW for speed)
4. **Hybrid Search**: Combine vector + keyword for better results
5. **Re-ranking**: Use cross-encoder for top results

## Common Patterns

### Hybrid Search Score

```python
final_score = alpha * vector_score + (1 - alpha) * keyword_score
# alpha = 0.5 is a good starting point
```

### Metadata Filtering

```python
# Filter before vector search for efficiency
results = index.query(
    vector=embedding,
    filter={"category": {"$eq": "docs"}, "date": {"$gte": "2024-01-01"}}
)
```
