# Garmin Health Analytics Dashboard

Personal health analytics dashboard for a masters athlete (47yr, 70kg).
Visualizes Garmin data across 3 pillars: **Running**, **Swimming**, and **Sleep**.
Uses Claude AI to generate personalized recommendations grounded in your own sports science research documents.

## What It Shows

| Tab | Content |
|-----|---------|
| 📊 Overview | Weekly training volume, resting HR, steps, ACWR |
| 🏃 Running | Pace trend, cadence, HR, race predictions (5K/10K/Half/Marathon) |
| 🏊 Swimming | Distance, SWOLF, HR, calories per session |
| 😴 Sleep | Nightly hours, deep/REM/light stages, respiration, alerts |
| 💪 Fitness & Recovery | VO2Max, Fitness Age, ACWR risk zones, intensity minutes |
| 🔗 Cross-Pillar | Sleep vs training load, Resting HR vs VO2Max correlations |
| 🤖 AI Recommendations | Claude AI 4-section analysis grounded in your research docs |

## Setup

### 1. Install dependencies

```bash
cd 01-personal/garmin-analytics

# Using the included virtual environment (already set up)
source .venv/bin/activate

# Or install fresh
pip install -r requirements.txt
```

### 2. Configure API key (for AI Recommendations tab)

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...
```

The dashboard works fully without an API key — only the AI Recommendations tab requires it.

### 3. Run

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Data Sources

All JSON files are read from `../aws-ai-agent/docs/` (no copying needed):

| File | What it contains |
|------|-----------------|
| `nesihaver@gmail.com_0_summarizedActivities.json` | All running + swimming sessions |
| `sleep_all_merged.json` | Nightly sleep with stage breakdown |
| `wellness_all_merged.json` | Daily steps, resting HR, intensity minutes |
| `vo2max_metrics_all_merged.json` | VO2Max and Fitness Age history |
| `race_predictions_all_merged.json` | Garmin-estimated 5K / 10K / Half / Marathon times |
| `training_history_all_merged.json` | Weekly training load and status |

## AI Knowledge Base

The AI Recommendations tab uses your 3 personal research documents as its knowledge base:
- `Research_Summary_Swimming.md` — swimming biomechanics, HR zones, SWOLF targets
- `Research_Summary_Running-EN.md` — 80/20 rule, cadence, half-marathon training
- `Research_Summary_sleeping-1.md` — HRV, sleep stages, ACWR, recovery protocols

## Key Metrics Explained

| Metric | What it means |
|--------|--------------|
| **ACWR** | Acute-to-Chronic Workload Ratio. Safe zone: 0.8–1.3. Above 1.5 = injury risk |
| **SWOLF** | Stroke + Lap time. Lower = more efficient swimmer. Elite target: <40 |
| **Cadence** | Running steps per minute. Target: 170–185 spm |
| **Deep Sleep %** | Target >15% of total sleep for physical recovery |
| **REM Sleep %** | Target >20% of total sleep for cognitive recovery |
| **Fitness Age** | Garmin's estimated physiological age based on VO2Max |
