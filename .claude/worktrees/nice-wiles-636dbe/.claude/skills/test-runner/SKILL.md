---
name: test-runner
description: Run tests across projects and report coverage. Use when executing pytest, checking test results, validating Lambda functions, or verifying test coverage. Triggers on keywords like run tests, pytest, test coverage, test suite, validate tests.
---

# Test Runner

Execute and manage test suites across all projects in the workspace.

## Purpose

Enforce the workspace standard: "Write tests for critical functionality."
- Run pytest for Python projects
- Execute Lambda function tests
- Check OAuth flow tests
- Report coverage gaps
- Validate before committing to main

## When to Use

- After `/execute-plan` — validate the implementation
- Before creating a PR or pushing to main
- After modifying Lambda functions
- When debugging test failures
- As part of `/review` workflow

## Project Test Locations

| Project | Test Path | Framework | Key Tests |
|---------|-----------|-----------|-----------|
| Garmin Health Backend | `01-personal/garmin-health/backend/tests/` | pytest | OAuth flow, activity query |
| Garmin Analytics | `01-personal/garmin-health/analytics/` | pytest | data_loader, metrics, charts |
| AWS AI Agent | `01-personal/aws-ai-agent/` | pytest | agent tools, Bedrock calls |
| Azure AI Foundry | `02-work/ai-foundry-agent/tests/` | pytest | unit/, integration/, e2e/ |
| Math Practice | `01-personal/math-practice/` | pytest / JS | exam generation, Hebrew UI |

## How It Works

1. **Detect project**: Identify which project's tests to run
2. **Check dependencies**: Verify venv/requirements are installed
3. **Run tests**: Execute pytest with appropriate flags
4. **Report results**: Summarize pass/fail/coverage
5. **Flag failures**: Surface issues before any commit

## Usage

```
/test-runner
```

Or natural language:
```
"run the garmin backend tests"
"check test coverage for the analytics module"
"why is the oauth test failing?"
"run all tests before I push"
```

## Quick Commands

### Garmin Health Backend
```bash
cd 01-personal/garmin-health/backend

# Install test deps
pip install -r requirements.txt pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=lambda --cov-report=term-missing

# Run specific test file
pytest tests/test_oauth_flow.py -v

# Run specific test
pytest tests/test_activity_query.py::test_fetch_recent_activities -v
```

### Garmin Analytics Dashboard
```bash
cd 01-personal/garmin-health/analytics

pytest tests/ -v --cov=src --cov-report=term-missing
```

### AWS AI Agent
```bash
cd 01-personal/aws-ai-agent

pytest tests/ -v
```

### Azure AI Foundry Agent
```bash
cd 02-work/ai-foundry-agent

# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests (requires Azure auth)
pytest tests/integration/ -v

# End-to-end (requires full stack running)
pytest tests/e2e/ -v

# All tests with coverage
pytest tests/ --cov=src --cov-report=html
```

### Math Practice App
```bash
cd 01-personal/math-practice

# Python tests
pytest tests/ -v

# JS tests (if applicable)
npm test
```

## Coverage Standards

Target coverage by component:

| Component | Minimum | Target |
|-----------|---------|--------|
| Lambda functions | 70% | 85% |
| Data pipeline (ETL) | 60% | 80% |
| AI agent tools | 70% | 85% |
| Analytics modules | 60% | 75% |
| API integrations | 50% | 70% |

## Test Report Format

After running, produce a summary:

```markdown
# Test Results — [Project] — [Date]

## Summary
| Status | Count |
|--------|-------|
| Passed | 12 |
| Failed | 2 |
| Skipped | 1 |
| Coverage | 78% |

## Failed Tests
1. `test_oauth_flow.py::test_token_refresh` — AssertionError: expected 200, got 401
2. `test_activity_query.py::test_empty_result` — KeyError: 'activities'

## Coverage Gaps
- `lambda/analyzer/handler.py` — 45% (critical: add tests for error paths)
- `lambda/fetch/pagination.py` — 60% (add edge case for empty page)

## Recommendation
Fix 2 failing tests before merging. Coverage acceptable except analyzer handler.
```

## Lambda-Specific Testing

### Local Lambda invocation
```bash
# Test Lambda locally with SAM (if installed)
sam local invoke GarminFetchFunction --event tests/events/fetch_event.json

# Or test handler directly
python -c "
from lambda.fetch.handler import lambda_handler
event = {'queryStringParameters': {'days': '7'}}
result = lambda_handler(event, {})
print(result)
"
```

### Mock AWS services in tests
```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_dynamodb():
    with patch('boto3.resource') as mock:
        mock_table = MagicMock()
        mock.return_value.Table.return_value = mock_table
        yield mock_table

def test_save_activity(mock_dynamodb):
    mock_dynamodb.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    # ... test logic
```

## Pre-commit Gate

Before committing any Python code:
```bash
# Run these in order
cd [project-directory]
pytest tests/ -v --tb=short
# If any failures → fix before committing
# If coverage drops below threshold → add tests or document why
```

## Integration with Workflow

```
/execute-plan (write code)
    ↓
/test-runner  ← YOU ARE HERE
    ↓
[Fix failing tests]
    ↓
/review
    ↓
/peer-review (if high-stakes)
    ↓
git commit + PR
```

## Troubleshooting

### Import errors in tests
```bash
# Ensure running from project root with venv active
source venv/bin/activate
export PYTHONPATH=$(pwd)
pytest tests/ -v
```

### Missing `.env` for integration tests
```bash
cp config/.env.example config/.env
# Fill in test values — use sandbox/mock credentials
```

### Tests pass locally but fail in CI
- Check environment variables are set in CI
- Verify Python version matches (`python --version`)
- Check for hardcoded paths (use `os.path` instead)