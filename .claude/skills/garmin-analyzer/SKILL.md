# Garmin Analyzer Skill

## Purpose

The Garmin Analyzer skill reads Garmin Connect health and activity exports, normalizes heterogeneous data sources, and produces evidence-based analysis of sleep, training load, running performance, swimming efficiency, and recovery status. It is purpose-built for serious endurance athletes and health-conscious professionals who use Garmin for long-term health preservation and sustainable performance.

## When to Use This Skill

Invoke this skill when you need to:
- **Analyze sleep trends** and correlate with training readiness
- **Assess training load balance** (acute vs. chronic, monotony, spikes)
- **Interpret running performance** and readiness indicators (VO₂ max, race prediction, efficiency)
- **Evaluate swimming efficiency** (pace, SWOLF, stroke rate / length balance)
- **Detect recovery mismatch** or overtraining risk
- **Generate actionable recommendations** for training adjustment, recovery, and sleep optimization
- **Monitor fatigue, detraining, plateaus, or performance opportunities** over weeks to months

This skill is especially suited for:
- Garmin sleep and wellness exports
- Training history and load data (JSON, CSV, XLSX)
- Running and swimming activity summaries
- VO₂ max and race prediction trends
- Correlative analysis across multiple data dimensions

## Supported Input Formats

### File Types
- **JSON**: Garmin-style exports (sleep, training history, VO₂ max, race predictions, user biometrics, personal records)
- **CSV**: Sleep summaries, activity summaries, export logs
- **XLSX**: Pool swim logs, activity tables with sport-specific fields
- **Markdown**: Research summaries, notes, manual annotations

### Known File Patterns

The skill recognizes and normalizes:
- `sleep_all_merged.json` — sleep windows, stages (deep, REM, light), respiration, confirmation type
- `training_history_all_merged.json` — sport, weekly load, load tunnel, training status, fitness/load trends
- `vo2max_metrics_all_merged.json` — VO₂ max value, fitness age, max MET, trend
- `race_predictions_all_merged.json` — race prediction trend and distances
- `[...}_userBioMetrics.json` — weight, height, biometric change points
- `my_garmin_swimming_pool.xlsx` — distance, time, pace, HR, TE, SWOLF, stroke rate, stroke count
- `SleepData.csv` — nightly sleep summaries with duration and quality metrics
- `Research_Summary_*.md` — interpretation rules, thresholds, and athlete context

### Robustness

The skill gracefully handles:
- Missing or null values
- Inconsistent field naming (e.g., `pace_seconds_per_500m` vs `pace`)
- Duplicate records with deduplication
- Partial or incomplete exports
- Off-wrist artifacts and low-confidence data markers
- Mixed date/time formats (ISO 8601, US/EU, Unix timestamps)
- Sport-specific fields present only for certain activity types

## Analysis Philosophy

### Interpretation Over Raw Metrics

The skill does not repeat raw numbers. Instead, it:
- Computes trends (rolling averages, variance, direction)
- Interprets relative to personal baselines and periodicity
- Flags anomalies, opportunities, and risks
- Provides context from sports science (80/20 running, CSS swimming, HRV as recovery proxy)

### Confidence and Uncertainty

Every conclusion includes a confidence assessment:
- **High confidence**: Multiple independent data sources agree; long history; consistent pattern
- **Medium confidence**: Limited data or inferred from correlated metrics
- **Low confidence**: Single source; recent change; missing validation; unclear cause

Tentative conclusions are explicitly flagged. Medical or diagnostic claims are avoided.

### Trend Analysis Over Time

The skill emphasizes:
- **Rolling averages** (7-day, 14-day, 28-day depending on metric)
- **Change direction** (improving, stable, declining)
- **Velocity** (how fast is it changing?)
- **Patterns** (weekly cycles, bi-weekly blocks, monthly periodization hints)
- **Outliers** (single bad night; exceptional training day)

## Supported Analysis Dimensions

### Sleep and Recovery
- **Nightly duration** and consistency (target 8.0–8.5 hours where feasible)
- **Sleep architecture**: deep sleep (physical recovery), REM (cognitive/neural recovery), light sleep (restorative)
- **Respiration quality** (breathing rate stability during sleep)
- **Garmin Sleep Score** interpretation (74+ is strong; <60 suggests recovery need)
- **Body Battery** as a directional proxy (not absolute truth)
- **Training Readiness** integration (sleep + HRV + stress + acute load)
- **Confidence weighting** (unconfirmed/low-confidence nights down-weighted)
- **Recovery trajectory**: Are you recharging after hard blocks, or accumulating debt?

### Training Load
- **Acute vs. Chronic balance** (ACWR 0.8–1.3 ideal; >1.5 elevated injury risk)
- **Weekly and monthly load patterns**
- **Load spikes** and their timing relative to sleep, readiness, and performance
- **Monotony**: Is load varied across intensities, or too much at one level?
- **Detraining windows**: Periods of insufficient stimulus
- **Productive fatigue vs. under-recovery**: Is fatigue leading to adaptation, or accumulating stale?

### Running (Masters-Athlete Lens)
- **VO₂ max trend**: Direction and stability over months
- **Race prediction trajectory** if available
- **Running efficiency** and economy signals
- **Durability focus**: recovery spacing, load density, weekly structure
- **Intensity balance**: 80/20 principle where inferable (80% easy, 20% hard)
- **Cadence trends** (ideally 170–185 rpm depending on pace and athlete context)
- **Long-run structure**, tempo/threshold work, recovery week patterns, consistency
- **Strength and mobility signals**: Are injuries or asymmetries emerging?

### Swimming (Technical Efficiency & Longevity)
- **Swim frequency** and progression
- **Pace consistency** and best pace behavior
- **SWOLF trend** (strokes + time per 25/50m; lower is more efficient)
- **Stroke rate (SR) and stroke length (SL) balance**: Preserve efficiency over brute-force rate
- **Stroke count per lap** and variability
- **Session profiles**: Aerobic endurance, threshold/CSS-like, technique, recovery, anaerobic
- **Shoulder health signals**: Load distribution, recovery patterns, interval intensity
- **Masters-specific technique**: EVF, straight-through pull, rotation, injury prevention

### Cross-Domain Correlations
- **Sleep quality → Training behavior**: Poor sleep often precedes poor quality workouts
- **Load spikes → Recovery mismatch**: High load without adequate sleep/HRV recovery
- **Performance decoupling**: Performance metrics still look good, but readiness/recovery reserves are declining
- **Fatigue types**: Productive fatigue (adaptation) vs. stale fatigue (under-recovery) vs. overreaching (unsustainable)
- **Detraining vs. recovery week**: Is reduced load intentional periodization, or unwanted decrement?
- **Sympathetic dominance**: Stress, poor HRV, poor sleep, elevated RHR—cluster suggests systemic stress

## Canonical Data Model

Internally, the skill normalizes all inputs into typed objects:

- **SourceRecord**: Raw input row with metadata (file, type, date, confidence)
- **DailySleepSummary**: Sleep duration, stages, respiration, quality score, confidence
- **DailyRecoverySummary**: HRV, Body Battery, stress level, readiness, resting HR
- **DailyTrainingLoadSummary**: Acute load, chronic load, ACWR, training status, intensity distribution
- **DailyWellnessSummary**: Aggregated sleep + load + recovery for a given date
- **RunningSessionSummary**: Date, distance, pace, HR zones, VO₂ impact, cadence, efficiency metrics
- **SwimmingSessionSummary**: Date, distance, pace, SWOLF, stroke rate/count, efficiency, session type
- **VO₂TrendPoint**: Date, VO₂ max value, fitness age, confidence, direction
- **RacePredictionPoint**: Date, race distance, predicted time, trend
- **RiskFlag**: Date, risk type (overtraining, under-recovery, plateau, etc.), severity, contributing factors
- **Recommendation**: Action, reason, expected benefit, suggested timeframe, priority

Each object includes:
- Source traceability (which file, which date range)
- Confidence scoring (high/medium/low)
- Missingness flags (which fields were unavailable?)
- Raw and normalized values

## Parsing and Normalization

The skill ingests heterogeneous formats:

1. **JSON Garmin exports**: Detects schema (sleep, training history, biometrics, etc.) and extracts typed records
2. **CSV files**: Infers headers, handles various date formats, deduplicates by date+type
3. **XLSX activity logs**: Reads sport-specific columns, normalizes pace/pace variants, aggregates laps
4. **Markdown research notes**: Extracts thresholds, baselines, and interpretation rules

After parsing:
- **Date normalization**: All timestamps converted to ISO 8601 YYYY-MM-DD (or YYYY-MM-DD HH:MM:SS for intra-day)
- **Unit normalization**: Pace to min/km, distance to km, HR to bpm, time to seconds
- **Deduplication**: By (date, sport, type) key
- **Validation**: Removes implausible values (pace < 2:00/km, HR > 220, sleep duration > 12 hours)
- **Confidence scoring**: Marks low-confidence data based on source type and metadata

## Analysis Engine

The engine computes:

1. **Time-series aggregation**:
   - Rolling 7-day and 28-day averages for load, sleep, recovery metrics
   - Weekly and bi-weekly patterns

2. **Trend detection**:
   - Linear regression or LOWESS smoothing for long-term direction
   - Change-point detection for abrupt shifts

3. **Fatigue / stress classification**:
   - Productive fatigue: Load increasing, sleep maintaining, readiness declining but controlled
   - Under-recovery: Load moderate-to-high, sleep poor or inconsistent, readiness low
   - Overreaching: High load, poor sleep, readiness collapsing, performance not improving
   - Detraining: Load declining below baseline for >10 days with no stimulus
   - Monotony: Load repeated at same intensity without variation

4. **Risk scoring**:
   - Overtraining: High ACWR, declining readiness, poor sleep cluster
   - Injury: Load spikes, rapid intensity increase, declining recovery pattern
   - Illness: Elevated RHR, poor HRV, poor sleep, low readiness over 3+ days
   - Plateau: Performance metrics flat despite good load, or performance declining despite high load

5. **Opportunity detection**:
   - Ready for intensity: Good sleep, high readiness, stable or rising load
   - Recovery opportunity: Accumulated fatigue + reduced load = rebound likely
   - Efficiency gain: SWOLF or pace improving with stable/lower effort

## Report Structure

Every full analysis produces a structured markdown report with:

### 1. Executive Summary
- **Physiological status** (well-recovered, managing fatigue, under-recovered, overreaching)
- **Readiness level** (ready for hard work, ready for maintenance, need recovery)
- **Main risk or opportunity** (what should you do in the next 7 days?)
- **Top 3 insights** (specific findings that support the recommendations)

### 2. Training Load Analysis
- **Acute vs. chronic interpretation** (current load relative to baseline)
- **Load trend** (direction over past 28 days)
- **Status classification** (maintaining, building, tapering, detraining, overreaching, recovering)
- **Fatigue accumulation signals** (poor sleep, low readiness, high monotony)
- **Spikes, gaps, monotony** (when and how much?)

### 3. Cardiovascular & Performance Analysis
- **VO₂ max trend** (stable, improving, declining; by how much over what period?)
- **Race prediction trajectory** (if data available)
- **Running efficiency or swim efficiency signals** when inferable
- **Threshold or aerobic capacity insights** based on available metrics

### 4. Sleep & Recovery Analysis
- **Sleep duration consistency** (rolling average, variability, target alignment)
- **Deep sleep and REM trends** (are they supporting recovery?)
- **Respiration patterns** (if available; elevated RR = stress/illness signal)
- **Recharge quality**: Can you accumulate high load and still recover well?
- **Readiness interpretation**: How well do sleep metrics align with training readiness?
- **Recovery vs. training demand balance**: Is load sustainable given sleep?

### 5. Risk Detection
- **Overtraining risk** (probability and contributing factors)
- **Under-recovery risk** (insufficient sleep or readiness relative to load)
- **Injury-risk indicators** (load spikes, poor load distribution, declining recovery reserve)
- **Plateau or stagnation** (performance not improving despite good load)
- **Sympathetic dominance** (stress accumulation: poor HRV, poor sleep, elevated RHR)
- **Sleep debt accumulation** (rolling deficit over 1–2 weeks)
- **Illness vulnerability** (RHR elevation, HRV degradation, poor sleep)

### 6. Recommendations
Each recommendation includes:
- **Action**: Specific, measurable, time-bounded (e.g., "reduce intensity density to 1 hard session per week for 7 days")
- **Reason**: Why (e.g., "ACWR 1.6 + poor sleep suggests high injury risk")
- **Expected benefit**: What you should observe (e.g., "readiness should rise 5–10 points; sleep duration should increase")
- **Timeframe**: Typical duration (e.g., "7–10 days before reassessment")
- **Priority**: High, medium, low based on urgency

Examples:
- Reduce intensity density to 1 hard session/week
- Increase Zone 2 proportion (80/20 structure)
- Shift bedtime 30 min earlier; reduce late caffeine
- Add 1–2 strength sessions focused on soleus, glutes, core
- Focus on swim technique while reducing run stress
- Insert 2–3 easy aerobic days after poor sleep cluster
- Maintain swim efficiency (CSS-like pace) rather than increasing rate

### 7. Confidence & Data Quality Notes
- **High-confidence conclusions**: Which recommendations rest on strong, multi-source evidence?
- **Tentative conclusions**: Which insights are inferred or limited by data gaps?
- **Missing data**: What would be valuable to add?
- **Assumptions**: What athlete profile or context are we assuming?
- **Next steps**: What metrics should be tracked or verified?

## Narrative Style

The report must be:
- **Analytical**: Grounded in computed metrics and rules, not intuition
- **Structured**: Clear headings, bullet points, logical flow
- **Concise but deep**: Every sentence adds value; no filler
- **Practical**: Recommendations are actionable and sport-specific
- **Confident without overstatement**: Distinguish between fact, inference, and speculation

Do **not**:
- Repeat raw numbers without interpretation
- Provide medical diagnosis or treatment advice
- Use generic wellness clichés ("listen to your body")
- Overstate certainty without evidence
- Make recommendations that contradict the data

## Usage

### CLI Invocation

```bash
# Analyze a folder of Garmin exports
garmin-analyzer analyze /path/to/garmin/exports/ --output report.md

# Analyze a single file
garmin-analyzer analyze /path/to/sleep_all_merged.json --output report.md

# Generate compact summary (no full recommendations)
garmin-analyzer summarize /path/to/exports/ --output summary.md

# Export JSON summary
garmin-analyzer analyze /path/to/exports/ --output summary.json --format json
```

### Within Claude Code / as a Skill

When invoked as a skill:
1. Receive file paths or raw data from the user
2. Parse and normalize all inputs
3. Run the analysis engine
4. Generate a structured markdown report
5. Highlight top 3 insights and primary recommendation
6. Return report path and key findings

## Limitations and Future Work

### Current Scope
- Focuses on sleep, training load, running, and swimming
- Does not analyze cycling, strength training, or other sports in depth
- Requires Garmin or compatible data (not arbitrary wearable formats)
- Does not integrate real-time biometric APIs (analyzes static exports)

### Known Limitations
- Sleep architecture accuracy depends on Garmin's algorithm; nights marked unconfirmed have lower confidence
- Race predictions are directional; absolute times less reliable
- VO₂ max estimated from pace/HR; field-tested VO₂ max more reliable
- SWOLF and stroke metrics depend on pool size and Garmin algorithm
- Does not account for altitude, heat, illness, or extraneous life stress not captured in Garmin

### Future Extensions
- Multi-sport analysis (cycling, strength, flexibility)
- Integration with power meter data (watts, power duration curve)
- Garmin Coaching AI integration for personalized plan suggestions
- Real-time alerting (high ACWR, HRV collapse, load spike) via webhooks
- Bayesian update of athlete-specific thresholds as more data accumulates
- Integration with calendar/schedule (planned taper, race event, life events)
- Video annotation (link recommendations to technique videos)

## Athlete Profile Assumptions

This skill is calibrated for:
- **Male, age ~47, ~70 kg, 1.75–1.80 m**
- **Strong aerobic profile** (VO₂ max likely 50–60 mL/kg/min or higher based on run pace)
- **Endurance focus**: Running and swimming as primary activities
- **Masters-athlete perspective**: Durability, recovery, and injury prevention > pure speed
- **Knowledge-worker background**: Values sleep, stress management, and sustainable progress
- **Garmin ecosystem user**: Trusts Garmin metrics but aware they are estimates

Recommendations are tuned for this profile. For significantly different athletes (sprinter, younger, different sport mix), thresholds and emphasis should be reviewed.

## Integration Notes

The skill is designed to be:
- **Modular**: Parsers, normalization, metrics, rules, and reporting are separate modules
- **Extensible**: New sports, new metrics, new rules can be added without refactoring the core
- **Testable**: Each component has unit tests; end-to-end tests verify output quality
- **Production-ready**: Error handling, logging, and data validation throughout
- **Documented**: Code comments explain non-obvious logic; assumptions are explicit

See the README and source code for implementation details.

---

**Version**: 1.0
**Last updated**: 2026-03-13
**Author**: Claude Code
**Status**: Production Ready
