#!/usr/bin/env python3
"""
Garmin Data Processor for RAG Training
Consolidates and transforms Garmin export data into RAG-optimized documents.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# Paths
BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"


def ensure_dirs():
    """Create output directories if they don't exist."""
    PROCESSED_DIR.mkdir(exist_ok=True)
    (PROCESSED_DIR / "documents").mkdir(exist_ok=True)


def load_json(filepath: Path) -> Any:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Any, filepath: Path):
    """Save data to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def format_duration(ms: float) -> str:
    """Convert milliseconds to human-readable duration."""
    seconds = int(ms / 1000)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def format_distance(meters: float) -> str:
    """Convert meters to km or m."""
    if meters >= 1000:
        return f"{meters/1000:.2f} km"
    return f"{meters:.0f} m"


def format_pace(speed_mps: float) -> str:
    """Convert m/s to min/km pace."""
    if speed_mps <= 0:
        return "N/A"
    pace_seconds_per_km = 1000 / speed_mps
    minutes = int(pace_seconds_per_km / 60)
    seconds = int(pace_seconds_per_km % 60)
    return f"{minutes}:{seconds:02d} /km"


# =============================================================================
# CONSOLIDATION FUNCTIONS
# =============================================================================

def consolidate_activities():
    """Consolidate activities into single file."""
    print("📊 Consolidating activities...")

    activities_file = RAW_DIR / "batch1" / "nesihaver@gmail.com_0_summarizedActivities.json"
    data = load_json(activities_file)
    activities = data[0]['summarizedActivitiesExport']

    # Sort by date (most recent first)
    activities.sort(key=lambda x: x.get('startTimeGmt', 0), reverse=True)

    save_json(activities, PROCESSED_DIR / "activities_all.json")
    print(f"   ✓ Saved {len(activities)} activities")

    return activities


def consolidate_wellness():
    """Consolidate all UDS wellness files."""
    print("📊 Consolidating daily wellness...")

    all_wellness = []
    batch2_dir = RAW_DIR / "batch2"

    for f in sorted(batch2_dir.glob("UDSFile_*.json")):
        data = load_json(f)
        all_wellness.extend(data)

    # Sort by date
    all_wellness.sort(key=lambda x: x.get('calendarDate', ''))

    # Remove duplicates by date
    seen = set()
    unique = []
    for w in all_wellness:
        date = w.get('calendarDate')
        if date and date not in seen:
            seen.add(date)
            unique.append(w)

    save_json(unique, PROCESSED_DIR / "wellness_daily_all.json")
    print(f"   ✓ Saved {len(unique)} daily wellness records")

    return unique


def consolidate_sleep():
    """Consolidate all sleep data files."""
    print("📊 Consolidating sleep data...")

    all_sleep = []
    batch2_dir = RAW_DIR / "batch2"

    for f in sorted(batch2_dir.glob("*_sleepData.json")):
        data = load_json(f)
        all_sleep.extend(data)

    # Sort by date
    all_sleep.sort(key=lambda x: x.get('calendarDate', ''))

    # Remove duplicates
    seen = set()
    unique = []
    for s in all_sleep:
        date = s.get('calendarDate')
        if date and date not in seen:
            seen.add(date)
            unique.append(s)

    save_json(unique, PROCESSED_DIR / "sleep_all.json")
    print(f"   ✓ Saved {len(unique)} sleep records")

    return unique


def consolidate_training():
    """Consolidate training history files."""
    print("📊 Consolidating training history...")

    all_training = []
    batch3_dir = RAW_DIR / "batch3"

    for f in sorted(batch3_dir.glob("TrainingHistory_*.json")):
        data = load_json(f)
        all_training.extend(data)

    all_training.sort(key=lambda x: x.get('calendarDate', ''))

    seen = set()
    unique = []
    for t in all_training:
        date = t.get('calendarDate')
        if date and date not in seen:
            seen.add(date)
            unique.append(t)

    save_json(unique, PROCESSED_DIR / "training_history_all.json")
    print(f"   ✓ Saved {len(unique)} training records")

    return unique


def consolidate_metrics():
    """Consolidate VO2 max and fitness metrics."""
    print("📊 Consolidating fitness metrics...")

    all_metrics = []
    batch3_dir = RAW_DIR / "batch3"

    for f in sorted(batch3_dir.glob("MetricsMaxMetData_*.json")):
        data = load_json(f)
        all_metrics.extend(data)

    all_metrics.sort(key=lambda x: x.get('calendarDate', ''))

    save_json(all_metrics, PROCESSED_DIR / "metrics_vo2max_all.json")
    print(f"   ✓ Saved {len(all_metrics)} fitness metric records")

    return all_metrics


def copy_personal_records():
    """Copy personal records file."""
    print("📊 Copying personal records...")

    pr_file = RAW_DIR / "batch1" / "nesihaver@gmail.com_personalRecord.json"
    data = load_json(pr_file)

    save_json(data, PROCESSED_DIR / "personal_records.json")
    print(f"   ✓ Saved personal records")

    return data


# =============================================================================
# RAG DOCUMENT GENERATION
# =============================================================================

def generate_activity_documents(activities: list):
    """Generate natural language documents for activities."""
    print("📝 Generating activity documents...")

    documents = []

    for activity in activities:
        try:
            # Parse timestamp
            ts = activity.get('startTimeLocal', 0)
            if ts:
                date = datetime.fromtimestamp(ts / 1000)
                date_str = date.strftime("%B %d, %Y at %H:%M")
            else:
                date_str = "Unknown date"

            activity_type = activity.get('activityType', 'unknown').replace('_', ' ').title()
            name = activity.get('name', activity_type)

            # Build document
            doc_parts = [f"Activity: {name}"]
            doc_parts.append(f"Date: {date_str}")
            doc_parts.append(f"Type: {activity_type}")

            if activity.get('duration'):
                doc_parts.append(f"Duration: {format_duration(activity['duration'])}")

            if activity.get('distance'):
                doc_parts.append(f"Distance: {format_distance(activity['distance'])}")

            if activity.get('avgSpeed'):
                doc_parts.append(f"Pace: {format_pace(activity['avgSpeed'])}")

            if activity.get('avgHr'):
                hr_info = f"Heart Rate: Avg {activity['avgHr']:.0f}"
                if activity.get('maxHr'):
                    hr_info += f", Max {activity['maxHr']:.0f}"
                doc_parts.append(hr_info + " bpm")

            if activity.get('calories'):
                doc_parts.append(f"Calories: {activity['calories']:.0f} kcal")

            if activity.get('elevationGain'):
                doc_parts.append(f"Elevation Gain: {activity['elevationGain']:.0f} m")

            if activity.get('vO2MaxValue'):
                doc_parts.append(f"VO2 Max: {activity['vO2MaxValue']}")

            if activity.get('aerobicTrainingEffect'):
                doc_parts.append(f"Aerobic Training Effect: {activity['aerobicTrainingEffect']:.1f}")

            doc = {
                "id": f"activity_{activity.get('activityId', 'unknown')}",
                "type": "activity",
                "date": date_str,
                "activity_type": activity_type,
                "content": "\n".join(doc_parts),
                "metadata": {
                    "activity_id": activity.get('activityId'),
                    "activity_type": activity.get('activityType'),
                    "duration_ms": activity.get('duration'),
                    "distance_m": activity.get('distance'),
                    "calories": activity.get('calories')
                }
            }
            documents.append(doc)

        except Exception as e:
            print(f"   ⚠ Error processing activity: {e}")

    save_json(documents, PROCESSED_DIR / "documents" / "activities_docs.json")
    print(f"   ✓ Generated {len(documents)} activity documents")

    return documents


def generate_wellness_documents(wellness: list):
    """Generate natural language documents for daily wellness."""
    print("📝 Generating wellness documents...")

    documents = []

    for day in wellness:
        try:
            date = day.get('calendarDate', 'Unknown')

            doc_parts = [f"Daily Wellness Summary: {date}"]

            # Steps
            steps = day.get('totalSteps', 0)
            goal = day.get('dailyStepGoal', 0)
            goal_met = "✓" if steps >= goal else "✗"
            doc_parts.append(f"Steps: {steps:,} (Goal: {goal:,}) {goal_met}")

            # Calories
            total_cal = day.get('totalKilocalories', 0)
            active_cal = day.get('activeKilocalories', 0)
            doc_parts.append(f"Calories: {total_cal:,.0f} kcal (Active: {active_cal:,.0f})")

            # Distance
            if day.get('totalDistanceMeters'):
                doc_parts.append(f"Distance: {format_distance(day['totalDistanceMeters'])}")

            # Heart Rate
            if day.get('restingHeartRate'):
                hr_parts = [f"Resting HR: {day['restingHeartRate']} bpm"]
                if day.get('minHeartRate'):
                    hr_parts.append(f"Min: {day['minHeartRate']}")
                if day.get('maxHeartRate'):
                    hr_parts.append(f"Max: {day['maxHeartRate']}")
                doc_parts.append(", ".join(hr_parts))

            # Stress
            stress = day.get('allDayStress', {})
            if stress:
                for agg in stress.get('aggregatorList', []):
                    if agg.get('type') == 'TOTAL':
                        doc_parts.append(f"Stress: Avg {agg.get('averageStressLevel', 'N/A')}, Max {agg.get('maxStressLevel', 'N/A')}")
                        break

            # Intensity Minutes
            mod_min = day.get('moderateIntensityMinutes', 0)
            vig_min = day.get('vigorousIntensityMinutes', 0)
            if mod_min or vig_min:
                doc_parts.append(f"Intensity Minutes: {mod_min} moderate, {vig_min} vigorous")

            doc = {
                "id": f"wellness_{date}",
                "type": "daily_wellness",
                "date": date,
                "content": "\n".join(doc_parts),
                "metadata": {
                    "steps": steps,
                    "calories": total_cal,
                    "resting_hr": day.get('restingHeartRate')
                }
            }
            documents.append(doc)

        except Exception as e:
            print(f"   ⚠ Error processing wellness: {e}")

    save_json(documents, PROCESSED_DIR / "documents" / "wellness_docs.json")
    print(f"   ✓ Generated {len(documents)} wellness documents")

    return documents


def generate_sleep_documents(sleep_data: list):
    """Generate natural language documents for sleep."""
    print("📝 Generating sleep documents...")

    documents = []

    for sleep in sleep_data:
        try:
            date = sleep.get('calendarDate', 'Unknown')

            deep = sleep.get('deepSleepSeconds', 0) / 3600
            light = sleep.get('lightSleepSeconds', 0) / 3600
            rem = sleep.get('remSleepSeconds', 0) / 3600
            awake = sleep.get('awakeSleepSeconds', 0) / 60
            total = deep + light + rem

            doc_parts = [f"Sleep Summary: {date}"]
            doc_parts.append(f"Total Sleep: {total:.1f} hours")
            doc_parts.append(f"Deep Sleep: {deep:.1f} hours ({deep/total*100:.0f}%)" if total > 0 else "Deep Sleep: N/A")
            doc_parts.append(f"Light Sleep: {light:.1f} hours ({light/total*100:.0f}%)" if total > 0 else "Light Sleep: N/A")
            doc_parts.append(f"REM Sleep: {rem:.1f} hours ({rem/total*100:.0f}%)" if total > 0 else "REM Sleep: N/A")
            doc_parts.append(f"Awake Time: {awake:.0f} minutes")

            if sleep.get('averageRespiration'):
                doc_parts.append(f"Respiration: Avg {sleep['averageRespiration']:.0f} breaths/min")

            doc = {
                "id": f"sleep_{date}",
                "type": "sleep",
                "date": date,
                "content": "\n".join(doc_parts),
                "metadata": {
                    "total_hours": round(total, 2),
                    "deep_hours": round(deep, 2),
                    "rem_hours": round(rem, 2)
                }
            }
            documents.append(doc)

        except Exception as e:
            print(f"   ⚠ Error processing sleep: {e}")

    save_json(documents, PROCESSED_DIR / "documents" / "sleep_docs.json")
    print(f"   ✓ Generated {len(documents)} sleep documents")

    return documents


def generate_summary_stats(activities, wellness, sleep_data):
    """Generate overall summary statistics document."""
    print("📝 Generating summary statistics...")

    # Activity stats by type
    activity_stats = {}
    for a in activities:
        atype = a.get('activityType', 'unknown')
        if atype not in activity_stats:
            activity_stats[atype] = {'count': 0, 'total_distance': 0, 'total_duration': 0}
        activity_stats[atype]['count'] += 1
        activity_stats[atype]['total_distance'] += a.get('distance', 0)
        activity_stats[atype]['total_duration'] += a.get('duration', 0)

    # Average wellness metrics
    avg_steps = sum(w.get('totalSteps', 0) for w in wellness) / len(wellness) if wellness else 0
    avg_rhr = sum(w.get('restingHeartRate', 0) for w in wellness if w.get('restingHeartRate')) / len([w for w in wellness if w.get('restingHeartRate')]) if wellness else 0

    # Average sleep
    avg_sleep = sum((s.get('deepSleepSeconds', 0) + s.get('lightSleepSeconds', 0) + s.get('remSleepSeconds', 0)) / 3600 for s in sleep_data) / len(sleep_data) if sleep_data else 0

    summary = {
        "overview": {
            "total_activities": len(activities),
            "total_wellness_days": len(wellness),
            "total_sleep_records": len(sleep_data),
            "date_range": {
                "earliest": min(w.get('calendarDate', '') for w in wellness) if wellness else "N/A",
                "latest": max(w.get('calendarDate', '') for w in wellness) if wellness else "N/A"
            }
        },
        "activity_summary": activity_stats,
        "wellness_averages": {
            "avg_daily_steps": round(avg_steps),
            "avg_resting_hr": round(avg_rhr, 1)
        },
        "sleep_averages": {
            "avg_total_sleep_hours": round(avg_sleep, 2)
        }
    }

    save_json(summary, PROCESSED_DIR / "summary_stats.json")
    print(f"   ✓ Generated summary statistics")

    return summary


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("🏃 Garmin Data Processor for RAG Training")
    print("=" * 60)
    print()

    ensure_dirs()

    # Phase 1: Consolidate raw data
    print("Phase 1: Consolidating raw data files...")
    print("-" * 40)
    activities = consolidate_activities()
    wellness = consolidate_wellness()
    sleep_data = consolidate_sleep()
    training = consolidate_training()
    metrics = consolidate_metrics()
    personal_records = copy_personal_records()
    print()

    # Phase 2: Generate RAG documents
    print("Phase 2: Generating RAG-optimized documents...")
    print("-" * 40)
    generate_activity_documents(activities)
    generate_wellness_documents(wellness)
    generate_sleep_documents(sleep_data)
    print()

    # Phase 3: Generate summaries
    print("Phase 3: Generating summary statistics...")
    print("-" * 40)
    generate_summary_stats(activities, wellness, sleep_data)
    print()

    print("=" * 60)
    print("✅ Processing complete!")
    print()
    print("Output files:")
    print(f"  📁 {PROCESSED_DIR}/")
    print("     ├── activities_all.json")
    print("     ├── wellness_daily_all.json")
    print("     ├── sleep_all.json")
    print("     ├── training_history_all.json")
    print("     ├── metrics_vo2max_all.json")
    print("     ├── personal_records.json")
    print("     ├── summary_stats.json")
    print("     └── documents/")
    print("         ├── activities_docs.json")
    print("         ├── wellness_docs.json")
    print("         └── sleep_docs.json")
    print()


if __name__ == "__main__":
    main()
