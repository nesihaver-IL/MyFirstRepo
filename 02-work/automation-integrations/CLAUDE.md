# CLAUDE.md - Automation Integrations

## Project Overview

Collection of JIRA and Confluence automation integrations for enterprise workflow automation. Automates ticket creation, status transitions, document sync, and cross-platform notifications.

## Technology Stack

| Component | Tech | Notes |
|-----------|------|-------|
| Language | Python 3.11+ | — |
| JIRA API | REST API v3 | Atlassian Cloud or Server |
| Confluence API | REST API v2 | Page creation, updates, attachments |
| Execution | AWS Lambda / Azure Functions | Serverless execution |
| Scheduling | AWS EventBridge / Azure Logic Apps | Scheduled or event-triggered |
| Secrets | AWS Secrets Manager / Azure Key Vault | API tokens, credentials |

## Project Structure

```
automation-integrations/
├── src/
│   ├── jira/               # JIRA automation functions
│   ├── confluence/         # Confluence sync functions
│   ├── shared/             # Common utilities (auth, retry, logging)
│   └── integrations/       # Cross-platform workflows
├── tests/                  # Unit + integration tests
├── infrastructure/         # Terraform (Lambda, EventBridge, IAM)
├── docs/
│   ├── jira-workflows/     # JIRA automation specs
│   └── confluence-templates/  # Confluence page templates
└── scripts/                # Deploy, test, monitor scripts
```

## Development Setup

```bash
# Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure credentials
# JIRA_API_TOKEN=your_token
# CONFLUENCE_API_TOKEN=your_token
# export them or use .env (excluded from git)

# Run tests
python -m pytest tests/ -v

# Run locally (for testing)
python -m src.integrations.main
```

## Claude Code Skills for This Project

| Skill | When to Use |
|-------|-----------|
| `jira-confluence` | Creating/updating tickets, building automation workflows |
| `test-runner` | Running pytest suite before commit |
| `security-audit` | Scanning for hardcoded tokens, OWASP issues |
| `terraform-ops` | Planning/deploying Lambda infrastructure |
| `review` | Self-reviewing automation logic for edge cases |

## Current Integrations

### JIRA Ticket Automation
- Auto-create tickets from external events (webhooks, scheduled tasks)
- Status transitions based on conditions
- Custom field population
- Bulk operations (label application, priority adjustment)

### Confluence Page Sync
- Auto-create pages from templates
- Keep pages synchronized with external data
- Attachment management
- Page versioning and archival

### Cross-Platform Notifications
- Webhook forwarding (Slack, Teams, email)
- Status change notifications
- Integration health monitoring

## Development Guidelines

### API Rate Limits
- **JIRA**: 30 requests per second (cloud), handle 429 responses
- **Confluence**: 30 requests per minute per API token
- **Implementation**: Implement exponential backoff for all calls

### Retry Logic
```python
# All API calls must use retry decorator
@retry(max_attempts=3, backoff_factor=2, exceptions=[APIError])
def create_jira_ticket(...):
    ...
```

### Logging & Monitoring
```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Creating ticket for {project}: {summary}")
logger.error(f"API error: {e}", extra={"api": "jira", "status_code": status})
```

### Pagination
```python
# Always handle pagination for list endpoints
page = 0
while True:
    response = jira.search_issues(jql=query, startAt=page*50, maxResults=50)
    process(response.issues)
    if response.isLast:
        break
    page += 1
```

## Testing

```bash
# Run full test suite
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_jira_automation.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Deployment

```bash
# Deploy infrastructure
cd infrastructure
terraform init
terraform plan -var-file="env.tfvars"
terraform apply -var-file="env.tfvars"

# Deploy Lambda functions
bash scripts/deploy-lambdas.sh

# Verify deployment
bash scripts/test-integration.sh
```

## Monitoring & Troubleshooting

- **CloudWatch/Application Insights**: Monitor Lambda execution and errors
- **API Health**: Check Atlassian status page for outages
- **Rate Limiting**: Monitor API response headers for rate limit counters
- **Logs**: All failures logged with timestamp, context, and error details

## Resources

- [JIRA REST API Documentation](https://developer.atlassian.com/cloud/jira/rest/v3/)
- [Confluence REST API Documentation](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [Atlassian Cloud Rate Limits](https://developer.atlassian.com/cloud/jira/platform/rate-limits/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
