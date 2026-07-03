# Getting Started — Garmin Health Analytics

## Three Ways to View Your Data

### 1. Interactive HTML Reports (Fastest — 1 minute)

**No setup needed!** View pre-rendered interactive charts:

```bash
cd 01-personal/garmin-health
python3 generate_reports.py
```

Opens 6 interactive charts in `data/exports/`:
- Running Performance Trends
- Swimming Performance Trends  
- Weekly Training Volume
- Sleep Quality Analysis
- Heart Rate Distribution
- Training Summary

### 2. Live Streamlit Dashboard (Most Features — 2 minutes)

**Automatic setup:**

```bash
cd 01-personal/garmin-health
./run.sh                    # Linux/Mac
# OR
run.bat                     # Windows
```

Dashboard opens at `http://localhost:8501` with:
- 9 tabs (Overview, Running, Swimming, Sleep, Fitness, Cross-Pillar, AI Coach, Personal Bests, Records)
- 18 interactive visualizations
- AI-powered insights from Claude
- Live date range filters

### 3. SQLite Database (Best Performance — Optional)

Migrate JSON to SQLite for 10x faster loading:

```bash
cd 01-personal/garmin-health/analytics
python3 setup_database.py ../data/garmin_health.db
```

---

## What's Included

- ✅ **783 activities** (2020-2025)
  - 443 swimming (748 km)
  - 190 running (886 km)
  - 80 cycling + fitness/generic

- ✅ **1,699 nights** of sleep tracked
- ✅ **210 VO2Max readings**
- ✅ **5.5 years** of health data

---

## Quick Feature Tour

| Feature | Where | What You'll See |
|---------|-------|-----------------|
| Weekly Volume | Overview Tab | Running vs Swimming km/week |
| Pace Trends | Running Tab | Your pace improvement over time |
| Sleep Quality | Sleep Tab | Duration, deep/REM/light breakdown |
| Heart Rate Zones | Cross-Pillar Tab | HR distribution by intensity zone |
| Race Predictions | Running Tab | Estimated 5K/10K/HM/Marathon times |
| AI Coaching | AI Coach Tab | Claude insights on training load & recovery |
| Personal Records | Personal Bests | Fastest/longest sessions by distance |
| Training Load (ACWR) | Overview | Training balance indicator (safe/caution/risk) |

---

## Troubleshooting

**"No module named streamlit"**
```bash
pip install -r analytics/requirements.txt
```

**"Database is locked"**
```bash
cd data
rm -f garmin*.db
python3 ../analytics/setup_database.py garmin_health.db
```

**Port 8501 already in use**
```bash
streamlit run analytics/app.py --server.port 8502
```

**Missing API key for AI Coach**
Edit `analytics/.env` and add:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## Project Files

```
garmin-health/
├── run.sh              ← Launch dashboard (Linux/Mac)
├── run.bat             ← Launch dashboard (Windows)
├── generate_reports.py ← Generate HTML charts
├── analytics/
│   ├── app.py          ← Dashboard (9 tabs, 18 charts)
│   ├── setup_database.py ← SQLite migration
│   ├── requirements.txt
│   └── src/
│       ├── data_loader.py   ← JSON/SQLite loading
│       ├── metrics.py       ← Aggregations & computations
│       ├── charts.py        ← 18 Plotly visualizations
│       └── ai_insights.py   ← Claude API integration
└── data/
    ├── garmin.db (existing)
    ├── exports/           ← Generated HTML reports
    └── raw/              ← JSON data (optional)
```

---

## Next Steps

1. **View reports now:** `python3 generate_reports.py`
2. **Launch dashboard:** `./run.sh` (or `run.bat`)
3. **Migrate to SQLite:** `cd analytics && python3 setup_database.py ../data/garmin_health.db`

Questions? See `CLAUDE.md` and `README.md` for full documentation.
