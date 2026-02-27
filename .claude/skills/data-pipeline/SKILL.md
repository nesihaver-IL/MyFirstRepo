---
name: data-pipeline
description: Manage Garmin data ingestion, ETL pipeline, and RAG dataset operations. Use when ingesting new Garmin exports, migrating data files, updating Lambda ETL functions, or managing RAG ZIP batches. Triggers on keywords like ingest data, pipeline, migrate dataset, garmin data, etl, rag dataset.
---

# Data Pipeline

Manage the end-to-end Garmin health data pipeline: from raw export → Lambda ETL → DynamoDB → RAG datasets → Streamlit dashboard.

## Purpose

- Ingest new Garmin JSON exports into the data layer
- Run and maintain Lambda ETL functions
- Manage RAG ZIP dataset batches
- Execute the pending migration: `aws-ai-agent/docs/` → `garmin-health/data/raw/`
- Normalize and validate data before storage

## Pipeline Architecture

```
Garmin Connect API
        ↓
Lambda: garmin-fetch (OAuth + fetch)
        ↓
Lambda: garmin-oauth (token management)
        ↓
Lambda: garmin-webhook (real-time events)
        ↓
DynamoDB (garmin-activities, garmin-wellness)
        ↓
Lambda: garmin-analyzer (metrics computation)
        ↓
garmin-health/data/
├── raw/        ← Garmin JSON exports (gitignored large files)
├── processed/  ← Normalized records
└── exports/    ← Generated reports + charts
        ↓
RAG ZIP batches (garmin-health/datasets/)
        ↓
Streamlit Dashboard (analytics/app.py)
```

## When to Use

- After downloading a new Garmin data export
- When updating Lambda ETL functions
- When preparing new RAG dataset batches
- Executing the pending data migration
- Debugging DynamoDB read/write issues
- Refreshing the analytics dashboard with new data

## Data File Inventory

### Raw Garmin Exports

| File | Contents | Current Location | Target |
|------|---------|-----------------|--------|
| `nesihaver@gmail.com_0_summarizedActivities.json` | All activities (runs + swims) | `aws-ai-agent/docs/` | `garmin-health/data/raw/` |
| `sleep_all_merged.json` | Nightly sleep records | `aws-ai-agent/docs/` | `garmin-health/data/raw/` |
| `wellness_all_merged.json` | Daily wellness (HRV, stress, steps) | `aws-ai-agent/docs/` | `garmin-health/data/raw/` |
| `vo2max_metrics_all_merged.json` | VO2Max history | `aws-ai-agent/docs/` | `garmin-health/data/raw/` |
| `race_predictions_all_merged.json` | Race time predictions | `aws-ai-agent/docs/` | `garmin-health/data/raw/` |
| `training_history_all_merged.json` | Training load history | `aws-ai-agent/docs/` | `garmin-health/data/raw/` |

### RAG Datasets

| ZIP Batch | Contents | Location |
|-----------|---------|---------|
| `activities-batch-*.zip` | Activity records for RAG | `garmin-health/datasets/` |
| `wellness-batch-*.zip` | Wellness data for RAG | `garmin-health/datasets/` |
| `training-batch-*.zip` | Training history for RAG | `garmin-health/datasets/` |

## How It Works

1. **Ingest**: Download Garmin export or trigger Lambda fetch
2. **Validate**: Check JSON schema and completeness
3. **Normalize**: Convert to standard record format
4. **Store**: Write to `data/raw/` and/or DynamoDB
5. **Process**: Run normalization → `data/processed/`
6. **Package**: Create/update RAG ZIP batches in `datasets/`
7. **Verify**: Confirm dashboard loads updated data

## Usage

```
/data-pipeline
```

Or natural language:
```
"migrate the garmin json files to data/raw"
"ingest the new activity export"
"update the rag dataset with recent activities"
"why is the data loader failing to find the sleep file?"
```

## Pending Migration (High Priority)

Move raw JSON files from legacy location to correct data layer:

```bash
# Step 1: Create target directory (if not exists)
mkdir -p 01-personal/garmin-health/data/raw

# Step 2: Copy files (verify paths first)
ls 01-personal/aws-ai-agent/docs/*.json

# Step 3: Copy JSON files
cp 01-personal/aws-ai-agent/docs/*summarizedActivities*.json \
   01-personal/garmin-health/data/raw/

cp 01-personal/aws-ai-agent/docs/sleep_all_merged.json \
   01-personal/garmin-health/data/raw/

cp 01-personal/aws-ai-agent/docs/wellness_all_merged.json \
   01-personal/garmin-health/data/raw/

cp 01-personal/aws-ai-agent/docs/vo2max_metrics_all_merged.json \
   01-personal/garmin-health/data/raw/

cp 01-personal/aws-ai-agent/docs/race_predictions_all_merged.json \
   01-personal/garmin-health/data/raw/

cp 01-personal/aws-ai-agent/docs/training_history_all_merged.json \
   01-personal/garmin-health/data/raw/

# Step 4: Update data_loader.py path
# Change DATA_DIR in analytics/src/data_loader.py

# Step 5: Verify dashboard still loads
cd 01-personal/garmin-health/analytics && streamlit run app.py
```

## Data Normalization Patterns

### Activity record normalization
```python
def normalize_activity(raw: dict) -> dict:
    """Normalize a Garmin activity record to standard schema."""
    return {
        "id": raw.get("activityId"),
        "date": raw.get("startTimeLocal", "")[:10],  # YYYY-MM-DD
        "type": raw.get("activityType", {}).get("typeKey", "unknown"),
        "duration_seconds": raw.get("duration", 0),
        "distance_meters": raw.get("distance", 0),
        "avg_hr": raw.get("averageHR"),
        "max_hr": raw.get("maxHR"),
        "calories": raw.get("calories", 0),
        "avg_pace_min_km": compute_pace(raw.get("duration"), raw.get("distance")),
    }

def compute_pace(duration_sec: float, distance_m: float) -> float | None:
    if not distance_m or distance_m == 0:
        return None
    km = distance_m / 1000
    return (duration_sec / 60) / km  # min/km
```

### Sleep record normalization
```python
def normalize_sleep(raw: dict) -> dict:
    return {
        "date": raw.get("calendarDate"),
        "duration_hours": raw.get("sleepTimeSeconds", 0) / 3600,
        "deep_sleep_hours": raw.get("deepSleepSeconds", 0) / 3600,
        "light_sleep_hours": raw.get("lightSleepSeconds", 0) / 3600,
        "rem_sleep_hours": raw.get("remSleepSeconds", 0) / 3600,
        "awake_hours": raw.get("awakeSleepSeconds", 0) / 3600,
        "sleep_score": raw.get("sleepScores", {}).get("overall", {}).get("value"),
        "hrv_status": raw.get("hrvStatus"),
    }
```

## Lambda ETL Functions

### garmin-fetch
```
Location: backend/lambda/fetch/
Purpose: Fetch activities from Garmin Connect API
Trigger: EventBridge (scheduled) or API Gateway (on-demand)
Output: DynamoDB garmin-activities table
```

### garmin-analyzer
```
Location: backend/lambda/analyzer/
Purpose: Compute derived metrics (pace, HR zones, training load)
Trigger: DynamoDB stream on new activity insert
Output: DynamoDB garmin-processed table + S3 reports
```

### Invoke Lambda manually for testing
```bash
# Trigger fetch for last 7 days
aws lambda invoke \
  --function-name garmin-fetch \
  --payload '{"days": 7}' \
  --cli-binary-format raw-in-base64-out \
  output.json

cat output.json
```

## RAG Dataset Management

### Create new RAG batch
```python
import zipfile
import json
from pathlib import Path

def create_rag_batch(data_dir: Path, output_dir: Path, batch_type: str, batch_num: int):
    """Package processed records into a RAG-ready ZIP batch."""
    records = []
    for file in data_dir.glob(f"*{batch_type}*.json"):
        with open(file) as f:
            records.extend(json.load(f))

    batch_file = output_dir / f"{batch_type}-batch-{batch_num:03d}.zip"
    with zipfile.ZipFile(batch_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{batch_type}.json", json.dumps(records, indent=2))

    print(f"Created {batch_file} with {len(records)} records")
```

## Data Validation

Before loading into DynamoDB or dashboard:
```python
def validate_activity(record: dict) -> list[str]:
    """Return list of validation errors (empty = valid)."""
    errors = []
    if not record.get("id"):
        errors.append("Missing activityId")
    if not record.get("date") or len(record["date"]) != 10:
        errors.append(f"Invalid date format: {record.get('date')}")
    if record.get("duration_seconds", 0) <= 0:
        errors.append("Invalid duration")
    return errors
```

## Integration with Workflow

```
New Garmin Export Downloaded
        ↓
/data-pipeline (validate + migrate)
        ↓
/terraform-ops (if DynamoDB schema changed)
        ↓
/streamlit-dash (update dashboard for new data)
        ↓
/test-runner (validate data_loader)
        ↓
/update-docs
```

## Troubleshooting

### Dashboard shows stale data
```bash
# Check which data files are being loaded
grep -n "DATA_DIR" 01-personal/garmin-health/analytics/src/data_loader.py
# Verify the path points to data/raw/ (not aws-ai-agent/docs/)
```

### DynamoDB query returns empty
```bash
# Check table has items
aws dynamodb scan --table-name garmin-activities --select COUNT

# Check Lambda logs for ingestion errors
aws logs tail /aws/lambda/garmin-fetch --since 1h
```

### JSON parse error
```bash
# Validate JSON file
python -c "import json; json.load(open('data/raw/sleep_all_merged.json'))"
```
