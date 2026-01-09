"""Example script for uploading documents to the vector store."""

import os
from pathlib import Path
from dotenv import load_dotenv
from src.agent import KnowledgeHubAgent, AgentConfig
from src.vector_store import DocumentProcessor

# Load environment variables
load_dotenv()


def main():
    """Upload documents to the knowledge hub."""

    # Initialize agent configuration
    config = AgentConfig(
        subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
        resource_group=os.getenv("AZURE_RESOURCE_GROUP"),
        project_name=os.getenv("AZURE_PROJECT_NAME"),
    )

    # Create agent
    print("Initializing Knowledge Hub Agent...")
    agent = KnowledgeHubAgent(config)

    # Create or get vector store
    print("Creating vector store...")
    agent.create_vector_store()

    # Upload individual files
    print("\n=== Uploading Individual Files ===")
    file_paths = [
        "docs/product-guide.md",
        "docs/api-reference.md",
        "docs/troubleshooting.md",
    ]

    # Filter to only existing files
    existing_files = [f for f in file_paths if Path(f).exists()]

    if existing_files:
        print(f"Uploading {len(existing_files)} files...")
        file_ids = agent.upload_files(existing_files, update_vector_store=True)
        print(f"Successfully uploaded {len(file_ids)} files")
        for file_path, file_id in zip(existing_files, file_ids):
            print(f"  - {file_path}: {file_id}")
    else:
        print("No files found to upload. Please update the file_paths list.")

    # Upload all files from a directory
    print("\n=== Uploading Files from Directory ===")
    docs_dir = "docs"

    if Path(docs_dir).exists():
        processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)

        # Process all markdown files in directory
        try:
            documents = processor.process_directory(
                docs_dir, category="product-docs", file_pattern="*.md"
            )
            print(
                f"Processed {len(documents)} document chunks from {docs_dir}"
            )

            # Note: For directory uploads, you'd typically use the vector store directly
            # rather than the agent's upload_files method
            print("Documents are ready for vector store upload")

        except Exception as e:
            print(f"Error processing directory: {e}")
    else:
        print(f"Directory {docs_dir} not found")

    print("\nDone!")


if __name__ == "__main__":
    main()
