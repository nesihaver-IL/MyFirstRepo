#!/usr/bin/env python3
"""
Initialize SQLite database schema and migrate Garmin data from JSON.
Run: python3 setup_database.py [path/to/database.db]
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

# Configuration
DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "garmin.db"
DOCS_DIR = Path(__file__).parent.parent.parent / "aws-ai-agent" / "docs"


def init_schema(db_path):
    """Create SQLite schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Activities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            date TIMESTAMP NOT NULL,
            sport_type TEXT NOT NULL,
            duration_min REAL,
            distance_km REAL,
            distance_m REAL,
            pace_min_per_km REAL,
            avg_hr REAL,
            max_hr REAL,
            calories REAL,
            vo2max REAL,
            aerobic_te REAL,
            avg_swolf REAL,
            pool_length_m REAL,
            active_lengths INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Sleep table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sleep (
            id TEXT PRIMARY KEY,
            date DATE NOT NULL UNIQUE,
            total_sleep_h REAL,
            deep_min REAL,
            light_min REAL,
            rem_min REAL,
            awake_min REAL,
            deep_pct REAL,
            rem_pct REAL,
            light_pct REAL,
            respiration_avg REAL,
            sleep_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Wellness table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wellness (
            id TEXT PRIMARY KEY,
            date DATE NOT NULL UNIQUE,
            steps INTEGER,
            step_goal INTEGER,
            resting_hr REAL,
            min_hr REAL,
            max_hr REAL,
            avg_hr REAL,
            stress_level INTEGER,
            body_battery INTEGER,
            recovery_time_h REAL,
            active_kcal REAL,
            moderate_min REAL,
            vigorous_min REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # VO2Max table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vo2max (
            id TEXT PRIMARY KEY,
            date TIMESTAMP NOT NULL,
            vo2max REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_sport ON activities(sport_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sleep_date ON sleep(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_wellness_date ON wellness(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vo2max_date ON vo2max(date)")

    conn.commit()
    conn.close()
    print(f"[Schema] Created at {db_path}")


def migrate_activities(db_path):
    """Migrate activities from JSON to SQLite."""
    activities_file = DOCS_DIR / "nesihaver@gmail.com_0_summarizedActivities.json"
    if not activities_file.exists():
        print(f"[Warn] Activities file not found: {activities_file}")
        return

    with open(activities_file, encoding="utf-8") as f:
        data = json.load(f)

    activities = data[0].get("summarizedActivitiesExport", [])

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activities")

    runs, swims = 0, 0
    for a in activities:
        sport = a.get("sportType", "")
        ts = a.get("startTimeGmt")
        if not ts:
            continue

        date = datetime.fromtimestamp(ts / 1000)
        dur_min = a.get("duration", 0) / 60000
        dist_cm = a.get("distance", 0)

        if dur_min <= 0 or dist_cm <= 0:
            continue

        activity_id = f"{date.isoformat()}-{sport}"

        if sport == "RUNNING":
            dist_km = dist_cm / 100000
            pace = (dur_min / dist_km) if dist_km > 0 else None

            cursor.execute("""
                INSERT OR REPLACE INTO activities
                (id, date, sport_type, duration_min, distance_km, pace_min_per_km, avg_hr, max_hr, calories, vo2max, aerobic_te)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                activity_id, date, "RUNNING",
                round(dur_min, 1),
                round(dist_km, 2),
                round(pace, 2) if pace else None,
                a.get("avgHr"),
                a.get("maxHr"),
                a.get("calories", 0),
                a.get("vO2MaxValue"),
                a.get("aerobicTrainingEffect"),
            ))
            runs += 1

        elif sport == "SWIMMING":
            dist_m = dist_cm / 100

            cursor.execute("""
                INSERT OR REPLACE INTO activities
                (id, date, sport_type, duration_min, distance_m, avg_hr, max_hr, calories, avg_swolf, pool_length_m, active_lengths, aerobic_te)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                activity_id, date, "SWIMMING",
                round(dur_min, 1),
                round(dist_m, 0),
                a.get("avgHr"),
                a.get("maxHr"),
                a.get("calories", 0),
                a.get("avgSwolf"),
                (a.get("poolLength") or 0) / 100,
                a.get("activeLengths"),
                a.get("aerobicTrainingEffect"),
            ))
            swims += 1

    conn.commit()
    conn.close()
    print(f"[Activities] Imported {runs} running + {swims} swimming sessions")


def migrate_sleep(db_path):
    """Migrate sleep data from JSON to SQLite."""
    sleep_file = DOCS_DIR / "sleep_all_merged.json"
    if not sleep_file.exists():
        print(f"[Warn] Sleep file not found: {sleep_file}")
        return

    with open(sleep_file, encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sleep")

    inserted = 0
    for r in data:
        if r.get("sleepWindowConfirmationType") not in {"ENHANCED_CONFIRMED_FINAL", "ENHANCED_CONFIRMED"}:
            continue

        date = r["calendarDate"]
        deep_min = r.get("deepSleepSeconds", 0) / 60
        light_min = r.get("lightSleepSeconds", 0) / 60
        rem_min = r.get("remSleepSeconds", 0) / 60
        awake_min = r.get("awakeSleepSeconds", 0) / 60
        total_min = deep_min + light_min + rem_min

        cursor.execute("""
            INSERT OR REPLACE INTO sleep
            (id, date, total_sleep_h, deep_min, light_min, rem_min, awake_min, deep_pct, rem_pct, light_pct, respiration_avg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date,
            date,
            round(total_min / 60, 2),
            round(deep_min, 1),
            round(light_min, 1),
            round(rem_min, 1),
            round(awake_min, 1),
            round(100 * deep_min / total_min, 1) if total_min > 0 else 0,
            round(100 * rem_min / total_min, 1) if total_min > 0 else 0,
            round(100 * light_min / total_min, 1) if total_min > 0 else 0,
            r.get("averageRespiration"),
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[Sleep] Imported {inserted} nights")


def migrate_wellness(db_path):
    """Migrate wellness data from JSON to SQLite."""
    wellness_file = DOCS_DIR / "wellness_all_merged.json"
    if not wellness_file.exists():
        print(f"[Warn] Wellness file not found: {wellness_file}")
        return

    with open(wellness_file, encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wellness")

    inserted = 0
    for r in data:
        date = r.get("calendarDate") or r.get("wellnessStartTimeLocal", "")[:10]
        if not date:
            continue

        cursor.execute("""
            INSERT OR REPLACE INTO wellness
            (id, date, steps, step_goal, resting_hr, min_hr, max_hr, avg_hr, stress_level, body_battery, recovery_time_h)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date,
            date,
            r.get("totalSteps", 0),
            r.get("dailyStepGoal", 10000),
            r.get("restingHeartRate"),
            r.get("minHeartRate"),
            r.get("maxHeartRate"),
            r.get("avgHeartRate"),
            r.get("stress", 0),
            r.get("bodyBattery"),
            r.get("remainingBodyBatteryPercentage"),
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[Wellness] Imported {inserted} days")


def migrate_vo2max(db_path):
    """Migrate VO2Max data from JSON to SQLite."""
    vo2_file = DOCS_DIR / "vo2max_metrics_all_merged.json"
    if not vo2_file.exists():
        print(f"[Warn] VO2Max file not found: {vo2_file}")
        return

    with open(vo2_file, encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vo2max")

    inserted = 0
    for r in data:
        ts = r.get("createTimeStamp")
        if not ts:
            continue

        date = datetime.fromtimestamp(ts / 1000)

        cursor.execute("""
            INSERT INTO vo2max (id, date, vo2max)
            VALUES (?, ?, ?)
        """, (
            f"{date.isoformat()}-vo2",
            date,
            r.get("value"),
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[VO2Max] Imported {inserted} readings")


def main():
    """Run all migrations."""
    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("Garmin Health Data Migration to SQLite")
    print("=" * 60 + "\n")

    init_schema(db_path)
    migrate_activities(db_path)
    migrate_sleep(db_path)
    migrate_wellness(db_path)
    migrate_vo2max(db_path)

    print("\n" + "=" * 60)
    print(f"Migration complete! Database: {db_path.resolve()}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
