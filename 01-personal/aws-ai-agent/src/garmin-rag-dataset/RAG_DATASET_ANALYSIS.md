# Garmin RAG Dataset Analysis

## Executive Summary

This document analyzes your Garmin Connect data export for RAG (Retrieval-Augmented Generation) training. The dataset spans **5+ years** (2020-2025) of personal health and fitness data.

---

## Dataset Overview

| Category | Files | Size | Records | Date Range |
|----------|-------|------|---------|------------|
| **Activities** | 1 | 3.2 MB | 783 activities | 2020-2025 |
| **Personal Records** | 1 | 11 KB | 48 PRs | 2020-2025 |
| **BioMetrics** | 1 | 133 KB | 339 entries | 2020-2025 |
| **Daily Wellness (UDS)** | 21 | ~7 MB | ~2,100 days | 2020-2025 |
| **Sleep Data** | 21 | ~760 KB | ~2,100 nights | 2020-2025 |
| **Training History** | 21 | ~850 KB | ~2,100 days | 2020-2025 |
| **VO2 Max Metrics** | 21 | ~90 KB | ~450 entries | 2020-2025 |
| **Race Predictions** | 19 | ~520 KB | ~1,900 entries | 2020-2025 |

**Total: ~12 MB of structured JSON data**

---

## Data Structure Analysis

### 1. Activities (`summarizedActivities.json`) - PRIMARY DATASET

**783 activities** with the following breakdown:

| Activity Type | Count | % |
|--------------|-------|---|
| Lap Swimming | 479 | 61% |
| Indoor Running | 128 | 16% |
| Cycling | 80 | 10% |
| Running | 72 | 9% |
| Walking | 16 | 2% |
| Other | 8 | 1% |

**Key Fields for RAG:**
- `activityType`, `name`, `sportType`
- `duration`, `distance`, `elevationGain`
- `avgSpeed`, `maxSpeed`, `avgHr`, `maxHr`
- `calories`, `steps`, `vO2MaxValue`
- `startTimeLocal`, `startLatitude`, `startLongitude`
- `aerobicTrainingEffect`, `anaerobicTrainingEffect`

**RAG Value: ⭐⭐⭐⭐⭐ CRITICAL** - Your main activity history

---

### 2. Daily Wellness (UDS Files) - HIGH VALUE

**~2,100 daily records** with comprehensive wellness metrics:

**Key Fields for RAG:**
- `calendarDate`, `totalSteps`, `dailyStepGoal`
- `totalKilocalories`, `activeKilocalories`, `bmrKilocalories`
- `totalDistanceMeters`
- `minHeartRate`, `maxHeartRate`, `restingHeartRate`
- `moderateIntensityMinutes`, `vigorousIntensityMinutes`
- `allDayStress.averageStressLevel`, `allDayStress.maxStressLevel`
- `bodyBatteryChargedValue`, `bodyBatteryDrainedValue`

**RAG Value: ⭐⭐⭐⭐⭐ CRITICAL** - Daily health snapshots

---

### 3. Sleep Data - HIGH VALUE

**~2,100 sleep records** with:

**Key Fields for RAG:**
- `calendarDate`, `sleepStartTimestampGMT`, `sleepEndTimestampGMT`
- `deepSleepSeconds`, `lightSleepSeconds`, `remSleepSeconds`
- `awakeSleepSeconds`
- `averageRespiration`, `lowestRespiration`, `highestRespiration`

**RAG Value: ⭐⭐⭐⭐ HIGH** - Sleep patterns and quality

---

### 4. Training History - MEDIUM VALUE

**~2,100 training status records:**

**Key Fields for RAG:**
- `calendarDate`, `weeklyTrainingLoadSum`
- `trainingStatus` (e.g., "PRODUCTIVE", "RECOVERY", "NO_STATUS")
- `fitnessLevelTrend`, `loadLevelTrend`
- `loadTunnelMin`, `loadTunnelMax`

**RAG Value: ⭐⭐⭐ MEDIUM** - Training load trends

---

### 5. VO2 Max / Fitness Metrics - MEDIUM VALUE

**Key Fields for RAG:**
- `vo2MaxValue`, `fitnessAge`, `maxMet`
- `calendarDate`, `updateTimestamp`

**RAG Value: ⭐⭐⭐ MEDIUM** - Fitness level tracking

---

### 6. Personal Records - CONTEXT VALUE

**48 personal records** across activities:
- Best 5K, 10K runs
- Farthest runs, cycles
- Best pool swim times
- Most steps records

**RAG Value: ⭐⭐ CONTEXT** - Achievement milestones

---

## Recommended RAG Processing Strategy

### Phase 1: Data Consolidation

Merge time-series files into single consolidated files:

```
processed/
├── activities_all.json          # All 783 activities
├── wellness_daily_all.json      # All ~2,100 daily records
├── sleep_all.json               # All ~2,100 sleep records
├── training_history_all.json    # All training status records
├── metrics_vo2max_all.json      # All VO2 max records
├── personal_records.json        # All PRs
└── user_profile.json            # User metadata
```

### Phase 2: Create RAG-Optimized Documents

Transform raw JSON into natural language documents for better embedding:

**Example Activity Document:**
```
On December 6, 2025, you completed a Running activity.
Duration: 1 hour 10 minutes
Distance: 11.21 km
Average Heart Rate: 171 bpm (Max: 189 bpm)
Calories: 3,373 kcal
Training Effect: Highly improving lactate threshold
VO2 Max: 47
```

**Example Daily Wellness Document:**
```
Daily Summary for January 8, 2024:
Steps: 9,772 (Goal: 9,720) ✓
Calories: 2,185 kcal (Active: 243, BMR: 1,942)
Heart Rate: Min 48, Max 116, Resting 55 bpm
Stress: Average 27, Max 94
```

### Phase 3: Chunking Strategy for Embeddings

| Document Type | Chunk Strategy | Chunk Size |
|--------------|----------------|------------|
| Activities | 1 activity = 1 chunk | ~500 tokens |
| Daily Wellness | 1 day = 1 chunk | ~300 tokens |
| Sleep | 1 night = 1 chunk | ~200 tokens |
| Weekly Summaries | 7 days = 1 chunk | ~800 tokens |
| Monthly Summaries | 30 days = 1 chunk | ~1,200 tokens |

### Phase 4: Create Derived Insights

Generate computed summaries for better retrieval:

1. **Weekly Summaries** - Aggregate stats per week
2. **Monthly Summaries** - Trends and patterns
3. **Activity Type Summaries** - Stats per sport
4. **Personal Bests Timeline** - PR progression
5. **Training Load Trends** - Overtraining/recovery patterns

---

## Questions Your RAG Agent Can Answer

### Activity Questions
- "What was my longest run this year?"
- "How many times did I swim in 2024?"
- "What's my average cycling distance?"
- "Show my running pace improvement over time"

### Health Questions
- "What's my average resting heart rate?"
- "How has my sleep quality changed?"
- "What days do I have the most stress?"
- "What's my average daily step count?"

### Training Questions
- "Am I overtraining this week?"
- "What's my current VO2 Max trend?"
- "When did I set my 5K PR?"
- "How does my training load compare to last month?"

### Pattern Questions
- "What time do I usually work out?"
- "Which day of the week am I most active?"
- "How does my sleep affect my performance?"

---

## Implementation Recommendations

### For AWS Bedrock RAG:

1. **Vector Store**: Use Amazon OpenSearch Serverless or Pinecone
2. **Embedding Model**: Amazon Titan Embeddings or Cohere
3. **Chunk Size**: 512-1024 tokens
4. **Overlap**: 50-100 tokens between chunks
5. **Metadata**: Include date, activity type, metrics for filtering

### Data Privacy Considerations:
- Remove GPS coordinates if not needed
- Anonymize user profile IDs
- Consider date obfuscation for demos

---

## Next Steps

1. **Run consolidation script** to merge all time-series files
2. **Generate natural language documents** from JSON
3. **Create embeddings** and store in vector database
4. **Build retrieval pipeline** with your AWS agent
5. **Test with sample queries** to validate accuracy
