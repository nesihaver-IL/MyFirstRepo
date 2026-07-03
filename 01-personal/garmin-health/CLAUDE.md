# Garmin Health - AI Context

## Output Formatting Rules

- **NEVER use em dash "—"** in any output, content, or deliverable. Always use a regular hyphen "-" instead.

## Project Purpose
End-to-end personal health analytics system for a 47-year-old male athlete (1.80m, 70kg).
Ingests Garmin data via AWS Lambda, stores it via DynamoDB, and surfaces insights through
a Streamlit dashboard powered by Claude AI.

**Three pillars**: Running | Swimming | Sleep

## Athlete Profile
- Age: 47, Height: 1.80m, Weight: 70kg
- Max HR (estimated): 173 bpm
- Sports: Running + Swimming
- Recovery pillar: Sleep (Garmin tracked)
- Goals: 2000m swim sessions, half-marathon training

## Project Structure

```
garmin-health/
├── backend/           AWS Lambda + Terraform ingestion pipeline
│   ├── config/        Environment config (.env.example, tfvars.example)
│   ├── lambda/        4 Lambda functions (fetch, oauth, webhook, analyzer)
│   ├── terraform/     Full AWS infrastructure (API GW, DynamoDB, EventBridge, IAM)
│   ├── scripts/       Deploy/destroy/test bash scripts
│   └── tests/         OAuth flow + activity query tests
├── datasets/          Garmin RAG dataset (3 ZIP batches: activities, wellness, training)
├── analytics/         Streamlit dashboard (app.py + src modules)
│   ├── app.py         Streamlit entry point
│   └── src/           ai_insights.py, charts.py, data_loader.py, metrics.py
└── data/              Runtime data (gitignored large files)
    ├── raw/           Original Garmin JSON exports
    ├── processed/     Normalized records
    └── exports/       Generated reports and charts
```

## Data Files (Current Location)
Garmin JSON exports currently live in `../aws-ai-agent/docs/` (historical location).
**Target**: migrate to `data/raw/` when next ingestion pipeline is run.

Key files:
- `nesihaver@gmail.com_0_summarizedActivities.json` — all activities
- `sleep_all_merged.json` — nightly sleep
- `wellness_all_merged.json` — daily wellness
- `vo2max_metrics_all_merged.json` — VO2Max history
- `race_predictions_all_merged.json` — race time predictions
- `training_history_all_merged.json` — training load history

## AI Knowledge Base (Expertise Docs)
Research summaries used for AI-grounded recommendations:
- `Research_Summary_Swimming.md`
- `Research_Summary_Running-EN.md`
- `Research_Summary_sleeping-1.md`

## Running the Analytics Dashboard
```bash
cd analytics
pip install -r requirements.txt
cp .env.example .env  # add ANTHROPIC_API_KEY
streamlit run app.py
```

## Deploying the AWS Backend
```bash
cd backend
cp config/.env.example config/.env        # fill in values
cp config/terraform.tfvars.example config/terraform.tfvars
bash scripts/deploy.sh
```

## Tech Stack
| Component | Technology |
|-----------|-----------|
| Data ingestion | AWS Lambda (Python) |
| Infrastructure | Terraform |
| API layer | AWS API Gateway |
| Storage | DynamoDB |
| Events | EventBridge |
| Dashboard | Streamlit + Python |
| AI | Anthropic Claude (via API) |
| Dataset | Garmin JSON exports (ZIP batches) |

## Active Plan
`.plans/PLAN-garmin-health-analytics-2026-02-20.md`
