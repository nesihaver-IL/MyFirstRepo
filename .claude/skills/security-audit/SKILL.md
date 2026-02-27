---
name: security-audit
description: Audit code for security vulnerabilities, exposed secrets, and OWASP issues. Use when scanning for hardcoded credentials, reviewing AWS IAM policies, checking .env patterns, or enforcing security standards. Triggers on keywords like security scan, check secrets, audit credentials, owasp, security review.
---

# Security Audit

Enforce the workspace security standard: "No secrets in code, follow security best practices."

## Purpose

- Detect hardcoded credentials, API keys, and tokens
- Verify `.env.example` patterns are used correctly
- Review AWS IAM policies for least-privilege
- Check OWASP Top 10 vulnerabilities in API/Lambda code
- Validate Azure Key Vault usage in work projects
- Gate commits that violate security standards

## When to Use

- Before any `git commit` on files containing API integrations
- Before `terraform apply` (IAM policy review)
- After adding new Lambda functions or API endpoints
- When reviewing `02-work/` code (company security policies apply)
- As part of pre-PR checklist

## Scope by Project

| Project | Critical Checks |
|---------|----------------|
| `garmin-health/backend/` | Lambda env vars, IAM roles, DynamoDB access |
| `aws-ai-agent/` | Bedrock permissions, API keys, S3 policies |
| `ai-foundry-agent/` | Azure Key Vault usage, no plaintext secrets |
| `automation-integrations/` | JIRA/Confluence API tokens, retry logic |
| All projects | `.env` not committed, no hardcoded credentials |

## How It Works

1. **Scan for secrets**: Pattern-match for common credential formats
2. **Check `.gitignore`**: Verify `.env` and `*.tfvars` are excluded
3. **Review IAM**: Verify least-privilege on Lambda roles
4. **Check API patterns**: Validate env var usage at system boundaries
5. **OWASP scan**: Review API endpoints for injection, auth bypass, etc.
6. **Report**: Severity-ranked findings with fixes

## Usage

```
/security-audit
```

Or natural language:
```
"scan for secrets before I commit"
"check the IAM policy on this Lambda role"
"audit the JIRA integration for OWASP issues"
"verify no API keys are hardcoded"
```

## Secret Pattern Detection

Patterns to flag immediately (critical — never commit):

```python
DANGEROUS_PATTERNS = [
    r'sk-ant-[a-zA-Z0-9]{20,}',          # Anthropic API key
    r'AKIA[0-9A-Z]{16}',                   # AWS Access Key ID
    r'(?i)(api[_-]?key|secret|password|token)\s*=\s*["\'][^"\']{8,}',  # Generic secrets
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',  # Azure client secrets
    r'-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----',  # Private keys
]
```

### Quick scan command
```bash
# Scan staged files for secrets before commit
git diff --cached | grep -iE "(api_key|secret|password|token|AKIA|sk-ant-)" | grep -v ".example"

# Scan entire project (excluding examples and tests)
grep -rn --include="*.py" --include="*.js" --include="*.ts" \
  -E "(api_key|secret_key|password)\s*=\s*['\"][^'\"]{8,}" \
  --exclude-pattern="*.example" \
  01-personal/ 02-work/
```

## `.gitignore` Verification

Every project must exclude:
```
# Required in .gitignore
.env
*.tfvars
terraform.tfstate
terraform.tfstate.backup
.terraform/
__pycache__/
*.pyc
venv/
node_modules/
```

Verify:
```bash
# Check .env is ignored
git check-ignore -v 01-personal/garmin-health/backend/config/.env
# Expected: .gitignore:<line>:.env  config/.env

# Confirm .env.example IS tracked (safe — no real values)
git ls-files 01-personal/garmin-health/backend/config/.env.example
```

## IAM Least-Privilege Review

For each Lambda function in `garmin-health/backend/`:

```hcl
# GOOD — scoped to specific table and actions
resource "aws_iam_role_policy" "lambda_dynamodb" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:Query"]
      Resource = "arn:aws:dynamodb:*:*:table/garmin-*"
    }]
  })
}

# BAD — over-permissive
resource "aws_iam_role_policy" "lambda_dynamodb_bad" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = "dynamodb:*"       # Too broad
      Resource = "*"                 # Too broad
    }]
  })
}
```

## OWASP Top 10 Checks (API/Lambda)

### Injection
```python
# BAD — SQL/NoSQL injection risk
def query_activities(user_id):
    return table.query(KeyConditionExpression=f"userId = {user_id}")  # ❌

# GOOD — parameterized
def query_activities(user_id: str):
    return table.query(
        KeyConditionExpression=Key('userId').eq(user_id)  # ✅ boto3 expression
    )
```

### Broken Authentication
```python
# BAD — no token validation
def lambda_handler(event, context):
    user_id = event['queryStringParameters']['userId']
    return get_activities(user_id)  # ❌ Anyone can query any user

# GOOD — validate JWT/Cognito token
def lambda_handler(event, context):
    token = event['headers'].get('Authorization', '').replace('Bearer ', '')
    claims = validate_jwt(token)  # ✅ Validates signature + expiry
    user_id = claims['sub']
    return get_activities(user_id)
```

### Sensitive Data Exposure
```python
# BAD — log contains credentials
logger.info(f"Connecting with key={api_key}")  # ❌

# GOOD — log reference only
logger.info("Connecting with configured API key")  # ✅
logger.info(f"Request from user_id={user_id[:8]}...")  # ✅ Partial ID only
```

## Azure Key Vault (Work Projects)

For `02-work/ai-foundry-agent/` — all secrets must use Key Vault:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

vault_url = os.environ["AZURE_KEYVAULT_URL"]  # URL from env, not hardcoded
credential = DefaultAzureCredential()
client = SecretClient(vault_url=vault_url, credential=credential)

# Retrieve secret at runtime — never store locally
jira_token = client.get_secret("jira-api-token").value
```

## Pre-commit Security Gate

Before any commit touching sensitive files:

```bash
# 1. No .env files staged
git diff --cached --name-only | grep "^.*\.env$" | grep -v ".example"
# If output → remove from staging: git reset HEAD <file>

# 2. No tfvars with real values staged
git diff --cached --name-only | grep "terraform.tfvars$" | grep -v ".example"

# 3. Quick secret pattern scan
git diff --cached | grep -iE "(sk-ant-|AKIA|password\s*=\s*['\"][^'\"]+)"
# Any output → investigate before committing
```

## Security Report Format

```markdown
# Security Audit Report — [Project] — [Date]

## Critical (Fix Before Commit)
- [ ] `config/.env` has real API key — not in .gitignore for this path

## High (Fix Before PR)
- [ ] Lambda IAM role uses `dynamodb:*` — scope to specific actions

## Medium (Fix This Sprint)
- [ ] Missing input validation on `userId` query parameter

## Passed ✅
- ✅ No hardcoded secrets found in source files
- ✅ .env.example used correctly
- ✅ Azure Key Vault used in ai-foundry-agent
- ✅ All Lambda logs sanitized
```

## Integration with Workflow

```
/execute-plan (write code)
    ↓
/security-audit  ← YOU ARE HERE (before commit)
    ↓
[Fix critical issues]
    ↓
/test-runner
    ↓
/review
    ↓
git commit (clean)
```
