# RAG Patterns

Retrieval-Augmented Generation patterns and best practices.

## Basic RAG

```
Query → Embed → Retrieve → Augment Prompt → Generate
```

```python
def basic_rag(query):
    # 1. Embed query
    query_embedding = embed(query)

    # 2. Retrieve relevant documents
    docs = vectorstore.similarity_search(query_embedding, k=5)

    # 3. Augment prompt
    context = "\n".join([d.content for d in docs])
    prompt = f"Context: {context}\n\nQuestion: {query}"

    # 4. Generate
    return llm.invoke(prompt)
```

## Advanced Patterns

### Hybrid Search

Combine vector and keyword search.

```python
def hybrid_search(query, alpha=0.5):
    vector_results = vector_search(query)
    keyword_results = keyword_search(query)

    # Reciprocal Rank Fusion
    combined = rrf_merge(vector_results, keyword_results)
    return combined[:k]
```

### Re-ranking

Use cross-encoder for better relevance.

```python
def rerank(query, docs, top_k=3):
    # Initial retrieval (more docs)
    candidates = retrieve(query, k=20)

    # Re-rank with cross-encoder
    scores = cross_encoder.predict([(query, d.content) for d in candidates])

    # Return top results
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in ranked[:top_k]]
```

### Query Expansion

Generate multiple queries for better coverage.

```python
def query_expansion(query):
    expansion_prompt = f"""
    Generate 3 alternative phrasings for this question:
    {query}
    """
    alternatives = llm.invoke(expansion_prompt)

    # Retrieve for each query
    all_docs = []
    for q in [query] + alternatives:
        all_docs.extend(retrieve(q))

    # Deduplicate and rank
    return dedupe_and_rank(all_docs)
```

### HyDE (Hypothetical Document Embeddings)

Generate hypothetical answer, then search.

```python
def hyde_search(query):
    # Generate hypothetical answer
    hypo_prompt = f"Write a detailed answer to: {query}"
    hypothetical_doc = llm.invoke(hypo_prompt)

    # Search using hypothetical doc embedding
    embedding = embed(hypothetical_doc)
    return vectorstore.similarity_search(embedding)
```

### Self-Query

Let LLM generate filters from natural language.

```python
def self_query(query):
    # Extract filters from query
    filter_prompt = f"""
    Extract search filters from: "{query}"
    Output JSON: {{"category": ..., "date_range": ...}}
    """
    filters = llm.invoke(filter_prompt)

    # Apply filters to search
    return vectorstore.search(query, filter=filters)
```

## Chunking Strategies

### Fixed Size

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
```

### Semantic Chunking

```python
def semantic_chunk(text):
    sentences = split_sentences(text)
    chunks = []
    current_chunk = []

    for sent in sentences:
        if should_split(current_chunk, sent):
            chunks.append(join(current_chunk))
            current_chunk = [sent]
        else:
            current_chunk.append(sent)

    return chunks
```

### Parent-Child

```python
# Store small chunks for retrieval
child_chunks = split(doc, size=200)
# Link to larger parent for context
parent_chunks = split(doc, size=2000)
# Retrieve child, return parent
```

## Evaluation Metrics

| Metric | Measures | Range |
|--------|----------|-------|
| Recall@K | % relevant in top K | 0-1 |
| MRR | Rank of first relevant | 0-1 |
| NDCG | Ranking quality | 0-1 |
| Faithfulness | Answer from context | 0-1 |
| Relevance | Answer addresses query | 0-1 |

## Best Practices

1. **Chunk size**: 500-1000 tokens typically optimal
2. **Overlap**: 10-20% prevents context loss
3. **Metadata**: Always store source, date, category
4. **Top-K**: Start with K=5, adjust based on context window
5. **Evaluation**: Test with known Q&A pairs
6. **Filtering**: Use metadata to narrow search space
7. **Caching**: Cache embeddings for repeated queries
