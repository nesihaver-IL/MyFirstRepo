"""Example API client for Knowledge Hub Agent."""

import requests
from typing import Optional


class KnowledgeHubClient:
    """Client for interacting with Knowledge Hub Agent API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client.

        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> dict:
        """Check API health status."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def create_thread(self) -> str:
        """Create a new conversation thread.

        Returns:
            Thread ID
        """
        response = requests.post(f"{self.base_url}/threads/create")
        response.raise_for_status()
        return response.json()["thread_id"]

    def query(
        self,
        question: str,
        thread_id: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> dict:
        """Query the agent.

        Args:
            question: Question to ask
            thread_id: Optional thread ID for conversation context
            instructions: Optional additional instructions

        Returns:
            Response with answer and thread_id
        """
        payload = {"question": question}

        if thread_id:
            payload["thread_id"] = thread_id
        if instructions:
            payload["instructions"] = instructions

        response = requests.post(
            f"{self.base_url}/query", json=payload
        )
        response.raise_for_status()
        return response.json()

    def upload_files(self, file_paths: list[str]) -> dict:
        """Upload files to the vector store.

        Args:
            file_paths: List of file paths to upload

        Returns:
            Response with file IDs and count
        """
        payload = {"file_paths": file_paths}

        response = requests.post(
            f"{self.base_url}/upload-files", json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_thread_history(self, thread_id: str) -> list:
        """Get conversation history for a thread.

        Args:
            thread_id: Thread ID

        Returns:
            List of messages
        """
        response = requests.get(
            f"{self.base_url}/threads/{thread_id}/history"
        )
        response.raise_for_status()
        return response.json()["messages"]


def main():
    """Demonstrate API client usage."""

    # Initialize client
    client = KnowledgeHubClient("http://localhost:8000")

    # Health check
    print("=== Health Check ===")
    health = client.health_check()
    print(f"Status: {health['status']}")
    print(f"Agent initialized: {health['agent_initialized']}\n")

    # Single query
    print("=== Single Query ===")
    result = client.query("What is this product?")
    print(f"Question: What is this product?")
    print(f"Answer: {result['answer']}\n")

    # Multi-turn conversation
    print("=== Multi-turn Conversation ===")
    thread_id = client.create_thread()
    print(f"Created thread: {thread_id}\n")

    # First question
    result = client.query("What are the main features?", thread_id=thread_id)
    print(f"Q: What are the main features?")
    print(f"A: {result['answer']}\n")

    # Follow-up question
    result = client.query("How do I get started?", thread_id=thread_id)
    print(f"Q: How do I get started?")
    print(f"A: {result['answer']}\n")

    # Get conversation history
    print("=== Conversation History ===")
    history = client.get_thread_history(thread_id)
    for msg in history:
        print(f"{msg['role'].upper()}: {msg['content'][:100]}...")

    print("\nDone!")


if __name__ == "__main__":
    main()
