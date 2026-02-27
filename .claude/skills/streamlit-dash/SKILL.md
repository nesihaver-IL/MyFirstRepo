---
name: streamlit-dash
description: Build and maintain the Garmin Health Streamlit analytics dashboard. Use when working on app.py, src modules (ai_insights, charts, data_loader, metrics), or running the dashboard locally. Triggers on keywords like streamlit, dashboard, garmin analytics, run dashboard, update chart.
---

# Streamlit Dashboard

Develop and maintain the Garmin Health analytics dashboard at `01-personal/garmin-health/analytics/`.

## Purpose

Power the AI-driven personal health dashboard that surfaces insights from Garmin data:
- Display running, swimming, and sleep analytics
- Generate AI-powered recommendations via Claude API
- Render charts for activities, wellness, and VO2Max trends
- Load and normalize Garmin JSON exports

## Project Location

```
01-personal/garmin-health/analytics/
├── app.py              ← Streamlit entry point
├── src/
│   ├── ai_insights.py  ← Claude API integration (ANTHROPIC_API_KEY)
│   ├── charts.py       ← Plotly/Altair chart components
│   ├── data_loader.py  ← Garmin JSON parsing + normalization
│   └── metrics.py      ← Computed health metrics
├── .env.example        ← Required: copy to .env and add key
└── requirements.txt
```

## Athlete Context (Always Apply)

| Attribute | Value |
|-----------|-------|
| Age | 47 |
| Height / Weight | 1.80m / 70kg |
| Max HR (estimated) | 173 bpm |
| Sports | Running + Swimming |
| Recovery | Sleep (Garmin tracked) |
| Goals | 2000m swim, half-marathon training |

## When to Use

- Developing new dashboard features
- Adding new Garmin data visualizations
- Updating AI insight prompts in `ai_insights.py`
- Fixing chart rendering issues
- Running the dashboard locally for testing
- Connecting new data sources (DynamoDB vs local JSON)

## Running the Dashboard

```bash
cd 01-personal/garmin-health/analytics

# First time setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env → add ANTHROPIC_API_KEY

# Run
streamlit run app.py

# With debug output
streamlit run app.py --logger.level=debug
```

## Module Responsibilities

### `app.py` — Entry Point
- Streamlit layout and page config
- Sidebar navigation (running / swimming / sleep)
- Calls src modules for data and charts
- Renders AI insights section

### `data_loader.py` — Data Layer
```python
# Loads Garmin JSON exports
# Key files (currently in aws-ai-agent/docs/, target: garmin-health/data/raw/)
DATA_FILES = {
    "activities": "nesihaver@gmail.com_0_summarizedActivities.json",
    "sleep": "sleep_all_merged.json",
    "wellness": "wellness_all_merged.json",
    "vo2max": "vo2max_metrics_all_merged.json",
    "race_predictions": "race_predictions_all_merged.json",
    "training_history": "training_history_all_merged.json",
}
```

### `metrics.py` — Computed Metrics
- Pace calculations (min/km)
- HR zone analysis (based on MaxHR 173)
- Training load + recovery score
- Sleep quality scoring

### `charts.py` — Visualizations
- Activity timeline (runs + swims)
- HR zone distribution pie/bar
- VO2Max trend line
- Sleep stages stacked bar
- Weekly training volume

### `ai_insights.py` — Claude AI Integration
```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def get_training_insight(activities: list, athlete_profile: dict) -> str:
    prompt = f"""
    You are a personal coach for an athlete: {athlete_profile}.
    Based on recent activities: {activities}
    Provide a concise training recommendation (2-3 sentences).
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
```

## Common Dashboard Tasks

### Add a new chart
```python
# In charts.py
import plotly.express as px

def render_swim_distance_chart(swim_data: pd.DataFrame) -> None:
    fig = px.bar(
        swim_data,
        x="date",
        y="distance_meters",
        title="Swimming Distance Over Time",
        labels={"distance_meters": "Distance (m)"}
    )
    st.plotly_chart(fig, use_container_width=True)
```

### Add a new page section
```python
# In app.py
with st.sidebar:
    page = st.radio("View", ["Running", "Swimming", "Sleep", "Overview"])

if page == "Swimming":
    st.header("Swimming Analytics")
    swim_df = loader.get_swim_activities()
    charts.render_swim_distance_chart(swim_df)
    insight = ai_insights.get_training_insight(swim_df.to_dict(), athlete_profile)
    st.info(insight)
```

### Update AI prompt
```python
# In ai_insights.py — tune prompts with athlete context
SYSTEM_PROMPT = """
You are a performance coach specializing in masters athletes (40+ years).
Athlete: 47M, 70kg, 1.80m, MaxHR 173, running + swimming.
Goal: Half-marathon training + 2000m swim sessions.
Research context: See Research_Summary_*.md files.
Always be specific, data-driven, and age-appropriate.
"""
```

## Data Migration Note

Garmin JSON files currently live in `../aws-ai-agent/docs/`.
Target location: `../data/raw/` (pending migration per active plan).

Update `data_loader.py` path after migration:
```python
# Current (temporary)
DATA_DIR = Path(__file__).parent.parent.parent / "aws-ai-agent" / "docs"

# Target (after migration)
DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
```

## Integration with Workflow

```
/data-pipeline (ingest new Garmin data)
    ↓
/streamlit-dash (update dashboard)
    ↓
/test-runner (validate data_loader + metrics)
    ↓
/review
    ↓
/update-docs
```

## Environment Variables

```bash
# .env (required, never commit)
ANTHROPIC_API_KEY=sk-ant-...

# Optional: connect to live DynamoDB instead of local JSON
AWS_REGION=eu-west-1
DYNAMODB_TABLE_ACTIVITIES=garmin-activities
DYNAMODB_TABLE_WELLNESS=garmin-wellness
```
