"""Knowledge Hub Agent using Azure AI Foundry."""

import logging
import time
from typing import Optional, List, Dict, Any
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    Agent,
    AgentThread,
    ThreadMessage,
    MessageRole,
    VectorStore,
    FileSearchTool,
    CodeInterpreterTool,
)
from azure.identity import DefaultAzureCredential
from tenacity import retry, stop_after_attempt, wait_exponential

from .agent_config import AgentConfig

logger = logging.getLogger(__name__)


class KnowledgeHubAgent:
    """Knowledge Hub Agent for product documentation Q&A using RAG."""

    def __init__(self, config: AgentConfig):
        """Initialize the Knowledge Hub Agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.credential = DefaultAzureCredential()

        # Initialize AI Foundry client
        self.client = AIProjectClient(
            credential=self.credential,
            subscription_id=config.subscription_id,
            resource_group_name=config.resource_group,
            project_name=config.project_name,
        )

        self.agent: Optional[Agent] = None
        self.vector_store: Optional[VectorStore] = None

        logger.info(
            f"Initialized KnowledgeHubAgent for project: {config.project_name}"
        )

    def create_vector_store(
        self, file_ids: Optional[List[str]] = None
    ) -> VectorStore:
        """Create or get vector store for file search.

        Args:
            file_ids: List of file IDs to add to the vector store

        Returns:
            VectorStore instance
        """
        # Check if vector store already exists
        try:
            vector_stores = self.client.agents.list_vector_stores()
            for vs in vector_stores:
                if vs.name == self.config.vector_store_name:
                    logger.info(
                        f"Found existing vector store: {vs.id}"
                    )
                    self.vector_store = vs
                    return vs
        except Exception as e:
            logger.warning(
                f"Error checking for existing vector stores: {e}"
            )

        # Create new vector store
        logger.info(
            f"Creating vector store: {self.config.vector_store_name}"
        )
        self.vector_store = self.client.agents.create_vector_store(
            name=self.config.vector_store_name,
            file_ids=file_ids or [],
        )

        logger.info(f"Created vector store: {self.vector_store.id}")
        return self.vector_store

    def upload_files(
        self, file_paths: List[str], update_vector_store: bool = True
    ) -> List[str]:
        """Upload files to AI Foundry for RAG.

        Args:
            file_paths: List of file paths to upload
            update_vector_store: Whether to add files to vector store

        Returns:
            List of uploaded file IDs
        """
        file_ids = []

        for file_path in file_paths:
            try:
                # Upload file
                with open(file_path, "rb") as f:
                    uploaded_file = self.client.agents.upload_file(
                        file=f, purpose="assistants"
                    )
                    file_ids.append(uploaded_file.id)
                    logger.info(
                        f"Uploaded file {file_path}: {uploaded_file.id}"
                    )
            except Exception as e:
                logger.error(f"Error uploading file {file_path}: {e}")
                continue

        # Update vector store with new files
        if update_vector_store and file_ids:
            if not self.vector_store:
                self.create_vector_store(file_ids=file_ids)
            else:
                # Add files to existing vector store
                for file_id in file_ids:
                    self.client.agents.create_vector_store_file(
                        vector_store_id=self.vector_store.id,
                        file_id=file_id,
                    )
                logger.info(
                    f"Added {len(file_ids)} files to vector store"
                )

        return file_ids

    def create_agent(self) -> Agent:
        """Create or get the knowledge hub agent.

        Returns:
            Agent instance
        """
        # Prepare tools
        tools = []

        # Add file search tool
        if self.config.use_file_search:
            tools.append(FileSearchTool())
            logger.info("Enabled file search tool")

        # Add code interpreter tool
        if self.config.enable_code_interpreter:
            tools.append(CodeInterpreterTool())
            logger.info("Enabled code interpreter tool")

        # Prepare tool resources
        tool_resources = {}
        if self.config.use_file_search and self.vector_store:
            tool_resources["file_search"] = {
                "vector_store_ids": [self.vector_store.id]
            }

        # Create agent
        logger.info(f"Creating agent: {self.config.agent_name}")
        self.agent = self.client.agents.create_agent(
            model=self.config.model,
            name=self.config.agent_name,
            instructions=self.config.instructions,
            tools=tools,
            tool_resources=tool_resources if tool_resources else None,
            temperature=self.config.temperature,
        )

        logger.info(
            f"Created agent: {self.agent.id} with model {self.config.model}"
        )
        return self.agent

    def create_thread(self) -> AgentThread:
        """Create a new conversation thread.

        Returns:
            AgentThread instance
        """
        thread = self.client.agents.create_thread()
        logger.info(f"Created thread: {thread.id}")
        return thread

    def add_message(
        self, thread_id: str, content: str, role: str = "user"
    ) -> ThreadMessage:
        """Add a message to a thread.

        Args:
            thread_id: Thread ID
            content: Message content
            role: Message role (user/assistant)

        Returns:
            ThreadMessage instance
        """
        message = self.client.agents.create_message(
            thread_id=thread_id,
            role=role,
            content=content,
        )
        logger.debug(f"Added message to thread {thread_id}")
        return message

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def run_agent(
        self, thread_id: str, instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run the agent on a thread.

        Args:
            thread_id: Thread ID
            instructions: Optional additional instructions for this run

        Returns:
            Run result with status and messages
        """
        if not self.agent:
            raise ValueError(
                "Agent not created. Call create_agent() first."
            )

        # Create run
        run = self.client.agents.create_run(
            thread_id=thread_id,
            agent_id=self.agent.id,
            additional_instructions=instructions,
        )

        logger.info(f"Started run: {run.id}")

        # Poll for completion
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = self.client.agents.get_run(
                thread_id=thread_id, run_id=run.id
            )

            if run.status == "requires_action":
                # Handle tool calls if needed
                logger.info("Run requires action (tool calls)")
                # For now, file_search is handled automatically by the service
                pass

        logger.info(f"Run completed with status: {run.status}")

        # Get messages
        messages = self.client.agents.list_messages(thread_id=thread_id)

        return {
            "status": run.status,
            "run_id": run.id,
            "messages": [
                {
                    "role": msg.role,
                    "content": self._extract_message_content(msg),
                    "created_at": msg.created_at,
                }
                for msg in messages.data
            ],
        }

    def query(
        self,
        question: str,
        thread_id: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> str:
        """Query the knowledge hub agent.

        Args:
            question: User question
            thread_id: Optional existing thread ID
            instructions: Optional additional instructions

        Returns:
            Agent response
        """
        # Create thread if not provided
        if not thread_id:
            thread = self.create_thread()
            thread_id = thread.id

        # Add user message
        self.add_message(thread_id, question)

        # Run agent
        result = self.run_agent(thread_id, instructions)

        # Extract assistant response
        if result["status"] == "completed":
            for msg in result["messages"]:
                if msg["role"] == "assistant":
                    return msg["content"]

        return f"Error: Run status was {result['status']}"

    def get_thread_history(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a thread.

        Args:
            thread_id: Thread ID

        Returns:
            List of messages
        """
        messages = self.client.agents.list_messages(thread_id=thread_id)

        return [
            {
                "role": msg.role,
                "content": self._extract_message_content(msg),
                "created_at": msg.created_at,
            }
            for msg in messages.data
        ]

    def cleanup(self):
        """Cleanup resources."""
        # Delete agent if created
        if self.agent:
            try:
                self.client.agents.delete_agent(self.agent.id)
                logger.info(f"Deleted agent: {self.agent.id}")
            except Exception as e:
                logger.error(f"Error deleting agent: {e}")

    @staticmethod
    def _extract_message_content(message: ThreadMessage) -> str:
        """Extract text content from message.

        Args:
            message: ThreadMessage instance

        Returns:
            Message text content
        """
        if not message.content:
            return ""

        # Handle different content types
        content_parts = []
        for content_item in message.content:
            if hasattr(content_item, "text"):
                # Text content
                text = content_item.text
                if hasattr(text, "value"):
                    content_parts.append(text.value)
                else:
                    content_parts.append(str(text))
            elif hasattr(content_item, "image_file"):
                # Image content
                content_parts.append("[Image]")
            else:
                content_parts.append(str(content_item))

        return "\n".join(content_parts)
