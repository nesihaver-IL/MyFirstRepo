"""
Data loader for Garmin Health Analytics Dashboard.

All source JSON files live in ../../../aws-ai-agent/docs/ relative to this file (01-personal/aws-ai-agent/docs/).

Unit notes (from Garmin internal format):
  - distance: centimeters  → divide by 100 for meters, by 100000 for km
  - duration: milliseconds → divide by 60000 for minutes
  - startTimeGmt: ms epoch → pd.to_datetime(x, unit='ms')
"""

import json
import os
import pandas as pd
from pathlib import Path

# Absolute path to the data folder
_DOCS_DIR = Path(__file__).parent.parent.parent.parent / "aws-ai-agent" / "docs"


def _docs(filename: str) -> Path:
    return _DOCS_DIR / filename


# ---------------------------------------------------------------------------
# Activities (Running + Swimming)
# ---------------------------------------------------------------------------

def load_activities() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parse summarizedActivities.json and return (run_df, swim_df).
    Each row is one activity session.
    """
    path = _docs("nesihaver@gmail.com_0_summarizedActivities.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    acts = raw[0]["summarizedActivitiesExport"]

    runs, swims = [], []
    for a in acts:
        sport = a.get("sportType", "")
        ts = a.get("startTimeGmt")
        if not ts:
            continue
        date = pd.to_datetime(ts, unit="ms").normalize()

        dur_min = a.get("duration", 0) / 60000
        dist_cm = a.get("distance", 0)
        avg_hr = a.get("avgHr")
        max_hr = a.get("maxHr")
        calories = a.get("calories", 0)
        vo2max = a.get("vO2MaxValue")

        if sport == "RUNNING":
            dist_km = dist_cm / 100000
            pace = dur_min / dist_km if dist_km > 0 else None
            cadence_spm = (a.get("avgRunCadence") or 0) * 2  # double cadence
            runs.append({
                "date": date,
                "duration_min": round(dur_min, 1),
                "distance_km": round(dist_km, 2),
                "pace_min_per_km": round(pace, 2) if pace else None,
                "avg_hr": avg_hr,
                "max_hr": max_hr,
                "cadence_spm": cadence_spm if cadence_spm > 0 else None,
                "calories": round(calories, 0),
                "vo2max": vo2max,
                "aerobic_te": a.get("aerobicTrainingEffect"),
            })

        elif sport == "SWIMMING":
            dist_m = dist_cm / 100
            swims.append({
                "date": date,
                "duration_min": round(dur_min, 1),
                "distance_m": round(dist_m, 0),
                "avg_hr": avg_hr,
                "max_hr": max_hr,
                "calories": round(calories, 0),
                "avg_swolf": a.get("avgSwolf"),
                "pool_length_m": (a.get("poolLength") or 0) / 100,
                "active_lengths": a.get("activeLengths"),
                "aerobic_te": a.get("aerobicTrainingEffect"),
            })

    run_df = pd.DataFrame(runs).sort_values("date").reset_index(drop=True)
    swim_df = pd.DataFrame(swims).sort_values("date").reset_index(drop=True)
    return run_df, swim_df


# ---------------------------------------------------------------------------
# Sleep
# ---------------------------------------------------------------------------

def load_sleep() -> pd.DataFrame:
    """
    Load sleep_all_merged.json.
    Only includes nights with ENHANCED_CONFIRMED_FINAL stage data.
    """
    path = _docs("sleep_all_merged.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    VALID_TYPES = {"ENHANCED_CONFIRMED_FINAL", "ENHANCED_CONFIRMED"}
    for r in raw:
        if r.get("sleepWindowConfirmationType") not in VALID_TYPES:
            continue
        date = pd.to_datetime(r["calendarDate"])
        deep_min = r.get("deepSleepSeconds", 0) / 60
        light_min = r.get("lightSleepSeconds", 0) / 60
        rem_min = r.get("remSleepSeconds", 0) / 60
        awake_min = r.get("awakeSleepSeconds", 0) / 60
        total_min = deep_min + light_min + rem_min
        rows.append({
            "date": date,
            "total_sleep_h": round(total_min / 60, 2),
            "deep_min": round(deep_min, 1),
            "light_min": round(light_min, 1),
            "rem_min": round(rem_min, 1),
            "awake_min": round(awake_min, 1),
            "deep_pct": round(100 * deep_min / total_min, 1) if total_min > 0 else 0,
            "rem_pct": round(100 * rem_min / total_min, 1) if total_min > 0 else 0,
            "respiration_avg": r.get("averageRespiration"),
        })

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Wellness (daily snapshot)
# ---------------------------------------------------------------------------

def load_wellness() -> pd.DataFrame:
    """Load wellness_all_merged.json — one row per day."""
    path = _docs("wellness_all_merged.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    for r in raw:
        date = pd.to_datetime(r.get("calendarDate") or r.get("wellnessStartTimeLocal", "")[:10])
        rows.append({
            "date": date,
            "steps": r.get("totalSteps", 0),
            "step_goal": r.get("dailyStepGoal", 10000),
            "resting_hr": r.get("restingHeartRate"),
            "min_hr": r.get("minHeartRate"),
            "max_hr": r.get("maxHeartRate"),
            "active_kcal": r.get("activeKilocalories", 0),
            "total_kcal": r.get("totalKilocalories", 0),
            "moderate_min": r.get("moderateIntensityMinutes", 0),
            "vigorous_min": r.get("vigorousIntensityMinutes", 0),
            "highly_active_sec": r.get("highlyActiveSeconds", 0),
        })

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    df = df.drop_duplicates(subset="date", keep="last")
    return df


# ---------------------------------------------------------------------------
# VO2Max
# ---------------------------------------------------------------------------

def load_vo2max() -> pd.DataFrame:
    """Load vo2max_metrics_all_merged.json."""
    path = _docs("vo2max_metrics_all_merged.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    for r in raw:
        rows.append({
            "date": pd.to_datetime(r["calendarDate"]),
            "vo2max": r.get("vo2MaxValue"),
            "fitness_age": int(r["fitnessAge"]) if r.get("fitnessAge") else None,
            "max_met": r.get("maxMet"),
        })

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    df = df.drop_duplicates(subset="date", keep="last")
    return df


# ---------------------------------------------------------------------------
# Race Predictions
# ---------------------------------------------------------------------------

def _sec_to_hms(seconds: float) -> str:
    if pd.isna(seconds):
        return "—"
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h > 0:
        return f"{h}:{m:02d}:{sec:02d}"
    return f"{m}:{sec:02d}"


def load_race_predictions() -> pd.DataFrame:
    """Load race_predictions_all_merged.json."""
    path = _docs("race_predictions_all_merged.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    for r in raw:
        rows.append({
            "date": pd.to_datetime(r["calendarDate"]),
            "5k_sec": r.get("raceTime5K"),
            "10k_sec": r.get("raceTime10K"),
            "half_sec": r.get("raceTimeHalf"),
            "marathon_sec": r.get("raceTimeMarathon"),
        })

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    df = df.drop_duplicates(subset="date", keep="last")
    # Add formatted time columns
    for col, label in [("5k_sec", "5k"), ("10k_sec", "10k"), ("half_sec", "half"), ("marathon_sec", "marathon")]:
        df[f"{label}_fmt"] = df[col].apply(_sec_to_hms)
    return df


# ---------------------------------------------------------------------------
# Training History
# ---------------------------------------------------------------------------

def load_training_history() -> pd.DataFrame:
    """Load training_history_all_merged.json."""
    path = _docs("training_history_all_merged.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    for r in raw:
        rows.append({
            "date": pd.to_datetime(r["calendarDate"]),
            "sport": r.get("sport", ""),
            "weekly_load": r.get("weeklyTrainingLoadSum", 0),
            "load_min": r.get("loadTunnelMin"),
            "load_max": r.get("loadTunnelMax"),
            "training_status": r.get("trainingStatus", ""),
            "fitness_trend": r.get("fitnessLevelTrend", ""),
            "load_trend": r.get("loadLevelTrend", ""),
        })

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Helper: filter by date range
# ---------------------------------------------------------------------------

def filter_dates(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Filter a DataFrame with a 'date' column to the given date range."""
    if df.empty:
        return df
    return df[(df["date"] >= start) & (df["date"] <= end)].copy()
