# Garmin Analyzer

A production-quality analysis tool for Garmin health and activity data, purpose-built for endurance athletes and health-conscious professionals. Analyzes sleep, training load, running performance, swimming efficiency, and recovery status to generate evidence-based recommendations for sustainable progress.

## Features

- **Multi-format ingestion**: JSON, CSV, XLSX, Markdown
- **Robust normalization**: Handles missing data, inconsistent schemas, duplicates
- **Sports-science driven**: 80/20 running, CSS swimming, HRV recovery, ACWR load balance
- **Trend analysis**: Rolling averages, change detection, anomaly flagging
- **Risk detection**: Overtraining, under-recovery, injury, plateau, illness signals
- **Actionable recommendations**: Specific, time-bounded, sport-specific guidance
- **Masters-athlete tuned**: Durability, recovery, injury prevention focus
- **Modular architecture**: Parsers, metrics, rules, and reporting are independent

## Installation

### Prerequisites
- Python 3.9+
- pip

### Setup

```bash
# Clone or copy the skill into .claude/skills/
cd .claude/skills/garmin-analyzer

# Install dependencies
pip install -r requirements.txt

# (Optional) Install in development mode
pip install -e .
```

## Usage

### Command Line

```bash
# Analyze a directory of Garmin exports
python -m garmin_analyzer analyze ./exports --output report.md

# Analyze a single file
python -m garmin_analyzer analyze ./sleep_all_merged.json --output report.md

# Compact summary (less detailed recommendations)
python -m garmin_analyzer summarize ./exports --output summary.md

# JSON output (for programmatic use)
python -m garmin_analyzer analyze ./exports --format json --output summary.json
```

### Python API

```python
from garmin_analyzer import GarminAnalyzer

analyzer = GarminAnalyzer(
    athlete_profile={
        "age": 47,
        "weight_kg": 70,
        "height_m": 1.77,
        "vo2max_estimate": 55,
        "primary_sports": ["running", "swimming"]
    }
)

# Load and analyze
report = analyzer.analyze_folder("./exports")
print(report.to_markdown())

# Or analyze a single file
sleep_report = analyzer.analyze_file("sleep_all_merged.json")
```

### Within Claude Code

When used as a skill in Claude Code:

```
/garmin-analyzer /path/to/exports --output report.md --athlete-age 47
```

The skill will:
1. Ingest all Garmin files
2. Parse and normalize data
3. Compute metrics and trends
4. Apply interpretation rules
5. Generate a structured markdown report
6. Return key insights and top recommendation

## Supported File Types

### JSON
- `sleep_all_merged.json` — Sleep windows, stages, respiration
- `training_history_all_merged.json` — Weekly load, training status, fitness/load trends
- `vo2max_metrics_all_merged.json` — VO₂ max, fitness age, max MET
- `race_predictions_all_merged.json` — Race prediction trend
- `*_userBioMetrics.json` — Weight, height, biometric changes
- `*_personalRecord.json` — PR metadata

### CSV
- `SleepData.csv` — Sleep summaries (nightly duration, quality)
- Activity exports with columns like: Date, Distance, Time, HR, Pace, Calories

### XLSX
- `my_garmin_swimming_pool.xlsx` — Pool swims with pace, SWOLF, stroke rate, etc.
- Any activity log with sport-specific columns

### Markdown
- `Research_Summary_*.md` — Interpretation rules and baselines

## Architecture

```
garmin_analyzer/
├── parsers/          # File ingestion (JSON, CSV, XLSX, Markdown)
├── normalization/    # Date, unit, schema normalization; deduplication
├── metrics/          # Compute sleep, load, recovery, running, swimming metrics
├── rules/            # Interpretation rules: fatigue, risk, recommendation logic
├── reporting/        # Markdown, JSON, compact report generation
├── cli.py            # Command-line interface
├── pipeline.py       # Orchestration: parse → normalize → compute → analyze → report
├── models.py         # Typed data model (sleep, load, recommendations, etc.)
└── config.py         # Configuration, thresholds, athlete profile
```

### Data Flow

```
Raw Garmin Exports
        ↓
    [Parsers]        → SourceRecord objects
        ↓
[Normalization]      → DailySleepSummary, DailyLoadSummary, etc.
        ↓
  [Metrics]          → Trends, rolling averages, efficiency scores
        ↓
  [Rules]            → Risk flags, fatigue classification, opportunities
        ↓
[Reporting]          → Markdown/JSON report with recommendations
```

## Core Modules

### `models.py`
Typed internal objects:
- `SourceRecord` — Raw input with metadata
- `DailySleepSummary` — Sleep metrics and confidence
- `DailyTrainingLoadSummary` — Acute/chronic load, ACWR, training status
- `RunningSessionSummary` — Run metrics: pace, cadence, efficiency, VO₂ impact
- `SwimmingSessionSummary` — Swim metrics: pace, SWOLF, stroke rate/length, aerobic TE
- `RiskFlag` — Overtraining, under-recovery, injury, plateau signals
- `Recommendation` — Action, reason, benefit, timeframe, priority

### `parsers/`
- `json_parser.py` — Garmin JSON exports (sleep, training history, VO₂, etc.)
- `csv_parser.py` — Sleep and activity CSV files
- `xlsx_parser.py` — Activity logs, swim details from Excel
- `md_parser.py` — Research summaries and manual notes

### `normalization/`
- `dates.py` — Converts any date format to ISO 8601
- `units.py` — Normalizes pace, distance, HR, time to standard units
- `dedupe.py` — Removes duplicate records by (date, sport, type)
- `schema_map.py` — Maps heterogeneous field names to canonical schema

### `metrics/`
- `sleep_metrics.py` — Duration, consistency, deep/REM trends, respiration, recharge quality
- `load_metrics.py` — 7-day/28-day rolling load, ACWR, monotony, load tensor
- `recovery_metrics.py` — HRV trend, Body Battery, stress, Training Readiness
- `running_metrics.py` — VO₂ max trend, cadence, efficiency, race prediction
- `swimming_metrics.py` — Pace, SWOLF, stroke rate/length balance, aerobic TE
- `trend_metrics.py` — Linear regression, change-point detection, anomaly flagging

### `rules/`
- `sleep_rules.py` — Sleep score interpretation, deep/REM balance, readiness signals
- `running_rules.py` — Durability checks, intensity balance, load distribution, efficiency
- `swimming_rules.py` — Stroke efficiency, session type classification, progression
- `risk_rules.py` — Overtraining (ACWR, readiness collapse), injury (load spikes), illness
- `recommendation_rules.py` — Generate specific actions based on detected conditions

### `reporting/`
- `markdown_report.py` — Full structured report (executive summary, 7 sections, recommendations)
- `json_report.py` — Programmatic output (metrics, flags, recommendations)
- `compact_summary.py` — Brief summary (status, top 3 insights, primary action)

### `pipeline.py`
Orchestrates the entire workflow:
1. Discover and parse all input files
2. Normalize and deduplicate
3. Compute metrics and trends
4. Apply interpretation rules
5. Generate report

### `cli.py`
Command-line interface with subcommands:
- `analyze` — Full analysis and report
- `summarize` — Compact summary
- `export` — JSON export for downstream processing

## Example Output

See `examples/sample_output.md` for a realistic full report.

### Sample Report Structure

```markdown
# Garmin Health Analysis Report
**Date Range**: 2026-02-14 to 2026-03-13 (28 days)
**Athlete**: Male, 47y, 70kg, 1.77m | VO₂ max ~55 mL/kg/min

## Executive Summary

**Physiological Status**: Managing accumulated fatigue; ready for recovery week

**Readiness Level**: Moderate (can maintain, not ready for new hard blocks)

**Main Opportunity**: Reduce intensity for 7–10 days; prioritize sleep consistency above 8 hours

**Top 3 Insights**:
1. ACWR drifted to 1.55 over past 7 days with concurrent sleep decline (average 7.2h)
2. VO₂ max stable; running pace consistent but cadence trending high (182 rpm avg), suggests fatigue
3. Swimming pace holding steady (1:42/100m) on lower frequency; technical efficiency preserved

---

## Training Load Analysis
...
```

## Configuration

Configuration is in `src/garmin_analyzer/config.py`. You can override at runtime:

```python
from garmin_analyzer import GarminAnalyzer
from garmin_analyzer.config import Config

config = Config(
    athlete_age=47,
    athlete_weight_kg=70,
    target_sleep_hours=8.5,
    acwr_warning_threshold=1.5,
    vo2_steady_state_window=28,  # days
)

analyzer = GarminAnalyzer(config=config)
```

### Key Thresholds

```yaml
# Sleep
sleep_target_hours: 8.0 to 8.5
sleep_consistency_window: 7 days
sleep_score_good: 74+
sleep_score_poor: <60

# Training Load
acwr_ideal_range: 0.8 to 1.3
acwr_warning: 1.5+
acwr_critical: 2.0+

# Running
running_intensity_threshold_rpm: 170 to 185 (cadence)
running_load_spike_threshold: 120% of 28-day average

# Swimming
swimming_swolf_efficiency_target: <210 for distance swimmer
stroke_rate_efficiency_range: 55 to 75 spm

# Recovery
readiness_good: 75+
readiness_moderate: 50 to 74
readiness_poor: <50

# Wellness
illness_rhr_elevation: >5 bpm above personal baseline
sympathetic_dominance_hrv_drop: >20% below 28-day baseline
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_parsers.py -v

# Run with coverage
pytest tests/ --cov=garmin_analyzer --cov-report=term-missing
```

### Test Coverage

- `test_parsers.py` — JSON, CSV, XLSX, Markdown parsing
- `test_normalization.py` — Date conversion, unit normalization, deduplication
- `test_metrics.py` — Sleep, load, recovery, running, swimming metric computation
- `test_rules.py` — Fatigue classification, risk detection, recommendation logic
- `test_pipeline.py` — End-to-end integration with sample data

## Extension Guide

### Adding a New Sport

1. **Create** `metrics/sport_metrics.py` with computation logic
2. **Add** sport-specific rules in `rules/sport_rules.py`
3. **Update** parsers to detect and normalize the sport
4. **Add** tests in `tests/test_metrics.py`
5. **Update** reporting to include new sport section

### Adding a New Metric

1. Implement in the relevant metrics module
2. Add unit tests
3. Create a rule that uses it (in `rules/`)
4. Update the report template to surface it

### Adding a New Data Source

1. Implement parser in `parsers/`
2. Test on sample file
3. Add normalization mappings in `normalization/schema_map.py`
4. Update `cli.py` to auto-discover the new type

## Known Limitations

- Sleep architecture accuracy depends on Garmin's algorithm; unconfirmed nights are down-weighted
- Race predictions are directional; absolute times less reliable
- VO₂ max estimated from pace/HR; field-tested value more accurate
- SWOLF accuracy depends on pool size and Garmin calibration
- Does not account for altitude, heat, illness, or life stress outside Garmin
- Requires at least 7 days of data for meaningful trend analysis; 28 days recommended

## Future Work

- [ ] Multi-sport support (cycling, strength, flexibility)
- [ ] Power meter integration (watts, power duration curve)
- [ ] Real-time alerting (high ACWR, HRV collapse, load spike)
- [ ] Bayesian threshold learning (per-athlete calibration)
- [ ] Calendar integration (planned taper, race events, life events)
- [ ] Video recommendation links (technique improvement)
- [ ] Garmin Coaching AI suggestions
- [ ] Slack/email integration (scheduled reports)

## Development

```bash
# Install in dev mode with test dependencies
pip install -e ".[dev]"

# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/

# Run full test suite
pytest tests/ -v --cov
```

## License

Proprietary. Part of the MyFirstRepo multi-project workspace.

## Support

For issues, questions, or feature requests:
- Check the SKILL.md for detailed methodology
- Review test files for usage examples
- Inspect sample output for expected report structure

---

**Status**: Production Ready (v1.0)
**Last Updated**: 2026-03-13
**Maintainer**: Claude Code
