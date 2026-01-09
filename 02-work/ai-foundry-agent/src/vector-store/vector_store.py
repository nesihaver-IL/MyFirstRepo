"""Vector Store Manager using Azure AI Search."""

import logging
from typing import List, Dict, Any, Optional
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages vector storage and retrieval using Azure AI Search."""

    def __init__(
        self,
        search_endpoint: str,
        index_name: str,
        credential: Optional[Any] = None,
        openai_endpoint: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-large",
    ):
        """Initialize Vector Store Manager.

        Args:
            search_endpoint: Azure AI Search endpoint URL
            index_name: Name of the search index
            credential: Azure credential (defaults to DefaultAzureCredential)
            openai_endpoint: Azure OpenAI endpoint for embeddings
            openai_api_key: Azure OpenAI API key
            embedding_model: Model name for embeddings
        """
        self.search_endpoint = search_endpoint
        self.index_name = index_name
        self.credential = credential or DefaultAzureCredential()
        self.embedding_model = embedding_model

        # Initialize search clients
        self.index_client = SearchIndexClient(
            endpoint=search_endpoint, credential=self.credential
        )
        self.search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=self.credential,
        )

        # Initialize OpenAI client for embeddings
        if openai_endpoint and openai_api_key:
            self.openai_client = AzureOpenAI(
                azure_endpoint=openai_endpoint,
                api_key=openai_api_key,
                api_version="2024-08-01-preview",
            )
        else:
            self.openai_client = None

    def create_index(self, vector_dimensions: int = 3072) -> None:
        """Create a new search index with vector search capabilities.

        Args:
            vector_dimensions: Dimensions of the embedding vectors (3072 for text-embedding-3-large)
        """
        # Define index fields
        fields = [
            SearchField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            ),
            SearchField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
                retrievable=True,
            ),
            SearchField(
                name="title",
                type=SearchFieldDataType.String,
                searchable=True,
                retrievable=True,
                filterable=True,
            ),
            SearchField(
                name="category",
                type=SearchFieldDataType.String,
                searchable=True,
                filterable=True,
                facetable=True,
            ),
            SearchField(
                name="metadata",
                type=SearchFieldDataType.String,
                retrievable=True,
            ),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=vector_dimensions,
                vector_search_profile_name="default-profile",
            ),
        ]

        # Configure vector search
        vector_search = VectorSearch(
            profiles=[
                VectorSearchProfile(
                    name="default-profile",
                    algorithm_configuration_name="hnsw-config",
                )
            ],
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="hnsw-config",
                    parameters={
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine",
                    },
                )
            ],
        )

        # Configure semantic search
        semantic_config = SemanticConfiguration(
            name="default-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                content_fields=[SemanticField(field_name="content")],
            ),
        )

        semantic_search = SemanticSearch(
            configurations=[semantic_config],
            default_configuration_name="default-semantic-config",
        )

        # Create the index
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
            semantic_search=semantic_search,
        )

        result = self.index_client.create_or_update_index(index)
        logger.info(f"Created/updated index: {result.name}")

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Azure OpenAI.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")

        response = self.openai_client.embeddings.create(
            input=text, model=self.embedding_model
        )
        return response.data[0].embedding

    def upload_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Upload documents to the vector store.

        Args:
            documents: List of document dictionaries with fields matching the index schema
        """
        # Generate embeddings if not provided
        for doc in documents:
            if "embedding" not in doc and "content" in doc:
                doc["embedding"] = self.get_embedding(doc["content"])

        result = self.search_client.upload_documents(documents=documents)
        logger.info(f"Uploaded {len(documents)} documents")
        return result

    def search(
        self,
        query: str,
        top_k: int = 5,
        use_semantic: bool = True,
        filters: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents using vector and semantic search.

        Args:
            query: Search query text
            top_k: Number of results to return
            use_semantic: Whether to use semantic ranking
            filters: OData filter expression

        Returns:
            List of search results with content and metadata
        """
        # Generate query embedding
        query_vector = self.get_embedding(query)

        # Create vectorized query
        vector_query = VectorizedQuery(
            vector=query_vector, k_nearest_neighbors=top_k, fields="embedding"
        )

        # Perform search
        results = self.search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            query_type="semantic" if use_semantic else "simple",
            semantic_configuration_name="default-semantic-config"
            if use_semantic
            else None,
            select=["id", "title", "content", "category", "metadata"],
            top=top_k,
            filter=filters,
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append(
                {
                    "id": result.get("id"),
                    "title": result.get("title"),
                    "content": result.get("content"),
                    "category": result.get("category"),
                    "metadata": result.get("metadata"),
                    "score": result.get("@search.score"),
                    "reranker_score": result.get("@search.reranker_score"),
                }
            )

        return formatted_results

    def delete_documents(self, document_ids: List[str]) -> None:
        """Delete documents from the vector store.

        Args:
            document_ids: List of document IDs to delete
        """
        documents = [{"id": doc_id} for doc_id in document_ids]
        result = self.search_client.delete_documents(documents=documents)
        logger.info(f"Deleted {len(document_ids)} documents")
        return result

    def get_document_count(self) -> int:
        """Get the total number of documents in the index.

        Returns:
            Total document count
        """
        stats = self.index_client.get_index_statistics(self.index_name)
        return stats.document_count
