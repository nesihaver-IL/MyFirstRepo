# Date Extraction Agent - User Guide

## Overview

The Date Extraction Agent is a specialized AI agent that can identify, extract, and derive dates from your company and product documentation using RAG (Retrieval-Augmented Generation).

## Features

✅ **Comprehensive Date Recognition**
- Product release dates
- Company milestones
- Contract dates and deadlines
- Event dates
- Version history
- Policy effective dates

✅ **Multiple Date Formats**
- Standard: 2025-01-12, 01/12/2025
- Written: January 12, 2025
- Relative: Q1 2025, next month
- Fiscal: FY2025, Q3 FY24

✅ **Context-Aware Extraction**
- Provides context for each date
- Cites source documents
- Identifies date relationships
- Creates timelines

✅ **Smart Queries**
- Natural language questions
- Timeline generation
- Date comparisons
- Upcoming dates extraction

## Quick Start

### 1. Configure Environment

Create or edit `.env` file:

```ini
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=knowledge-hub-rg
AZURE_PROJECT_NAME=knowledge-hub-dev-project
```

### 2. Prepare Documents

Organize your company and product documents:

```
docs/
├── company/
│   ├── history.md          # Company founding, milestones
│   ├── press-releases.md   # Major announcements
│   └── timeline.md         # Company timeline
├── product/
│   ├── release-notes.md    # Product releases
│   ├── roadmap.md          # Future plans
│   └── changelog.md        # Version history
├── contracts/
│   └── agreements.md       # Contract dates
└── events/
    └── conferences.md      # Event dates
```

### 3. Run Setup Script

```bash
cd /home/user/MyFirstRepo/02-work/ai-foundry-agent
python setup_date_agent.py
```

Follow the interactive prompts to:
1. ✅ Validate configuration
2. ✅ Create vector store
3. ✅ Upload documents
4. ✅ Create agent
5. ✅ Start querying

## Document Preparation Guidelines

### Best Practices for Date-Rich Documents

**✅ DO:**

1. **Use Consistent Date Formats**
   ```markdown
   Product v2.0 was released on January 15, 2024.
   The beta started on 2023-12-01.
   ```

2. **Provide Context for Dates**
   ```markdown
   On March 10, 2024, we launched the AI feature that increased user engagement by 50%.
   ```

3. **Include Version History**
   ```markdown
   ## Release History
   - v1.0 (2023-01-15): Initial release
   - v1.5 (2023-07-20): Added payment processing
   - v2.0 (2024-01-15): Major UI overhaul
   ```

4. **Document Milestones with Dates**
   ```markdown
   ## Company Milestones
   - Founded: January 10, 2020
   - First Customer: March 2020
   - Series A Funding: September 15, 2021
   - Reached 1M Users: December 2023
   ```

5. **Include Timelines**
   ```markdown
   ## Product Roadmap
   - Q1 2025: AI chatbot feature
   - Q2 2025: Mobile app launch
   - Q3 2025: Enterprise tier
   ```

**❌ DON'T:**

- Use vague timeframes without dates ("recently", "soon")
- Mix multiple date formats inconsistently
- Omit years (always include the year)
- Use ambiguous references ("last quarter" without year)

### Example Document Templates

#### Company History Template

```markdown
# Company History

## Founding
Our company was founded on January 10, 2020 by John Doe and Jane Smith in San Francisco.

## Major Milestones
- **March 2020**: Launched beta product
- **June 15, 2020**: First paying customer
- **September 2021**: Raised $5M Series A (September 15, 2021)
- **January 2022**: Reached 10,000 users
- **December 2023**: Achieved profitability

## Leadership Changes
- January 2020: John Doe, CEO
- July 2022: Jane Smith promoted to CTO
- March 2024: Hired first VP of Sales
```

#### Product Release Notes Template

```markdown
# Product Release Notes

## Version 2.5 (Current)
**Release Date:** November 15, 2024

### New Features
- AI-powered search (launched November 15, 2024)
- Dark mode (launched November 20, 2024)

### Bug Fixes
- Fixed login issue (resolved November 18, 2024)

## Version 2.0
**Release Date:** January 15, 2024

### Major Changes
- Complete UI redesign
- New API v2 (deprecated v1 on June 30, 2024)

## Version 1.0
**Release Date:** March 1, 2023

### Initial Release
- Core functionality
- Basic API
```

#### Roadmap Template

```markdown
# Product Roadmap

## 2025 Roadmap

### Q1 2025 (January - March)
- [ ] AI Chatbot Beta (Target: January 31, 2025)
- [ ] Mobile App Development Kickoff (Start: February 1, 2025)
- [ ] Contract Renewal (Due: March 31, 2025)

### Q2 2025 (April - June)
- [ ] Mobile App Launch (Target: May 15, 2025)
- [ ] Enterprise Tier Beta (Target: June 1, 2025)

### H2 2025
- [ ] Global Expansion (Target: Q3 2025)
- [ ] Advanced Analytics (Target: Q4 2025)
```

#### Contracts Template

```markdown
# Active Contracts

## Cloud Services Contract
- **Provider:** Azure
- **Start Date:** January 1, 2024
- **End Date:** December 31, 2025
- **Renewal Deadline:** October 31, 2025 (notify 60 days prior)

## SaaS License
- **Vendor:** Salesforce
- **Start Date:** March 15, 2024
- **Term:** 1 year
- **Renewal Date:** March 15, 2025
- **Auto-Renewal:** Yes (must cancel by February 15, 2025)
```

## Usage Examples

### Basic Queries

```python
from src.agent.date_extraction_agent import DateExtractionAgent
import os

# Initialize
agent = DateExtractionAgent(
    subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
    resource_group=os.getenv("AZURE_RESOURCE_GROUP"),
    project_name=os.getenv("AZURE_PROJECT_NAME")
)

# Setup
agent.create_vector_store()
agent.upload_documents(["docs/company/history.md", "docs/product/releases.md"])
agent.create_agent()

# Query: When was product launched?
result = agent.query_dates("When was our product first released?")
print(result["answer"])

# Query: Version history
result = agent.query_dates("What are the release dates for all versions?")
print(result["answer"])

# Query: Specific milestone
result = agent.query_dates("When did we reach 1 million users?")
print(result["answer"])
```

### Timeline Extraction

```python
# Extract complete timeline
timeline = agent.extract_timeline("product releases")
print(timeline)

# Extract company milestones timeline
timeline = agent.extract_timeline("company milestones")
print(timeline)

# Extract contract timeline
timeline = agent.extract_timeline("contracts and agreements")
print(timeline)
```

### Find Upcoming Dates

```python
# Find dates in next 90 days
upcoming = agent.find_upcoming_dates(90)
print(upcoming)

# Find dates in next 30 days
upcoming = agent.find_upcoming_dates(30)
print(upcoming)
```

### Compare Dates

```python
# Compare product versions
comparison = agent.compare_dates("version 1.0", "version 2.0")
print(comparison)

# Compare milestones
comparison = agent.compare_dates("Series A funding", "reaching 1M users")
print(comparison)
```

### Multi-Turn Conversation

```python
# Start conversation
result = agent.query_dates("What are the major product releases?")
thread_id = result["thread_id"]
print(result["answer"])

# Follow-up question (maintains context)
result = agent.query_dates(
    "Which of those was the most significant?",
    thread_id=thread_id
)
print(result["answer"])

# Another follow-up
result = agent.query_dates(
    "What features were added in that release?",
    thread_id=thread_id
)
print(result["answer"])
```

## Common Query Patterns

### Product Questions
- "When was [product name] launched?"
- "What are all the version release dates?"
- "When is the next major release planned?"
- "What features were added in Q1 2024?"

### Company Questions
- "When was the company founded?"
- "What are the major milestones and when did they happen?"
- "When did we raise our Series A?"
- "When did we reach [X] users?"

### Contract Questions
- "What contracts are expiring soon?"
- "When is the Azure contract renewal date?"
- "What are all the important contract deadlines?"

### Timeline Questions
- "Create a timeline of all product launches"
- "Show me the company history timeline"
- "What happened in 2024?"
- "What are the Q1 2025 milestones?"

### Comparison Questions
- "Compare the launch dates of product A and product B"
- "How much time passed between Series A and Series B?"
- "What was released first, feature X or feature Y?"

## Response Format

The agent formats responses clearly:

```
📅 **Product Release Dates:**
- Product v1.0: March 1, 2023 (Initial launch - Source: releases.md)
- Product v2.0: January 15, 2024 (Major update - Source: releases.md)
- Product v2.5: November 15, 2024 (Current - Source: releases.md)

📅 **Upcoming Milestones:**
- January 31, 2025: AI Chatbot Beta (Source: roadmap.md)
- March 31, 2025: Contract Renewal Deadline (Source: contracts.md)

📅 **Company History:**
- Founded: January 10, 2020 (Source: history.md)
- Series A: September 15, 2021 (Source: funding.md)
```

## Troubleshooting

### Agent can't find dates

**Problem:** Agent says "No dates found in documentation"

**Solutions:**
1. ✅ Verify documents were uploaded successfully
2. ✅ Check if documents actually contain dates
3. ✅ Ensure dates are in recognizable formats
4. ✅ Wait a few minutes for indexing to complete

### Dates are incorrect

**Problem:** Agent returns wrong dates

**Solutions:**
1. ✅ Check source documents for accuracy
2. ✅ Verify date formats are clear and unambiguous
3. ✅ Update documents if information is outdated
4. ✅ Ask more specific questions with context

### Missing recent dates

**Problem:** Recent dates not showing up

**Solutions:**
1. ✅ Upload the latest version of documents
2. ✅ Wait for vector store to re-index (2-5 minutes)
3. ✅ Verify new documents were added to vector store

## Best Practices

### 1. Regular Updates
- Update documents monthly with new dates
- Re-upload changed files to vector store
- Archive outdated information

### 2. Document Organization
- Keep related dates in the same document
- Use consistent file naming
- Maintain clear document structure

### 3. Date Clarity
- Always include the year
- Use consistent formats within documents
- Provide context for every date

### 4. Query Optimization
- Be specific in questions
- Reference document sections if known
- Use follow-up questions for clarification

### 5. Maintenance
- Review agent responses for accuracy
- Update instructions if needed
- Monitor query patterns to improve documentation

## API Reference

### DateExtractionAgent Class

```python
class DateExtractionAgent:
    def __init__(self, subscription_id, resource_group, project_name, agent_name="date-extraction-agent")
    def create_vector_store(self, name="company-product-docs")
    def upload_documents(self, file_paths: List[str]) -> List[str]
    def create_agent(self, model="gpt-4o", temperature=0.1) -> Agent
    def query_dates(self, question: str, thread_id: Optional[str] = None) -> Dict
    def extract_timeline(self, topic: str) -> str
    def find_upcoming_dates(self, days_ahead: int = 90) -> str
    def compare_dates(self, item1: str, item2: str) -> str
```

### Methods

**query_dates(question, thread_id=None)**
- Query agent about dates
- Maintains conversation context if thread_id provided
- Returns: `{"question": str, "answer": str, "thread_id": str, "status": str}`

**extract_timeline(topic)**
- Creates chronological timeline for a topic
- Returns: Formatted timeline string

**find_upcoming_dates(days_ahead=90)**
- Finds upcoming dates and deadlines
- Returns: List of upcoming dates

**compare_dates(item1, item2)**
- Compares dates between two items
- Returns: Comparison with specific dates

## Support

For issues or questions:
1. Check this guide first
2. Review example documents
3. Verify configuration with `python scripts/validate_config.py`
4. Consult main documentation: `docs/troubleshooting.md`

---

*Last Updated: 2025-01-12*
