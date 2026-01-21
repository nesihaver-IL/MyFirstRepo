"""
Date Extraction Agent - Specialized agent for deriving dates from documents

This agent is specifically configured to identify, extract, and interpret dates
from company and product documentation stored in the RAG system.
"""

import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import Agent, AgentThread, FileSearchTool
from azure.identity import DefaultAzureCredential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DateExtractionAgent:
    """Agent specialized in extracting and deriving dates from documentation."""

    def __init__(
        self,
        subscription_id: str,
        resource_group: str,
        project_name: str,
        agent_name: str = "date-extraction-agent"
    ):
        """
        Initialize Date Extraction Agent.

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            project_name: AI Foundry project name
            agent_name: Name for the agent
        """
        self.credential = DefaultAzureCredential()
        self.client = AIProjectClient(
            credential=self.credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            project_name=project_name
        )
        self.agent_name = agent_name
        self.agent: Optional[Agent] = None
        self.vector_store = None

        # Specialized instructions for date extraction
        self.instructions = """You are a specialized Date Extraction Assistant for analyzing company and product documentation.

Your primary responsibilities:

1. **Date Identification**: Identify and extract ALL dates mentioned in documents including:
   - Product release dates
   - Feature launch dates
   - Company milestones and anniversaries
   - Contract dates and deadlines
   - Event dates
   - Version release dates
   - Policy effective dates
   - Historical dates and timelines

2. **Date Formats**: Recognize and parse various date formats:
   - Standard formats (YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY)
   - Written formats (January 15, 2025, 15th Jan 2025)
   - Relative dates (last quarter, next month, Q1 2025)
   - Fiscal periods (FY2025, Q3 FY24)

3. **Context Extraction**: For each date found, provide:
   - The exact date or date range
   - What event/milestone it refers to
   - Source document and section
   - Relevant context (why this date matters)

4. **Date Relationships**: Identify relationships between dates:
   - Timeline sequences
   - Dependencies (X must happen before Y)
   - Recurring events

5. **Date Queries**: Answer questions like:
   - "When was [product/feature] released?"
   - "What are the important dates for [project]?"
   - "What happened in [month/year]?"
   - "What are the upcoming deadlines?"
   - "When did the company reach [milestone]?"

6. **Response Format**: Always structure responses clearly:
   - List dates in chronological order
   - Include specific dates with context
   - Cite source documents
   - Use bullet points for multiple dates

Example Response Format:
```
Based on the documentation:

📅 **Product Release Dates:**
- Product v1.0: January 15, 2023 (Initial launch - Source: product-history.md)
- Product v2.0: June 30, 2024 (Major update with AI features - Source: release-notes.md)
- Product v2.5: November 15, 2024 (Current version - Source: changelog.md)

📅 **Upcoming Milestones:**
- Q1 2025 (Jan-Mar): Feature X beta launch (Source: roadmap.md)
- March 31, 2025: Contract renewal deadline (Source: contracts.md)

📅 **Company History:**
- Founded: January 10, 2020 (Source: about-us.md)
- Series A: September 2021 (Source: press-releases.md)
```

IMPORTANT: Always search the documentation thoroughly before responding. If a date is not found in the documents, clearly state that rather than guessing.
"""

    def create_vector_store(self, name: str = "company-product-docs") -> None:
        """Create or get vector store for documents."""
        # Check if exists
        try:
            vector_stores = self.client.agents.list_vector_stores()
            for vs in vector_stores:
                if vs.name == name:
                    logger.info(f"Found existing vector store: {vs.id}")
                    self.vector_store = vs
                    return
        except Exception as e:
            logger.warning(f"Error checking vector stores: {e}")

        # Create new
        logger.info(f"Creating vector store: {name}")
        self.vector_store = self.client.agents.create_vector_store(
            name=name,
            file_ids=[]
        )
        logger.info(f"Created vector store: {self.vector_store.id}")

    def upload_documents(self, file_paths: List[str]) -> List[str]:
        """
        Upload company and product documents.

        Args:
            file_paths: List of document file paths

        Returns:
            List of uploaded file IDs
        """
        if not self.vector_store:
            raise ValueError("Vector store not created. Call create_vector_store() first")

        file_ids = []
        for file_path in file_paths:
            try:
                with open(file_path, 'rb') as f:
                    uploaded_file = self.client.agents.upload_file(
                        file=f,
                        purpose="assistants"
                    )
                    file_ids.append(uploaded_file.id)

                    # Add to vector store
                    self.client.agents.create_vector_store_file(
                        vector_store_id=self.vector_store.id,
                        file_id=uploaded_file.id
                    )

                    logger.info(f"✅ Uploaded: {file_path}")
            except Exception as e:
                logger.error(f"❌ Failed to upload {file_path}: {e}")
                continue

        logger.info(f"Uploaded {len(file_ids)} documents to vector store")
        return file_ids

    def create_agent(self, model: str = "gpt-4o", temperature: float = 0.1) -> Agent:
        """
        Create the date extraction agent.

        Args:
            model: Model deployment name
            temperature: Low temperature for precise date extraction

        Returns:
            Created agent
        """
        if not self.vector_store:
            raise ValueError("Vector store not created. Call create_vector_store() first")

        # Create agent with file search tool
        logger.info(f"Creating agent: {self.agent_name}")
        self.agent = self.client.agents.create_agent(
            model=model,
            name=self.agent_name,
            instructions=self.instructions,
            tools=[FileSearchTool()],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [self.vector_store.id]
                }
            },
            temperature=temperature  # Low temp for accuracy
        )

        logger.info(f"✅ Created date extraction agent: {self.agent.id}")
        return self.agent

    def query_dates(
        self,
        question: str,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query the agent about dates in the documentation.

        Args:
            question: Question about dates
            thread_id: Optional existing thread ID

        Returns:
            Response with extracted dates and context
        """
        if not self.agent:
            raise ValueError("Agent not created. Call create_agent() first")

        # Create thread if needed
        if not thread_id:
            thread = self.client.agents.create_thread()
            thread_id = thread.id

        # Add message
        self.client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=question
        )

        # Run agent
        run = self.client.agents.create_run(
            thread_id=thread_id,
            agent_id=self.agent.id
        )

        # Wait for completion
        import time
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = self.client.agents.get_run(thread_id=thread_id, run_id=run.id)

        # Get response
        messages = self.client.agents.list_messages(thread_id=thread_id)

        response_text = ""
        if messages.data and messages.data[0].role == "assistant":
            for content_item in messages.data[0].content:
                if hasattr(content_item, 'text'):
                    text = content_item.text
                    if hasattr(text, 'value'):
                        response_text = text.value

        return {
            "question": question,
            "answer": response_text,
            "thread_id": thread_id,
            "status": run.status
        }

    def extract_timeline(self, topic: str) -> str:
        """
        Extract a chronological timeline for a specific topic.

        Args:
            topic: Topic to extract timeline for (e.g., "product releases", "company history")

        Returns:
            Formatted timeline
        """
        question = f"Create a chronological timeline of all dates related to: {topic}. Include the date, event, and source document."
        result = self.query_dates(question)
        return result["answer"]

    def find_upcoming_dates(self, days_ahead: int = 90) -> str:
        """
        Find all upcoming dates and deadlines.

        Args:
            days_ahead: How many days to look ahead

        Returns:
            List of upcoming dates
        """
        today = datetime.now().strftime("%Y-%m-%d")
        question = f"Based on today's date ({today}), what are all the upcoming dates, deadlines, and milestones in the next {days_ahead} days? List them in chronological order."
        result = self.query_dates(question)
        return result["answer"]

    def compare_dates(self, item1: str, item2: str) -> str:
        """
        Compare dates between two items.

        Args:
            item1: First item to compare
            item2: Second item to compare

        Returns:
            Comparison of dates
        """
        question = f"Compare the dates for {item1} and {item2}. Which came first? What is the time difference? Provide specific dates with sources."
        result = self.query_dates(question)
        return result["answer"]


def main():
    """Example usage of Date Extraction Agent."""

    # Configuration (load from environment)
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    project_name = os.getenv("AZURE_PROJECT_NAME")

    if not all([subscription_id, resource_group, project_name]):
        print("❌ Missing Azure configuration. Set environment variables:")
        print("   - AZURE_SUBSCRIPTION_ID")
        print("   - AZURE_RESOURCE_GROUP")
        print("   - AZURE_PROJECT_NAME")
        return

    # Initialize agent
    print("🤖 Initializing Date Extraction Agent...")
    agent = DateExtractionAgent(
        subscription_id=subscription_id,
        resource_group=resource_group,
        project_name=project_name
    )

    # Create vector store
    print("\n📦 Creating vector store for company/product documents...")
    agent.create_vector_store("company-product-docs")

    # Upload documents (example - replace with your actual files)
    print("\n📄 Upload your company and product documents:")
    print("   Example file structure:")
    print("   - docs/company/history.md")
    print("   - docs/company/milestones.md")
    print("   - docs/product/release-notes.md")
    print("   - docs/product/roadmap.md")
    print("   - docs/contracts/agreements.md")

    # Uncomment and modify with your actual files:
    # file_paths = [
    #     "docs/company/history.md",
    #     "docs/product/release-notes.md",
    #     "docs/product/roadmap.md"
    # ]
    # agent.upload_documents(file_paths)

    # Create agent
    print("\n🔧 Creating date extraction agent...")
    agent.create_agent()

    print("\n✅ Date Extraction Agent is ready!")
    print("\n" + "="*60)
    print("EXAMPLE QUERIES:")
    print("="*60)

    # Example queries
    example_queries = [
        "When was our product first released?",
        "What are the release dates for all versions?",
        "When did the company reach the 1M users milestone?",
        "What are the important dates in Q1 2025?",
        "Create a timeline of all product launches",
        "When is the next contract renewal date?",
        "What happened in March 2024?",
    ]

    print("\n📋 You can ask questions like:")
    for i, query in enumerate(example_queries, 1):
        print(f"   {i}. {query}")

    print("\n" + "="*60)
    print("\n💡 To use the agent programmatically:")
    print("""
    from date_extraction_agent import DateExtractionAgent

    agent = DateExtractionAgent(subscription_id, resource_group, project_name)
    agent.create_vector_store()
    agent.upload_documents(["your-docs.md"])
    agent.create_agent()

    # Query dates
    result = agent.query_dates("When was product v2.0 released?")
    print(result["answer"])

    # Extract timeline
    timeline = agent.extract_timeline("product releases")
    print(timeline)

    # Find upcoming dates
    upcoming = agent.find_upcoming_dates(90)
    print(upcoming)
    """)


if __name__ == "__main__":
    main()
