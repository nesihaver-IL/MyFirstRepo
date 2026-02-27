# Garmin Health Analytics

Personal health analytics system integrating Garmin wearable data with AWS serverless infrastructure and Claude AI-powered insights.

## Architecture

```
Garmin Connect API
      ↓
AWS Lambda (garmin_fetch_activity.py)
      ↓
DynamoDB + EventBridge
      ↓
Lambda AI Analyzer (garmin_ai_analyzer.py)
      ↓
Streamlit Dashboard (analytics/app.py)
      ↓
Claude AI Insights
```

## Sub-Projects

| Folder | Description |
|--------|-------------|
| `backend/` | AWS Lambda functions + Terraform infrastructure |
| `datasets/` | Garmin RAG dataset batches for AI grounding |
| `analytics/` | Streamlit visualization dashboard |
| `data/` | Runtime data (raw → processed → exports) |

## Quick Start

**Dashboard only (no AWS needed):**
```bash
cd analytics && pip install -r requirements.txt
cp .env.example .env  # add ANTHROPIC_API_KEY
streamlit run app.py
```

**Full backend deployment:**
```bash
cd backend && bash scripts/deploy.sh
```

## See Also
- [CLAUDE.md](CLAUDE.md) — full AI context and data locations
- [DECISIONS.md](DECISIONS.md) — architectural decisions
- [Active plan](.plans/PLAN-garmin-health-analytics-2026-02-20.md)
