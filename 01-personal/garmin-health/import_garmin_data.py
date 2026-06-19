#!/usr/bin/env python3
import json
import sqlite3
import glob
from pathlib import Path

DATA_DIR = Path("data/Garmin_full_Data_020626/DI_CONNECT")
OUTPUT_DIR = Path("data")
GARMIN_DB = OUTPUT_DIR / "garmin.db"
ACTIVITIES_DB = OUTPUT_DIR / "garmin_activities.db"

def seconds_to_time(seconds):
    if not seconds:
        return "00:00:00"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def import_sleep_data():
    conn = sqlite3.connect(GARMIN_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sleep (
            day DATE PRIMARY KEY,
            start DATETIME,
            end DATETIME,
            total_sleep TIME,
            deep_sleep TIME,
            light_sleep TIME,
            rem_sleep TIME,
            awake TIME,
            avg_spo2 FLOAT,
            avg_rr FLOAT,
            score INTEGER
        )
    """)
    conn.execute("DELETE FROM sleep")

    sleep_files = sorted(glob.glob(str(DATA_DIR / "DI-Connect-Wellness/*sleepData.json")))
    print(f"Found {len(sleep_files)} sleep data files")

    inserted = 0
    for sleep_file in sleep_files:
        try:
            with open(sleep_file) as f:
                sleep_list = json.load(f)
            for entry in sleep_list:
                day = entry.get("calendarDate")
                if not day:
                    continue
                start = entry.get("sleepStartTimestampGMT")
                end = entry.get("sleepEndTimestampGMT")
                total_sleep = seconds_to_time(entry.get("totalSleepSeconds", 0))
                deep_sleep = seconds_to_time(entry.get("deepSleepSeconds", 0))
                light_sleep = seconds_to_time(entry.get("lightSleepSeconds", 0))
                rem_sleep = seconds_to_time(entry.get("remSleepSeconds", 0))
                awake = seconds_to_time(entry.get("awakeSleepSeconds", 0))
                avg_rr = entry.get("averageRespiration", 0)
                avg_spo2 = entry.get("averageSpO2", 0)
                score = entry.get("sleepScores", {}).get("overall", 0) if isinstance(entry.get("sleepScores"), dict) else 0

                conn.execute("""
                    INSERT OR REPLACE INTO sleep
                    (day, start, end, total_sleep, deep_sleep, light_sleep, rem_sleep, awake, avg_spo2, avg_rr, score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (day, start, end, total_sleep, deep_sleep, light_sleep, rem_sleep, awake, avg_spo2, avg_rr, score))
                inserted += 1
        except Exception as e:
            print(f"Sleep error: {e}")

    conn.commit()
    print(f"Imported {inserted} sleep records")
    conn.close()

def import_activities_data():
    conn = sqlite3.connect(ACTIVITIES_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            activityId INTEGER PRIMARY KEY,
            name TEXT,
            activityType TEXT,
            beginTimestamp DATETIME,
            distance FLOAT,
            calories FLOAT,
            avgHeartRate FLOAT,
            maxHeartRate FLOAT,
            duration FLOAT
        )
    """)
    conn.execute("DELETE FROM activities")

    activities_file = DATA_DIR / "DI-Connect-Fitness/nesihaver@gmail.com_0_summarizedActivities.json"
    if not activities_file.exists():
        print(f"Activities file not found")
        conn.close()
        return

    try:
        with open(activities_file) as f:
            data = json.load(f)
        
        activities_list = data[0].get("summarizedActivitiesExport", []) if isinstance(data, list) and len(data) > 0 else []
        print(f"Found {len(activities_list)} activities")

        inserted = 0
        for act in activities_list:
            if not isinstance(act, dict):
                continue
            try:
                activity_type = act.get("activityType", {})
                if isinstance(activity_type, dict):
                    activity_type_key = activity_type.get("typeKey", "")
                else:
                    activity_type_key = str(activity_type)
                
                conn.execute("""
                    INSERT INTO activities
                    (activityId, name, activityType, beginTimestamp, distance, calories, avgHeartRate, maxHeartRate, duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    act.get("activityId"),
                    act.get("name"),
                    activity_type_key,
                    act.get("beginTimestamp"),
                    act.get("distance"),
                    act.get("calories"),
                    act.get("averageHeartRate"),
                    act.get("maxHeartRate"),
                    act.get("duration")
                ))
                inserted += 1
            except Exception as e:
                print(f"Activity error: {e}")
        
        conn.commit()
        print(f"Imported {inserted} activities")
    except Exception as e:
        print(f"Error: {e}")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Garmin GDPR Data Import")
    print("=" * 60)
    print(f"\nImporting sleep data...")
    import_sleep_data()
    print(f"\nImporting activities data...")
    import_activities_data()
    print("\n" + "=" * 60)
    print("Import complete!")
    print("=" * 60)
