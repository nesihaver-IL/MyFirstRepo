# Garmin Health Analytics Dashboard — AI Context

## Project Purpose
Personal health analytics dashboard for a 47-year-old male athlete (1.80m, 70kg).
Visualizes Garmin data across 3 pillars: Running, Swimming, Sleep.
Uses Claude AI to generate recommendations grounded in the athlete's personal research documents.

## Athlete Profile
- Age: 47, Height: 1.80m, Weight: 70kg
- Max HR (estimated): 173 bpm
- Sports: Running + Swimming
- Recovery pillar: Sleep (Garmin tracked)
- Goals: 2000m swim sessions, half-marathon training

## Data Location
All Garmin JSON exports are in `../aws-ai-agent/docs/` (relative to this project):
- `nesihaver@gmail.com_0_summarizedActivities.json` — all activities
- `sleep_all_merged.json` — nightly sleep
- `wellness_all_merged.json` — daily wellness
- `vo2max_metrics_all_merged.json` — VO2Max history
- `race_predictions_all_merged.json` — race time predictions
- `training_history_all_merged.json` — training load history

## Expertise Documents (AI Knowledge Base)
- `Research_Summary_Swimming.md`
- `Research_Summary_Running-EN.md`
- `Research_Summary_sleeping-1.md`

## Running the App
```bash
pip install -r requirements.txt
cp .env.example .env  # add ANTHROPIC_API_KEY
streamlit run app.py
```
