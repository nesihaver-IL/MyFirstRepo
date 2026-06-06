# Implementation Plan: Garmin Health Analytics Dashboard (Updated)

**Status**: Ready for Approval
**Updated**: 2026-02-20
**Location**: `01-personal/garmin-analytics/`

---

## What Changed from Previous Plan

- **Removed**: Cycling (not in your data)
- **Added**: Sleep analytics as a first-class sport/pillar (equal to running + swimming)
- **Added**: Wellness daily metrics (steps, HR, calories, intensity minutes)
- **Added**: VO2Max trend chart and Fitness Age tracking
- **Added**: Race Predictions trend (5K / 10K / Half / Full)
- **Data source updated**: All JSON files already exist in `01-personal/aws-ai-agent/docs/`
- **Expertise documents updated**: Points to your 3 Research Summary MD files for AI prompting

---

## Athlete Profile (from your data)

| Field | Value |
|-------|-------|
| **Age** | 47 |
| **Height** | 1.80m |
| **Weight** | 70kg |
| **Max HR (estimated)** | 173 bpm |
| **Sports** | Running + Swimming |
| **Recovery pillar** | Sleep (tracked via Garmin) |
| **Goal** | 2000m swim sessions + Half-Marathon training |

---

## Goals

- **Primary**: Visualize running, swimming, and sleep data in one integrated dashboard
- **Secondary**: AI-generated insights that cross-reference your actual data against your expert research documents (your personal knowledge base)
- **Tertiary**: Track fitness trends — VO2Max, race predictions, training load, HRV/recovery
- **Success criteria**:
  - All 6 JSON files load and render charts automatically
  - Recommendations are grounded in your 3 Research Summary documents
  - Dashboard shows cross-pillar view (e.g., how poor sleep affects training)
  - Runs locally with a single command

---

## Data Sources (Already Available)

All files are in `01-personal/aws-ai-agent/docs/`:

| File | Content | Key Fields |
|------|---------|-----------|
| `nesihaver@gmail.com_0_summarizedActivities.json` | All activities (running + swimming) | activityType, duration, distance, avgHr, maxHr, avgSpeed, calories, avgRunCadence, vO2MaxValue, avgStrideLength |
| `sleep_all_merged.json` | Nightly sleep records | calendarDate, deepSleepSeconds, lightSleepSeconds, remSleepSeconds, awakeSleepSeconds, averageRespiration |
| `wellness_all_merged.json` | Daily wellness snapshot | calendarDate, totalSteps, restingHeartRate, activeKilocalories, moderateIntensityMinutes, vigorousIntensityMinutes, highlyActiveSeconds |
| `vo2max_metrics_all_merged.json` | VO2Max over time | calendarDate, vo2MaxValue, fitnessAge, maxMet |
| `race_predictions_all_merged.json` | Garmin predicted race times | calendarDate, raceTime5K, raceTime10K, raceTimeHalf, raceTimeMarathon (in seconds) |
| `training_history_all_merged.json` | Weekly training load | calendarDate, sport, weeklyTrainingLoadSum, trainingStatus, loadLevelTrend |

---

## Expertise Documents (AI Knowledge Base)

All files are in `01-personal/aws-ai-agent/docs/`:

| File | Content |
|------|---------|
| `Research_Summary_Swimming.md` | HR zones, stroke efficiency, injury prevention, SWOLF, CSS for 47-yr master |
| `Research_Summary_Running-EN.md` | 80/20 rule, cadence, 10% rule, nutrition, half-marathon plan for 70kg masters runner |
| `Research_Summary_sleeping-1.md` | HRV, sleep stages, Body Battery, ACWR (0.8–1.3), sleep optimization protocols |

---

## Technical Decisions

| Tool | Role | Why |
|------|------|-----|
| **Streamlit** | Browser UI | Pure Python, runs locally, instant interactivity |
| **Plotly** | Charts | Interactive zoom/hover, handles time-series well |
| **Claude API** | AI insights | Reads your actual data + your research docs, generates grounded recommendations |
| **Pandas** | Data processing | Parse, normalize, and aggregate all 6 JSON files |
| **python-dotenv** | Config | Keeps API key out of code |

---

## File Structure

```
01-personal/garmin-analytics/
├── app.py                        (CREATE) - Streamlit main app entry point
├── requirements.txt              (CREATE) - Python dependencies
├── .env.example                  (CREATE) - API key template
├── src/
│   ├── __init__.py               (CREATE)
│   ├── data_loader.py            (CREATE) - Load and normalize all 6 JSON files
│   ├── metrics.py                (CREATE) - Derived metrics per sport + sleep scores
│   ├── ai_insights.py            (CREATE) - Claude API integration using research docs
│   └── charts.py                 (CREATE) - All Plotly chart builders
├── CLAUDE.md                     (CREATE) - Project-specific AI context
└── README.md                     (CREATE) - Setup and usage guide
```

> **Note**: No `data/` folder needed — data files are already in `01-personal/aws-ai-agent/docs/`. The app reads from that path directly.

---

## Dashboard Structure (7 Tabs)

### Tab 1 — Overview
- Total weekly training hours (running + swimming combined)
- Resting HR trend (from wellness)
- Daily steps vs. goal (10,000)
- Training status badge (from training_history: Peaking / Maintaining / Overreaching)
- Body Battery / Active calories weekly bar chart

### Tab 2 — Running
- Pace trend over time (min/km, computed from avgSpeed)
- Distance per session trend
- Heart rate distribution by session (avg vs. max)
- Cadence trend (steps per minute, from avgRunCadence × 2)
- Weekly training load (from training_history, sport=RUNNING)
- Race Predictions trend: 5K / 10K / Half / Marathon (converted from seconds to HH:MM:SS)

### Tab 3 — Swimming
- Session duration trend (minutes)
- Distance trend (meters/km per session)
- Avg HR per session
- Calories per session
- VO2Max at time of session (from vO2MaxValue inside summarizedActivities)

### Tab 4 — Sleep
- Nightly total sleep duration (hours)
- Sleep stage breakdown per night: Deep / Light / REM / Awake (stacked bar)
- Deep sleep % trend — target: >15% of total
- REM sleep % trend — target: >20% of total
- Average respiration rate trend
- Weekly sleep score (computed: weighted by stage quality)
- Alerts: nights below 7h total, low deep sleep weeks

### Tab 5 — Fitness & Recovery
- VO2Max trend over time + Fitness Age trend
- Acute-to-Chronic Workload Ratio (ACWR): 7-day vs. 28-day rolling load
  - Color zones: Green (0.8–1.3 = safe), Yellow (1.3–1.5 = caution), Red (>1.5 = injury risk)
- Resting HR trend (lower = better fitness)
- Intensity minutes: Moderate vs. Vigorous per week vs. WHO target (150 min moderate)

### Tab 6 — Cross-Pillar Correlations
- Sleep duration vs. Next-day training load (scatter)
- Resting HR vs. VO2Max over time (dual-axis line)
- Weekly training volume vs. Sleep quality score (correlation view)
- This tab surfaces the most actionable insights (e.g., "you train harder after good sleep")

### Tab 7 — AI Recommendations
- Sidebar controls: time window (last 30 / 60 / 90 days)
- Button: "Generate Personalized Analysis"
- Claude receives:
  1. Summarized stats from selected period (not raw records — just aggregates)
  2. Full text of all 3 Research Summary documents
  3. Your athlete profile (age, weight, height)
- Response structured in 4 sections:
  - **Training Load Assessment** — are you in the right ACWR window?
  - **Running Analysis** — pace trends, cadence, race prediction progress
  - **Swimming Analysis** — session consistency, HR zones, efficiency
  - **Sleep & Recovery** — HRV interpretation, sleep stage quality, behavioral recommendations
- Response cached for 1 hour to avoid repeat API calls

---

## Implementation Steps

### Phase 1: Project Setup
1. [ ] Create folder `01-personal/garmin-analytics/`
2. [ ] Create `requirements.txt`
3. [ ] Create `.env.example` with `ANTHROPIC_API_KEY=`
4. [ ] Create skeleton `app.py` (loads with no errors, shows placeholder tabs)
5. [ ] Create `CLAUDE.md`

### Phase 2: Data Loader (`src/data_loader.py`)
1. [ ] Load `summarizedActivities.json` — parse the nested `summarizedActivitiesExport` array
2. [ ] Split activities by `sportType`: `RUNNING` vs `LAP_SWIMMING` / `OPEN_WATER_SWIMMING`
3. [ ] Normalize running activities: date, duration_min, distance_km, avg_hr, max_hr, cadence_spm, calories, pace_min_per_km, vo2max_at_session
4. [ ] Normalize swimming activities: date, duration_min, distance_m, avg_hr, calories
5. [ ] Load `sleep_all_merged.json` → normalize: date, total_sleep_h, deep_min, light_min, rem_min, awake_min, respiration_avg
6. [ ] Load `wellness_all_merged.json` → normalize: date, steps, resting_hr, active_kcal, moderate_min, vigorous_min
7. [ ] Load `vo2max_metrics_all_merged.json` → normalize: date, vo2max, fitness_age
8. [ ] Load `race_predictions_all_merged.json` → normalize: date, 5k_sec, 10k_sec, half_sec, marathon_sec
9. [ ] Load `training_history_all_merged.json` → normalize: date, sport, weekly_load, training_status
10. [ ] All loaders return clean Pandas DataFrames with `date` as a proper datetime index

### Phase 3: Metrics (`src/metrics.py`)
1. [ ] Running: pace (min/km), weekly km, cadence (spm = avgRunCadence × 2), HR zone assignment
2. [ ] Swimming: session duration trend, calories per session
3. [ ] Sleep: total hours, sleep stage % breakdown, weekly sleep score (weighted: deep×3 + rem×2 + light×1)
4. [ ] Fitness: ACWR (7-day load / 28-day rolling avg), VO2Max trend
5. [ ] Race predictions: convert seconds → MM:SS string for display
6. [ ] Cross-pillar: correlate sleep quality score with next-day training load
7. [ ] Wellness: weekly intensity minutes vs. WHO target (150 min/week moderate)

### Phase 4: Charts (`src/charts.py`)
One function per chart, all return Plotly `Figure` objects:
1. [ ] `weekly_volume_bar()` — stacked run + swim hours per week
2. [ ] `pace_trend_line()` — running pace over time
3. [ ] `hr_distribution_box()` — avg HR per session by sport
4. [ ] `cadence_trend_line()` — running cadence over time
5. [ ] `race_predictions_line()` — 4 distances on one chart, improving = line goes down
6. [ ] `sleep_duration_bar()` — nightly total sleep with 7h/8.5h reference lines
7. [ ] `sleep_stages_stacked_bar()` — deep/light/rem/awake per night
8. [ ] `sleep_stage_pct_line()` — deep% and rem% trends
9. [ ] `vo2max_trend_line()` — VO2Max + fitness age dual axis
10. [ ] `acwr_chart()` — 7-day/28-day load ratio with colored risk zones
11. [ ] `resting_hr_trend()` — resting HR from wellness data
12. [ ] `intensity_minutes_bar()` — weekly moderate + vigorous vs. 150 min goal
13. [ ] `sleep_vs_load_scatter()` — cross-pillar: sleep hours vs. next-day load
14. [ ] `steps_trend_bar()` — daily steps vs. 10k goal

### Phase 5: Streamlit App (`app.py`)
1. [ ] Sidebar: date range picker (default: last 90 days), sport filter
2. [ ] Load all DataFrames via `data_loader.py` with `@st.cache_data`
3. [ ] Build 7 tabs, wire each chart to the date range filter
4. [ ] Tab 7: "Generate Insights" button → call `ai_insights.py` → display formatted response
5. [ ] Add loading spinners for data and AI calls
6. [ ] Error messages when data is missing or API key not set

### Phase 6: AI Insights (`src/ai_insights.py`)
1. [ ] Read all 3 Research Summary MD files from `01-personal/aws-ai-agent/docs/`
2. [ ] Aggregate last N days of data into a compact text summary (stats only, not raw records):
   - Running: total sessions, avg pace, avg HR, cadence avg, weekly km
   - Swimming: total sessions, avg duration, avg HR, avg calories
   - Sleep: avg total hours, avg deep%, avg rem%, nights below 7h
   - VO2Max: current value, trend direction
   - ACWR: current ratio, recent training status
3. [ ] Send to Claude with structured prompt and athlete profile
4. [ ] Parse and return 4-section response
5. [ ] Cache result with `@st.cache_data(ttl=3600)` so it doesn't re-run on every refresh

### Phase 7: Polish
1. [ ] README with: how to set up, how to run, folder locations
2. [ ] Handle gracefully: missing fields in JSON (not all activities have all fields)
3. [ ] Handle gracefully: summarizedActivities.json is very large — stream/chunk if needed

---

## Dependencies

```
streamlit>=1.32.0
plotly>=5.20.0
pandas>=2.0.0
anthropic>=0.25.0
python-dotenv>=1.0.0
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| `summarizedActivities.json` is very large (~1.2M tokens raw) | Load once with `@st.cache_data`, only parse needed fields |
| Some sleep records have no stage data (UNCONFIRMED type) | Filter to `ENHANCED_CONFIRMED_FINAL` records, show count of excluded nights |
| Swimming and Running in same activities file | Filter by `sportType` field: `LAP_SWIMMING`, `OPEN_WATER_SWIMMING`, `RUNNING` |
| Claude API cost on large AI calls | Send only aggregated stats (< 2000 tokens of data) + research docs |
| Data privacy | All processing is local; only aggregated stats leave your machine for Claude |

---

## Success Criteria

- [ ] `streamlit run app.py` starts with no errors
- [ ] All 7 tabs load with charts populated from your actual JSON files
- [ ] Sleep tab shows stage breakdown (deep/light/rem) trends
- [ ] Running tab shows pace trend + race predictions improving over time
- [ ] ACWR chart shows green/yellow/red risk zones correctly
- [ ] "Generate Insights" returns a structured 4-section analysis within 30 seconds
- [ ] AI response references your research documents (e.g., mentions 80/20 rule, ACWR 0.8–1.3 window, sleep stage targets)

---

## How to Run (after implementation)

```bash
cd 01-personal/garmin-analytics
pip install -r requirements.txt
cp .env.example .env        # add your ANTHROPIC_API_KEY
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## Approval

- [ ] Technical approach approved
- [ ] 7-tab dashboard structure acceptable
- [ ] Data source folder confirmed (`01-personal/aws-ai-agent/docs/`)
- [ ] Ready to execute with `/execute-plan`
