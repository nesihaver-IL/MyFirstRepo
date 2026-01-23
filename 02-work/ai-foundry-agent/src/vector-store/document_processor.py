"""Document processor for preparing documents for vector storage."""

import hashlib
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes documents for ingestion into vector store."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize Document Processor.

        Args:
            chunk_size: Maximum size of text chunks in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for punct in [". ", ".\n", "! ", "?\n", "? "]:
                    last_punct = text.rfind(punct, start, end)
                    if last_punct != -1:
                        end = last_punct + len(punct)
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    def process_document(
        self,
        content: str,
        title: str,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
        source_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Process a document into searchable chunks.

        Args:
            content: Document content
            title: Document title
            category: Document category
            metadata: Additional metadata
            source_id: Source document identifier

        Returns:
            List of processed document chunks ready for upload
        """
        # Chunk the content
        chunks = self.chunk_text(content)

        # Create document records
        documents = []
        for i, chunk in enumerate(chunks):
            # Generate unique ID
            chunk_id = self._generate_id(source_id or title, i)

            # Prepare metadata
            chunk_metadata = {
                "source_id": source_id or title,
                "chunk_index": i,
                "total_chunks": len(chunks),
                **(metadata or {}),
            }

            # Create document record
            doc = {
                "id": chunk_id,
                "content": chunk,
                "title": f"{title} (Part {i + 1}/{len(chunks)})"
                if len(chunks) > 1
                else title,
                "category": category,
                "metadata": json.dumps(chunk_metadata),
            }

            documents.append(doc)

        logger.info(
            f"Processed document '{title}' into {len(documents)} chunks"
        )
        return documents

    def process_file(
        self,
        file_path: str,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Process a file into searchable chunks.

        Args:
            file_path: Path to the file
            category: Document category
            metadata: Additional metadata

        Returns:
            List of processed document chunks
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

        # Use filename as title
        title = path.stem

        # Add file metadata
        file_metadata = {
            "filename": path.name,
            "file_extension": path.suffix,
            **(metadata or {}),
        }

        return self.process_document(
            content=content,
            title=title,
            category=category,
            metadata=file_metadata,
            source_id=str(path),
        )

    def process_directory(
        self,
        directory_path: str,
        category: str = "general",
        file_pattern: str = "*.md",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Process all files in a directory.

        Args:
            directory_path: Path to the directory
            category: Document category
            file_pattern: Glob pattern for files to process
            metadata: Additional metadata

        Returns:
            List of all processed document chunks
        """
        path = Path(directory_path)

        if not path.exists() or not path.is_dir():
            raise ValueError(f"Invalid directory: {directory_path}")

        all_documents = []
        files = list(path.glob(file_pattern))

        logger.info(
            f"Processing {len(files)} files from {directory_path}"
        )

        for file_path in files:
            try:
                docs = self.process_file(
                    str(file_path), category=category, metadata=metadata
                )
                all_documents.extend(docs)
            except Exception as e:
                logger.error(
                    f"Error processing file {file_path}: {e}"
                )
                continue

        logger.info(
            f"Processed {len(files)} files into {len(all_documents)} chunks"
        )
        return all_documents

    @staticmethod
    def _generate_id(source: str, index: int) -> str:
        """Generate a unique ID for a document chunk.

        Args:
            source: Source identifier
            index: Chunk index

        Returns:
            Unique document ID
        """
        content = f"{source}_{index}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
