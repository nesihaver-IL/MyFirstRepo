# Document Management Guide

Complete guide for managing product documentation in the Knowledge Hub Agent.

## Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Markdown | `.md` | ✅ Recommended - Best for text-based docs |
| Plain Text | `.txt` | ✅ Simple text files |
| PDF | `.pdf` | ✅ Supported - May need preprocessing |
| HTML | `.html`, `.htm` | ✅ Web pages and exported docs |
| Microsoft Word | `.docx` | ⚠️ Requires python-docx (not included by default) |

## File Requirements

- **Maximum file size**: 512 MB per file
- **Maximum total files**: 10,000 per vector store
- **Encoding**: UTF-8 recommended
- **Special characters**: Supported, but test with sample first

## Document Organization

### Recommended Structure

```
docs/
├── getting-started/
│   ├── 01-overview.md
│   ├── 02-quick-start.md
│   └── 03-installation.md
├── user-guide/
│   ├── authentication.md
│   ├── configuration.md
│   └── features.md
├── api-reference/
│   ├── endpoints.md
│   ├── authentication-api.md
│   └── examples.md
├── integration-guides/
│   ├── slack-integration.md
│   ├── teams-integration.md
│   └── webhook-setup.md
└── troubleshooting/
    ├── common-issues.md
    ├── error-codes.md
    └── faq.md
```

### Naming Conventions

**Good**:
- `oauth-authentication-setup.md`
- `api-rate-limits.md`
- `slack-integration-guide.md`

**Bad**:
- `doc1.md`
- `temp.txt`
- `New Document (2).md`

## Chunking Strategy

The system automatically chunks documents for optimal RAG performance.

**Default Settings**:
- **Chunk size**: 1000 characters
- **Chunk overlap**: 200 characters

**Adjust for your needs**:
```python
from src.vector_store import DocumentProcessor

# More context per chunk (better for complex topics)
processor = DocumentProcessor(chunk_size=1500, chunk_overlap=300)

# Smaller chunks (better for precise retrieval)
processor = DocumentProcessor(chunk_size=800, chunk_overlap=150)
```

## Upload Procedures

### Initial Upload

**Step 1: Prepare documents**
```bash
# Organize in docs/ directory
mkdir -p docs/{getting-started,user-guide,api-reference}

# Verify files
find docs/ -type f -name "*.md" | wc -l
```

**Step 2: Upload via Python**
```python
from src.agent import KnowledgeHubAgent, AgentConfig

config = AgentConfig(
    subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
    resource_group=os.getenv("AZURE_RESOURCE_GROUP"),
    project_name=os.getenv("AZURE_PROJECT_NAME")
)

agent = KnowledgeHubAgent(config)
agent.create_vector_store()

# Upload all markdown files
from pathlib import Path
file_paths = [str(p) for p in Path("docs").rglob("*.md")]

print(f"Uploading {len(file_paths)} files...")
file_ids = agent.upload_files(file_paths, update_vector_store=True)
print(f"✅ Uploaded {len(file_ids)} files")
```

### Updating Documents

**Option 1: Upload new version** (Recommended)
```python
# Upload updated file
agent.upload_files(["docs/updated-guide.md"], update_vector_store=True)

# Old version remains in vector store - agent uses most recent
```

**Option 2: Delete and re-upload**
```python
# List files in vector store
files = agent.client.agents.list_vector_store_files(
    vector_store_id=agent.vector_store.id
)

# Find and delete old file
for file in files.data:
    if "old-guide" in file.id:
        agent.client.agents.delete_vector_store_file(
            vector_store_id=agent.vector_store.id,
            file_id=file.id
        )

# Upload new version
agent.upload_files(["docs/new-guide.md"], update_vector_store=True)
```

### Batch Upload

For large document sets:
```python
import time
from pathlib import Path

file_paths = [str(p) for p in Path("docs").rglob("*.md")]
batch_size = 20  # Upload 20 at a time

for i in range(0, len(file_paths), batch_size):
    batch = file_paths[i:i+batch_size]
    print(f"Uploading batch {i//batch_size + 1}/{(len(file_paths)-1)//batch_size + 1}...")
    
    try:
        file_ids = agent.upload_files(batch, update_vector_store=True)
        print(f"  ✅ Uploaded {len(file_ids)} files")
    except Exception as e:
        print(f"  ❌ Batch failed: {e}")
        continue
    
    time.sleep(2)  # Rate limiting

print("✅ All batches complete")
```

## Document Quality

### Best Practices

1. **Clear Structure**
   - Use headings (H1, H2, H3)
   - Short paragraphs
   - Bullet points and lists

2. **Consistent Style**
   - Follow same format across docs
   - Use templates for common doc types

3. **Searchable Keywords**
   - Include terms users will search for
   - Use synonyms ("authenticate" AND "login")

4. **Examples**
   - Include code examples
   - Show before/after
   - Provide step-by-step instructions

5. **Metadata** (for Markdown)
   ```markdown
   ---
   title: "Authentication Setup"
   category: "Getting Started"
   tags: ["auth", "security", "oauth"]
   last_updated: "2025-01-12"
   ---
   
   # Authentication Setup
   ...
   ```

### What to Avoid

❌ **Too much in one file** (>10,000 words)
✅ Split into multiple focused files

❌ **Duplicate content** across multiple files
✅ Use cross-references instead

❌ **Outdated information**
✅ Regular review and update cycle

❌ **No examples**
✅ Include practical examples

## Monitoring Document Performance

### Check What Users Are Asking

```python
# View recent queries (from Application Insights)
# Identify gaps in documentation
```

### Analyze Retrieval Quality

```python
# Test retrieval with common questions
test_questions = [
    "How do I configure authentication?",
    "What are the pricing tiers?",
    "How do I integrate with Slack?"
]

for question in test_questions:
    response = agent.query(question)
    print(f"Q: {question}")
    print(f"A: {response[:200]}...")
    print()
```

## Regular Maintenance

### Monthly Tasks

- [ ] Review and update outdated docs
- [ ] Add docs for new features
- [ ] Remove deprecated content
- [ ] Check for broken links
- [ ] Test sample queries
- [ ] Review user feedback

### Quarterly Tasks

- [ ] Audit all documentation
- [ ] Reorganize if needed
- [ ] Update screenshots
- [ ] Refresh examples
- [ ] Performance review

## Version Control

**Recommended**: Keep docs in Git
```bash
# Track changes
git add docs/
git commit -m "Update authentication documentation"
git push

# Tag releases
git tag -a docs-v2.0 -m "Documentation v2.0"
git push --tags
```

## Backup Strategy

```python
# Export vector store metadata
import json
from datetime import datetime

backup = {
    "date": datetime.now().isoformat(),
    "vector_store_id": agent.vector_store.id,
    "file_count": agent.vector_store.file_counts.total,
    "files": []
}

files = agent.client.agents.list_vector_store_files(
    vector_store_id=agent.vector_store.id
)

for file in files.data:
    backup["files"].append({
        "id": file.id,
        "status": file.status,
        "created_at": str(file.created_at)
    })

# Save backup
with open(f"backup-{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
    json.dump(backup, f, indent=2)
```

---

*Last Updated: 2025-01-12*
