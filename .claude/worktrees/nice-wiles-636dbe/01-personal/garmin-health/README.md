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

**Insight pipeline (recommended — no AWS needed):**
```bash
cd 01-personal/garmin-health
pip install -r requirements.txt
cp analytics/.env.example .env  # add ANTHROPIC_API_KEY=sk-ant-...
python run_pipeline.py           # last 90 days (default)
python run_pipeline.py --days 30
```
Output: `data/exports/health-report-YYYY-MM-DD.html` — open in any browser.

**Dashboard only (interactive charts):**
```bash
cd analytics && pip install -r requirements.txt
cp .env.example .env  # add ANTHROPIC_API_KEY
streamlit run app.py
```

**Full backend deployment:**
```bash
cd backend && bash scripts/deploy.sh
```

## Running the Pipeline

The pipeline is a local, on-demand CLI tool that produces a self-contained health report.

```
run_pipeline.py
    └── GarminHealthOrchestrator
            ├── DataAgent      — loads all 6 Garmin JSON files + computes ACWR
            ├── AlertAgent     — deterministic threshold checks (no AI)
            ├── AnalysisAgent  — Claude AI 4-section analysis
            └── ReportAgent    — writes Markdown + HTML to data/exports/
```

**Alerts fired by thresholds (not AI):**
- ACWR >1.5 → RED (injury risk), >1.3 → YELLOW, <0.8 → YELLOW (detraining)
- Sleep avg <6.5h or deep% <8% → RED; <7h or deep% <12% → YELLOW
- No running in 21+ days → RED; 10+ days → YELLOW
- VO2Max declined >2 ml/kg/min in 30 days → YELLOW

Running without `ANTHROPIC_API_KEY` still produces a partial report (alerts + metrics, no AI analysis).

## See Also
- [CLAUDE.md](CLAUDE.md) — full AI context and data locations
- [DECISIONS.md](DECISIONS.md) — architectural decisions
- [Pipeline plan](.plans/PLAN-garmin-health-pipeline-2026-02-27.md)
- [Analytics plan](.plans/PLAN-garmin-health-analytics-2026-02-20.md)
