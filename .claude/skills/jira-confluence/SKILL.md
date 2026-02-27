---
name: jira-confluence
description: Automate JIRA and Confluence operations. Use when creating/updating JIRA tickets, writing Confluence pages, or building automation integrations. Triggers on keywords like jira ticket, confluence page, jira automation, create ticket, update board.
---

# JIRA / Confluence

Automate JIRA issue management and Confluence documentation for `02-work/automation-integrations/` and the Azure AI Foundry agent integration.

## Purpose

- Create, update, and transition JIRA issues programmatically
- Write and publish Confluence pages via API
- Build automation workflows between JIRA, Confluence, and AI agents
- Implement the `02-work/automation-integrations/` skeleton project

## When to Use

- Working on `02-work/automation-integrations/`
- Connecting the Azure AI Foundry agent to JIRA/Confluence
- Creating automation rules (e.g., AI-generated tickets from alerts)
- Reading JIRA boards to feed context into AI agents
- Publishing AI-generated summaries to Confluence

## Project Location

```
02-work/automation-integrations/
├── src/
│   ├── jira/          # JIRA API client + operations
│   ├── confluence/    # Confluence API client + operations
│   └── workflows/     # Automation orchestration
├── tests/
└── CLAUDE.md
```

## How It Works

1. **Authenticate**: Use API tokens (stored in `.env`, never in code)
2. **Read**: Query JIRA boards, sprints, issues; read Confluence spaces
3. **Write**: Create/update issues, transition statuses, publish pages
4. **Integrate**: Connect to Azure AI Foundry for AI-powered automation

## Usage

```
/jira-confluence
```

Or natural language:
```
"create a JIRA ticket for this bug"
"update the Confluence page with the deployment summary"
"build the JIRA automation workflow"
"read the current sprint board"
```

## JIRA API Patterns

### Authentication
```python
import requests
from requests.auth import HTTPBasicAuth
import os

JIRA_BASE_URL = os.environ["JIRA_BASE_URL"]  # e.g., https://company.atlassian.net
JIRA_EMAIL = os.environ["JIRA_EMAIL"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {"Accept": "application/json", "Content-Type": "application/json"}
```

### Create Issue
```python
def create_issue(project_key: str, summary: str, description: str, issue_type: str = "Task") -> dict:
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
            },
            "issuetype": {"name": issue_type}
        }
    }
    response = requests.post(
        f"{JIRA_BASE_URL}/rest/api/3/issue",
        json=payload, headers=headers, auth=auth
    )
    response.raise_for_status()
    return response.json()
```

### Transition Issue
```python
def transition_issue(issue_key: str, transition_name: str) -> None:
    # Get available transitions
    transitions = requests.get(
        f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions",
        headers=headers, auth=auth
    ).json()["transitions"]

    transition_id = next(
        t["id"] for t in transitions if t["name"] == transition_name
    )
    requests.post(
        f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/transitions",
        json={"transition": {"id": transition_id}},
        headers=headers, auth=auth
    )
```

### Read Sprint Board
```python
def get_active_sprint_issues(board_id: int) -> list[dict]:
    sprints = requests.get(
        f"{JIRA_BASE_URL}/rest/agile/1.0/board/{board_id}/sprint?state=active",
        headers=headers, auth=auth
    ).json()["values"]

    if not sprints:
        return []

    sprint_id = sprints[0]["id"]
    issues = requests.get(
        f"{JIRA_BASE_URL}/rest/agile/1.0/sprint/{sprint_id}/issue",
        headers=headers, auth=auth
    ).json()["issues"]
    return issues
```

## Confluence API Patterns

### Create/Update Page
```python
CONFLUENCE_BASE_URL = os.environ["CONFLUENCE_BASE_URL"]

def create_page(space_key: str, title: str, content_html: str, parent_id: str = None) -> dict:
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": content_html,
                "representation": "storage"
            }
        }
    }
    if parent_id:
        payload["ancestors"] = [{"id": parent_id}]

    response = requests.post(
        f"{CONFLUENCE_BASE_URL}/rest/api/content",
        json=payload, headers=headers, auth=auth
    )
    response.raise_for_status()
    return response.json()
```

## Azure AI Foundry Integration

Connect JIRA/Confluence to the AI Foundry agent (`02-work/ai-foundry-agent/`):

```python
# Feed JIRA context into AI agent
from azure.ai.projects import AIProjectClient

def get_jira_context_for_ai(issue_key: str) -> str:
    issue = get_issue(issue_key)
    return f"""
    JIRA Issue: {issue['key']}
    Summary: {issue['fields']['summary']}
    Status: {issue['fields']['status']['name']}
    Description: {issue['fields']['description']}
    """

# AI agent generates Confluence content
def ai_to_confluence(prompt: str, space_key: str, title: str) -> dict:
    ai_content = foundry_agent.complete(prompt)
    return create_page(space_key, title, f"<p>{ai_content}</p>")
```

## Environment Variables Required

```bash
# .env (never commit — use .env.example as template)
JIRA_BASE_URL=https://company.atlassian.net
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=your-api-token
CONFLUENCE_BASE_URL=https://company.atlassian.net
```

## Integration with Workflow

```
/exploration-phase (understand automation needs)
    ↓
/create-plan (design workflow)
    ↓
/execute-plan (build JIRA/Confluence integration)
    ↓
/jira-confluence (test operations)
    ↓
/review
    ↓
/update-docs
```

## Security Rules

- API tokens go in `.env` only — never hardcode
- Use least-privilege JIRA roles (read-only unless write needed)
- Log all API calls (required per `02-work/ai-foundry-agent/CLAUDE.md`)
- All integrations must have retry logic with exponential backoff
- Store tokens in Azure Key Vault for production deployments
