"""Basic usage example for Knowledge Hub Agent."""

import os
from dotenv import load_dotenv
from src.agent import KnowledgeHubAgent, AgentConfig

# Load environment variables
load_dotenv()


def main():
    """Demonstrate basic agent usage."""

    # Initialize agent configuration
    config = AgentConfig(
        subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
        resource_group=os.getenv("AZURE_RESOURCE_GROUP"),
        project_name=os.getenv("AZURE_PROJECT_NAME"),
        temperature=0.3,
    )

    # Create agent
    print("Initializing Knowledge Hub Agent...")
    agent = KnowledgeHubAgent(config)

    # Create vector store
    print("Creating vector store...")
    agent.create_vector_store()

    # Upload sample documentation (optional)
    # Uncomment and update paths to your documentation
    # print("Uploading documentation...")
    # file_paths = [
    #     "docs/product-guide.md",
    #     "docs/api-reference.md",
    # ]
    # file_ids = agent.upload_files(file_paths, update_vector_store=True)
    # print(f"Uploaded {len(file_ids)} files")

    # Create agent
    print("Creating agent...")
    agent.create_agent()

    # Single query example
    print("\n=== Single Query Example ===")
    question = "What is this product about?"
    print(f"Question: {question}")
    response = agent.query(question)
    print(f"Answer: {response}\n")

    # Multi-turn conversation example
    print("=== Multi-turn Conversation Example ===")
    thread = agent.create_thread()
    print(f"Created thread: {thread.id}")

    # First question
    question1 = "What are the main features?"
    print(f"\nUser: {question1}")
    agent.add_message(thread.id, question1)
    result = agent.run_agent(thread.id)
    if result["messages"]:
        print(f"Agent: {result['messages'][0]['content']}")

    # Follow-up question
    question2 = "How do I get started?"
    print(f"\nUser: {question2}")
    agent.add_message(thread.id, question2)
    result = agent.run_agent(thread.id)
    if result["messages"]:
        print(f"Agent: {result['messages'][0]['content']}")

    # Cleanup
    print("\n=== Cleanup ===")
    agent.cleanup()
    print("Done!")


if __name__ == "__main__":
    main()
