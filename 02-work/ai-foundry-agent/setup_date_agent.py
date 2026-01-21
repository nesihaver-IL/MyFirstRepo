#!/usr/bin/env python3
"""
Setup script for Date Extraction Agent

This script helps you set up and use the specialized date extraction agent.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.date_extraction_agent import DateExtractionAgent


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def validate_config():
    """Validate Azure configuration."""
    required = {
        "AZURE_SUBSCRIPTION_ID": "Azure subscription ID",
        "AZURE_RESOURCE_GROUP": "Resource group name",
        "AZURE_PROJECT_NAME": "AI Foundry project name"
    }

    missing = []
    for var, desc in required.items():
        if not os.getenv(var):
            missing.append(f"   ❌ {var} ({desc})")

    if missing:
        print_header("❌ Configuration Missing")
        print("\nPlease set these environment variables in your .env file:\n")
        for item in missing:
            print(item)
        print("\nExample .env file:")
        print("```")
        print("AZURE_SUBSCRIPTION_ID=12345678-1234-1234-1234-123456789abc")
        print("AZURE_RESOURCE_GROUP=knowledge-hub-rg")
        print("AZURE_PROJECT_NAME=knowledge-hub-dev-project")
        print("```")
        return False

    return True


def setup_agent():
    """Set up the date extraction agent."""
    print_header("🤖 Date Extraction Agent Setup")

    # Validate config
    if not validate_config():
        return None

    # Get configuration
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    project_name = os.getenv("AZURE_PROJECT_NAME")

    print(f"\n📋 Configuration:")
    print(f"   Subscription: {subscription_id[:8]}...")
    print(f"   Resource Group: {resource_group}")
    print(f"   Project: {project_name}")

    # Initialize agent
    print("\n🔧 Initializing agent...")
    try:
        agent = DateExtractionAgent(
            subscription_id=subscription_id,
            resource_group=resource_group,
            project_name=project_name
        )
        print("   ✅ Agent initialized")
        return agent
    except Exception as e:
        print(f"   ❌ Error initializing agent: {e}")
        return None


def upload_documents_interactive(agent):
    """Interactive document upload."""
    print_header("📄 Document Upload")

    print("\n📂 Recommended document structure:")
    print("""
    docs/
    ├── company/
    │   ├── history.md          (Company founding, milestones)
    │   ├── press-releases.md   (Major announcements with dates)
    │   └── timeline.md         (Company timeline)
    ├── product/
    │   ├── release-notes.md    (Product release dates)
    │   ├── roadmap.md          (Future release dates)
    │   ├── changelog.md        (Version history)
    │   └── versions.md         (All version dates)
    ├── contracts/
    │   ├── agreements.md       (Contract dates, renewals)
    │   └── deadlines.md        (Important deadlines)
    └── events/
        ├── conferences.md      (Event dates)
        └── webinars.md         (Webinar schedule)
    """)

    print("\n💡 Enter document paths (one per line, empty line to finish):")
    print("   Example: docs/company/history.md")

    file_paths = []
    while True:
        path = input("   📄 File path: ").strip()
        if not path:
            break

        if Path(path).exists():
            file_paths.append(path)
            print(f"      ✅ Added: {path}")
        else:
            print(f"      ❌ File not found: {path}")

    if not file_paths:
        print("\n⚠️  No files added. You can upload documents later.")
        return []

    # Upload
    print(f"\n📤 Uploading {len(file_paths)} documents...")
    try:
        file_ids = agent.upload_documents(file_paths)
        print(f"   ✅ Uploaded {len(file_ids)} documents")
        return file_ids
    except Exception as e:
        print(f"   ❌ Error uploading documents: {e}")
        return []


def query_agent_interactive(agent):
    """Interactive query interface."""
    print_header("💬 Query the Date Extraction Agent")

    print("\n📋 Example questions you can ask:")
    examples = [
        "When was our product first released?",
        "What are all the version release dates?",
        "Create a timeline of product launches",
        "What happened in March 2024?",
        "What are the upcoming deadlines?",
        "When did the company reach 1M users?",
        "Compare the release dates of v1.0 and v2.0"
    ]

    for i, example in enumerate(examples, 1):
        print(f"   {i}. {example}")

    print("\n" + "-" * 70)
    print("💡 Type your question (or 'quit' to exit):")
    print("-" * 70)

    thread_id = None  # Maintain conversation context

    while True:
        print()
        question = input("❓ Your question: ").strip()

        if not question:
            continue

        if question.lower() in ['quit', 'exit', 'q']:
            break

        # Special commands
        if question.lower().startswith("timeline:"):
            topic = question[9:].strip()
            print(f"\n📅 Extracting timeline for: {topic}")
            try:
                result = agent.extract_timeline(topic)
                print(f"\n{result}\n")
            except Exception as e:
                print(f"❌ Error: {e}")
            continue

        if question.lower() == "upcoming":
            print(f"\n📅 Finding upcoming dates...")
            try:
                result = agent.find_upcoming_dates(90)
                print(f"\n{result}\n")
            except Exception as e:
                print(f"❌ Error: {e}")
            continue

        # Regular query
        print("\n🤔 Searching documents...")
        try:
            result = agent.query_dates(question, thread_id=thread_id)
            thread_id = result["thread_id"]  # Keep context

            print(f"\n💡 Answer:\n")
            print(result["answer"])
            print(f"\n(Thread: {thread_id[:20]}... | Status: {result['status']})")

        except Exception as e:
            print(f"\n❌ Error querying agent: {e}")


def main():
    """Main function."""
    print("\n" + "=" * 70)
    print("  📅 DATE EXTRACTION AGENT - Setup & Query Tool")
    print("=" * 70)

    # Step 1: Setup agent
    agent = setup_agent()
    if not agent:
        return

    # Step 2: Create vector store
    print_header("📦 Vector Store Setup")
    print("\n🔧 Creating vector store for company/product documents...")
    try:
        agent.create_vector_store("company-product-docs")
        print("   ✅ Vector store ready")
    except Exception as e:
        print(f"   ❌ Error creating vector store: {e}")
        return

    # Step 3: Upload documents
    print("\n❓ Do you want to upload documents now? (y/n): ", end="")
    response = input().strip().lower()

    if response == 'y':
        upload_documents_interactive(agent)

    # Step 4: Create agent
    print_header("🤖 Creating Date Extraction Agent")
    print("\n🔧 Configuring specialized date extraction agent...")
    try:
        agent.create_agent()
        print("   ✅ Agent created and ready")
    except Exception as e:
        print(f"   ❌ Error creating agent: {e}")
        return

    # Step 5: Query interface
    print("\n✅ Setup complete! The date extraction agent is ready.")
    print("\n❓ Do you want to query the agent now? (y/n): ", end="")
    response = input().strip().lower()

    if response == 'y':
        query_agent_interactive(agent)

    # Done
    print_header("✅ Session Complete")
    print("\n💡 To query the agent later, run:")
    print("   python setup_date_agent.py")
    print("\n💡 To use in your code:")
    print("""
    from src.agent.date_extraction_agent import DateExtractionAgent

    agent = DateExtractionAgent(subscription_id, resource_group, project_name)
    agent.create_vector_store()
    agent.create_agent()

    # Query dates
    result = agent.query_dates("When was version 2.0 released?")
    print(result["answer"])
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
