# Implementation Plan: Garmin Health Automated Insight Pipeline

**Status**: Ready for Approval
**Created**: 2026-02-27
**Project**: `01-personal/garmin-health/`

---

## Overview

Build an orchestrator + 4 sub-agents that run on demand (`python run_pipeline.py`) to:
1. Load and validate all Garmin data (6 JSON files)
2. Detect health threshold violations and fire alerts
3. Generate a Claude AI 4-section analysis
4. Write a self-contained Markdown + HTML report to `data/exports/`

**What this is NOT**: not a chat agent, not a webhook, not a scheduler. It is a composable, testable pipeline that produces a dated report file you can open in any browser.

---

## Goals

- **Primary**: One command produces a comprehensive health report with alerts + AI analysis
- **Secondary**: Reuse existing `data_loader.py`, `metrics.py`, `ai_insights.py` — zero duplication
- **Tertiary**: Each sub-agent is independently importable and testable
- **Success criteria**:
  - `python run_pipeline.py` completes with no errors
  - Report is saved to `data/exports/health-report-YYYY-MM-DD.html`
  - Alert section is accurate and data-driven (no AI hallucination in alerts)
  - AI analysis section is grounded in the 3 research docs
  - HTML report renders correctly in any browser (self-contained, no CDN)

---

## Architecture

```
run_pipeline.py  (CLI entry point at garmin-health/ root)
    └── GarminHealthOrchestrator
            │
            ├── DataAgent          — loads all 6 DataFrames + computes ACWR
            │       uses: analytics/src/data_loader.py
            │       uses: analytics/src/metrics.py
            │       returns: DataBundle (dataclass with all DataFrames)
            │
            ├── AlertAgent         — threshold checks → Alert list
            │       receives: DataBundle
            │       checks: ACWR zones, sleep quality, training gaps, VO2Max trend
            │       returns: List[Alert]  (severity: RED | YELLOW | INFO)
            │
            ├── AnalysisAgent      — Claude AI 4-section analysis
            │       uses: analytics/src/ai_insights.py (build_data_summary + generate_insights)
            │       receives: DataBundle, days: int
            │       returns: str  (4-section markdown text)
            │
            └── ReportAgent        — assembles and writes report files
                    receives: DataBundle, List[Alert], analysis str, days int
                    produces: data/exports/health-report-YYYY-MM-DD.md
                              data/exports/health-report-YYYY-MM-DD.html
                    returns: dict with output file paths
```

**Data flow: sequential, no parallelism needed** (each agent feeds the next).

**No internet access except for Claude API call** (in AnalysisAgent).

---

## Technical Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Language | Python 3.11+ | Matches existing analytics stack |
| Agent pattern | Simple function objects with `.run()` | No framework overhead; easy to test |
| Data passing | `DataBundle` dataclass | Type-safe, avoids re-loading data between agents |
| Alert logic | Pure Python thresholds | Never hallucinated — deterministic |
| HTML generation | Jinja2 template + inline CSS | Self-contained file, works offline |
| Markdown generation | Python f-strings | Simple, no Markdown library needed for writing |
| Path management | `sys.path` insert in agent module | Avoids modifying existing analytics package |
| Error handling | Fail-fast per agent, log to console | Clear feedback when data files are missing |

---

## File Structure

```
01-personal/garmin-health/
├── run_pipeline.py                    CREATE  CLI entry point
├── requirements.txt                   CREATE  pipeline-level deps (adds jinja2 + markdown)
├── agent/
│   ├── __init__.py                    CREATE  (empty)
│   ├── models.py                      CREATE  DataBundle, Alert dataclasses
│   ├── orchestrator.py                CREATE  coordinates all 4 agents
│   ├── data_agent.py                  CREATE  loads DataBundle from data_loader + metrics
│   ├── alert_agent.py                 CREATE  threshold rules → List[Alert]
│   ├── analysis_agent.py              CREATE  wraps ai_insights.generate_insights
│   └── report_agent.py                CREATE  Markdown + HTML output
├── templates/
│   └── report.html.jinja2             CREATE  HTML report template
├── analytics/                         EXISTS  unchanged
│   └── src/
│       ├── data_loader.py             EXISTS  (path already fixed)
│       ├── metrics.py                 EXISTS
│       ├── ai_insights.py             EXISTS  (path already fixed)
│       └── charts.py                 EXISTS
└── data/
    └── exports/                       EXISTS  output directory (already created)
```

---

## Alert Thresholds (AlertAgent)

These are pure data checks — no AI involved. Each produces an `Alert` with `severity` and `message`.

### ACWR (Acute:Chronic Workload Ratio)
| Condition | Severity | Message |
|-----------|----------|---------|
| ACWR > 1.5 | RED | "Injury risk: ACWR {val}. Reduce training load immediately." |
| ACWR 1.3–1.5 | YELLOW | "Caution: ACWR {val} is elevated. Monitor training load." |
| ACWR < 0.8 | YELLOW | "Detraining risk: ACWR {val}. Consider increasing training load." |
| ACWR 0.8–1.3 | INFO | "Training load is in the optimal zone (ACWR {val})." |

### Sleep Quality (last 7 nights)
| Condition | Severity | Message |
|-----------|----------|---------|
| Avg total sleep < 6.5h | RED | "Critical sleep deficit: avg {val}h. Recovery is impaired." |
| Avg total sleep < 7h | YELLOW | "Below sleep target: avg {val}h. Aim for 7–9h nightly." |
| Avg deep sleep < 8% | RED | "Very low deep sleep: {val}% avg (target >15%). Recovery at risk." |
| Avg deep sleep < 12% | YELLOW | "Low deep sleep: {val}% avg (target >15%). Review sleep hygiene." |

### Training Gaps (days since last session)
| Condition | Severity | Message |
|-----------|----------|---------|
| No running in 21+ days | RED | "No running in {n} days. Significant detraining risk." |
| No running in 10+ days | YELLOW | "Running gap: last session {n} days ago." |
| No swimming in 14+ days | INFO | "No swimming in {n} days." |

### VO2Max Trend (last 30 days)
| Condition | Severity | Message |
|-----------|----------|---------|
| VO2Max declined >2 ml/kg/min | YELLOW | "VO2Max dropped from {old} to {new}. Check training quality." |
| VO2Max improved >1 ml/kg/min | INFO | "VO2Max improving: {old} → {new} ml/kg/min." |

---

## Report Format

### Markdown structure (`health-report-YYYY-MM-DD.md`)
```markdown
# Garmin Health Report — 2026-02-27
**Analysis period**: Last 90 days  |  **Generated**: 2026-02-27 08:30

---

## Alerts

| Severity | Alert |
|----------|-------|
| 🔴 RED   | Injury risk: ACWR 1.62. Reduce training load immediately. |
| 🟡 YELLOW | Low deep sleep: 11.2% avg (target >15%). Review sleep hygiene. |

---

## Key Metrics Snapshot (Last 90 Days)

| Pillar | Metric | Value | Context |
|--------|--------|-------|---------|
| Running | Sessions | 24 | — |
| Running | Avg pace | 5:42 min/km | — |
| Running | Total km | 186.4 km | — |
| Swimming | Sessions | 12 | — |
| Swimming | Avg distance | 1,840 m | Goal: 2,000m |
| Sleep | Avg duration | 7.1h | Target: 7–9h |
| Sleep | Avg deep sleep | 13.2% | Target: >15% |
| Fitness | VO2Max | 48 ml/kg/min | — |
| Fitness | Fitness Age | 38 years | Chronological: 47 |

---

## AI Analysis

### 1. Training Load Assessment
[...]

### 2. Running Analysis
[...]

### 3. Swimming Analysis
[...]

### 4. Sleep & Recovery Recommendations
[...]

---
*Generated by Garmin Health Pipeline | Model: claude-sonnet-4-6*
```

### HTML report
Same content rendered via Jinja2 template with:
- Inline CSS (no CDN, works offline)
- Alert color coding (red/yellow/green badges)
- Responsive table layout
- Collapsible AI Analysis sections (pure CSS, no JS required)

---

## Implementation Steps

### Phase 1: Models + DataAgent

**Files**: `agent/__init__.py`, `agent/models.py`, `agent/data_agent.py`

1. [ ] Create `agent/__init__.py` (empty)
2. [ ] Create `agent/models.py`:
   - `Alert` dataclass: `severity: str`, `category: str`, `message: str`
   - `DataBundle` dataclass: `run_df`, `swim_df`, `sleep_df`, `well_df`, `vo2_df`, `race_df`, `train_df`, `acwr_df`, `loaded_at`, `days_back`
3. [ ] Create `agent/data_agent.py`:
   - Add `sys.path` insert to make `analytics/src` importable
   - `DataAgent.run(days: int) -> DataBundle`
   - Import and call all `data_loader.py` load functions
   - Call `metrics.compute_acwr(run_df, train_df)` to produce `acwr_df`
   - Validate: check each DataFrame is non-empty, log warnings for missing data
   - Return populated `DataBundle`

**Validation**: `python -c "from agent.data_agent import DataAgent; b = DataAgent().run(); print(b.run_df.shape)"`

---

### Phase 2: AlertAgent

**File**: `agent/alert_agent.py`

1. [ ] Create `agent/alert_agent.py`:
   - `AlertAgent.run(bundle: DataBundle) -> List[Alert]`
   - Implement all threshold checks from the table above
   - Use `bundle.sleep_df`, `bundle.acwr_df`, `bundle.run_df`, `bundle.swim_df`, `bundle.vo2_df`
   - Sleep checks: filter to last 7 days
   - ACWR check: use latest row of `acwr_df`
   - Training gap checks: compute days since most recent session
   - VO2Max trend: compare first vs last record in last 30 days
   - Return `List[Alert]` sorted by severity (RED first)

**Validation**: `python -c "from agent.data_agent import DataAgent; from agent.alert_agent import AlertAgent; b=DataAgent().run(); alerts=AlertAgent().run(b); [print(a) for a in alerts]"`

---

### Phase 3: AnalysisAgent

**File**: `agent/analysis_agent.py`

1. [ ] Create `agent/analysis_agent.py`:
   - `AnalysisAgent.run(bundle: DataBundle, days: int) -> str`
   - Import `generate_insights` and `build_data_summary` from `analytics/src/ai_insights.py`
   - Unpack `DataBundle` into the 7 DataFrames expected by `generate_insights`
   - Call `generate_insights(...)` and return the result string
   - On `ANTHROPIC_API_KEY` missing: return a fallback string "AI analysis unavailable — set ANTHROPIC_API_KEY in .env" (so pipeline still produces a report)
   - On API error: catch exception, log, return error message (don't crash pipeline)

**Validation**: Requires valid `ANTHROPIC_API_KEY` in `.env` — test separately

---

### Phase 4: ReportAgent

**Files**: `agent/report_agent.py`, `templates/report.html.jinja2`

1. [ ] Create `templates/report.html.jinja2` — self-contained HTML with:
   - Inline CSS (clean, readable, no frameworks)
   - Header: report date + analysis period
   - Alert section: colored badges per severity
   - Key metrics table
   - AI analysis rendered as HTML (convert Markdown headings + lists)
   - Footer: timestamp + model name
2. [ ] Create `agent/report_agent.py`:
   - `ReportAgent.run(bundle, alerts, analysis, days) -> dict`
   - `_build_metrics_table(bundle, days) -> List[dict]` — summarize key stats
   - `_render_markdown(bundle, alerts, analysis, days) -> str` — produce `.md` text
   - `_render_html(bundle, alerts, analysis, days) -> str` — render Jinja2 template
   - Write both files to `data/exports/health-report-{date}.md` and `.html`
   - Return `{"md": path_to_md, "html": path_to_html}`

**Validation**: Run full pipeline and open HTML file in browser

---

### Phase 5: Orchestrator + CLI

**Files**: `agent/orchestrator.py`, `run_pipeline.py`

1. [ ] Create `agent/orchestrator.py`:
   ```python
   class GarminHealthOrchestrator:
       def run(self, days: int = 90) -> dict:
           bundle  = DataAgent().run(days)
           alerts  = AlertAgent().run(bundle)
           analysis = AnalysisAgent().run(bundle, days)
           paths   = ReportAgent().run(bundle, alerts, analysis, days)
           return {"alerts": alerts, "paths": paths}
   ```
2. [ ] Create `run_pipeline.py` at `garmin-health/` root:
   - `argparse` with `--days` (default 90)
   - Print progress: "Loading data...", "Checking alerts...", "Running AI analysis...", "Writing report..."
   - Print each alert with emoji severity prefix
   - Print final: "Report saved to: {html_path}"
   - Exit code 0 on success, 1 on error

---

### Phase 6: Requirements + README update

1. [ ] Create `garmin-health/requirements.txt` (pipeline-level):
   ```
   # Re-export analytics deps
   -r analytics/requirements.txt
   # Pipeline additions
   jinja2>=3.1.0
   markdown>=3.5.0
   ```
2. [ ] Update `garmin-health/TODO.md` — mark pipeline item as done when complete
3. [ ] Add pipeline usage to `garmin-health/README.md`

---

## Files to Create

| File | Purpose |
|------|---------|
| `agent/__init__.py` | Package marker |
| `agent/models.py` | `DataBundle` and `Alert` dataclasses |
| `agent/data_agent.py` | Loads all DataFrames, returns DataBundle |
| `agent/alert_agent.py` | Threshold checks → List[Alert] |
| `agent/analysis_agent.py` | Wraps Claude AI analysis call |
| `agent/report_agent.py` | Assembles + writes Markdown and HTML files |
| `agent/orchestrator.py` | Sequences all 4 agents |
| `run_pipeline.py` | CLI entry point |
| `templates/report.html.jinja2` | Self-contained HTML report template |
| `requirements.txt` | Pipeline-level Python deps |

## Files to Modify

| File | Change |
|------|--------|
| `garmin-health/README.md` | Add "Running the Pipeline" section |
| `garmin-health/TODO.md` | Mark pipeline task complete after execution |

## Files NOT to modify

| File | Why untouched |
|------|---------------|
| `analytics/src/data_loader.py` | Used as-is via import |
| `analytics/src/metrics.py` | Used as-is via import |
| `analytics/src/ai_insights.py` | Used as-is via import |
| `analytics/src/charts.py` | Not needed (no charts in report — text only) |
| `analytics/app.py` | Streamlit dashboard is separate; pipeline is CLI only |
| All `backend/` files | Backend is AWS-only; pipeline is local |

---

## Dependencies

```
# Already in analytics/requirements.txt (re-exported):
streamlit>=1.32.0
plotly>=5.20.0
pandas>=2.0.0
anthropic>=0.25.0
python-dotenv>=1.0.0

# New for pipeline:
jinja2>=3.1.0       # HTML template rendering
markdown>=3.5.0     # Converting AI analysis markdown → HTML in report
```

---

## Running the Pipeline

```bash
# From garmin-health/ directory
cd 01-personal/garmin-health

# Install deps (first time)
pip install -r requirements.txt

# Set up API key
cp analytics/.env.example .env
# Edit .env: add ANTHROPIC_API_KEY=sk-ant-...

# Run pipeline (default: last 90 days)
python run_pipeline.py

# Custom date window
python run_pipeline.py --days 30
python run_pipeline.py --days 180

# Output
# Loading data...
# Checking alerts...
# 🔴 Injury risk: ACWR 1.62. Reduce training load immediately.
# 🟡 Low deep sleep: 11.2% avg (target >15%). Review sleep hygiene.
# Running AI analysis...
# Writing report...
# Report saved to: data/exports/health-report-2026-02-27.html
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| `metrics.compute_acwr` may not exist yet | Check metrics.py for ACWR function; if missing, implement inline in DataAgent |
| `summarizedActivities.json` is very large | Already handled by `data_loader.py` — loads once |
| Anthropic API unavailable | AnalysisAgent returns a fallback string; report still generates |
| Data files not found | DataAgent raises `FileNotFoundError` with clear path message |
| Jinja2 not installed | Caught at import with clear "pip install jinja2" message |

---

## Success Criteria

- [ ] `python run_pipeline.py` runs end-to-end in under 60 seconds
- [ ] HTML report opens in browser with no broken layout
- [ ] Alert section shows correct severity colors
- [ ] Metrics table reflects actual data from JSON files
- [ ] AI analysis references research docs (mentions 80/20, ACWR, sleep stages)
- [ ] Running without `ANTHROPIC_API_KEY` still produces a partial report (no crash)
- [ ] Running `--days 30` and `--days 90` both work correctly

---

## Approval

- [ ] Architecture (orchestrator + 4 sub-agents) approved
- [ ] Alert thresholds acceptable
- [ ] Report format (Markdown + HTML, self-contained) approved
- [ ] CLI interface (`python run_pipeline.py --days N`) approved
- [ ] Ready to execute with `/execute-plan`
