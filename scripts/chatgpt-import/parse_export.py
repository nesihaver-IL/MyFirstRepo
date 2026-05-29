#!/usr/bin/env python3
"""
Parse ChatGPT conversations.json export and convert to markdown files.

Usage:
    python scripts/chatgpt-import/parse_export.py

This script:
1. Reads conversations.json from 04-reference/chatgpt-export/raw/
2. Converts each conversation to markdown
3. Saves to 04-reference/chatgpt-export/unorganized/
4. Prints a summary

Requirements:
    - conversations.json in 04-reference/chatgpt-export/raw/
    - Output directory must exist (created by setup)
"""

import json
import os
from pathlib import Path
from datetime import datetime
import re


def sanitize_filename(title, max_length=80):
    """Convert conversation title to safe filename."""
    # Remove special characters, keep alphanumeric, spaces, hyphens
    safe = re.sub(r'[^\w\s-]', '', title)
    # Replace spaces with hyphens
    safe = re.sub(r'\s+', '-', safe)
    # Remove multiple hyphens
    safe = re.sub(r'-+', '-', safe)
    # Limit length and strip trailing hyphens
    safe = safe[:max_length].rstrip('-')
    return safe or "conversation"


def extract_text_content(content_obj):
    """Extract text from a message's content object."""
    if not content_obj:
        return ""

    if content_obj.get("content_type") == "text":
        parts = content_obj.get("parts", [])
        # Parts is usually a list of strings
        if isinstance(parts, list):
            return "".join(str(p) for p in parts)

    return ""


def conversation_to_markdown(conversation):
    """Convert a ChatGPT conversation to markdown format."""
    title = conversation.get("title", "Untitled Conversation")
    messages = conversation.get("messages", [])

    # Start with title and metadata
    md = f"# {title}\n\n"
    md += f"**Export Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md += f"**Conversation ID**: {conversation.get('id', 'unknown')}\n"
    md += f"**Messages**: {len(messages)}\n\n"
    md += "---\n\n"

    # Add each message
    for i, msg in enumerate(messages):
        author = msg.get("author", {})
        role = author.get("role", "unknown")
        name = author.get("name") or role.title()

        # Extract text content
        content = msg.get("content", {})
        text = extract_text_content(content)

        # Skip messages with no text (images, files, etc.)
        if not text.strip():
            continue

        # Format message
        md += f"## {name}\n\n"
        md += f"{text}\n\n"

    return md


def main():
    """Main processing function."""
    repo_root = Path(__file__).parent.parent.parent
    export_dir = repo_root / "04-reference" / "chatgpt-export"
    raw_dir = export_dir / "raw"
    unorganized_dir = export_dir / "unorganized"
    conversations_file = raw_dir / "conversations.json"

    print(f"ChatGPT Conversations Parser")
    print(f"=" * 60)
    print(f"Looking for: {conversations_file}")

    # Check if file exists
    if not conversations_file.exists():
        print(f"\n❌ ERROR: {conversations_file} not found")
        print(f"\nSteps to fix:")
        print(f"1. Go to ChatGPT Settings → Data Controls → Export Data")
        print(f"2. Wait for OpenAI to email you a download link (can take days)")
        print(f"3. Download and extract the ZIP file")
        print(f"4. Place conversations.json in {raw_dir}/")
        print(f"5. Re-run this script")
        return False

    print(f"✓ Found conversations.json\n")

    # Load conversations
    try:
        with open(conversations_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Failed to parse JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Failed to read file: {e}")
        return False

    print(f"Loaded {len(conversations)} conversations")
    print(f"Processing and converting to markdown...\n")

    # Create output directory if needed
    unorganized_dir.mkdir(parents=True, exist_ok=True)

    # Process each conversation
    successful = 0
    skipped = 0

    for conv in conversations:
        try:
            title = conv.get("title", "Untitled")
            conv_id = conv.get("id", "unknown")

            # Convert to markdown
            md_content = conversation_to_markdown(conv)

            # Skip if no content
            if md_content.strip() == "":
                skipped += 1
                continue

            # Create filename
            safe_title = sanitize_filename(title)
            filename = f"{safe_title}.md"
            filepath = unorganized_dir / filename

            # Handle filename collisions
            counter = 1
            base_filepath = filepath
            while filepath.exists():
                name = base_filepath.stem
                filepath = base_filepath.parent / f"{name}_{counter}.md"
                counter += 1

            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)

            successful += 1
            print(f"  ✓ {title[:50]:<50} → {filepath.name}")

        except Exception as e:
            print(f"  ✗ Failed to process conversation: {e}")
            skipped += 1

    # Summary
    print(f"\n" + "=" * 60)
    print(f"Summary:")
    print(f"  ✓ Successfully converted: {successful}")
    print(f"  ✗ Skipped (no content): {skipped}")
    print(f"  📁 Output directory: {unorganized_dir}")
    print(f"\nNext steps:")
    print(f"1. Review generated markdown files in unorganized/")
    print(f"2. Move files to appropriate project folders in projects/")
    print(f"3. Update each project's CONTEXT.md with custom instructions")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
