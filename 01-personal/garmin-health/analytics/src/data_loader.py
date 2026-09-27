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
# Activities CSV (Garmin Connect export)
# ---------------------------------------------------------------------------

_CSV_DIR = Path(__file__).parent.parent.parent / "data" / "exports"


def _parse_duration_to_min(t: str) -> float | None:
    """Convert 'HH:MM:SS' string to total minutes."""
    try:
        parts = str(t).strip().split(":")
        if len(parts) == 3:
            return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
        if len(parts) == 2:
            return int(parts[0]) + int(parts[1]) / 60
    except Exception:
        pass
    return None


def _parse_pace_to_float(p: str) -> float | None:
    """Convert 'M:SS' pace string (min/km) to float minutes."""
    try:
        parts = str(p).strip().split(":")
        if len(parts) == 2:
            return int(parts[0]) + int(parts[1]) / 60
    except Exception:
        pass
    return None


def _clean(val):
    """Replace '--' sentinel with NaN and strip commas from numbers."""
    if isinstance(val, str):
        val = val.strip().strip('"')
        if val in ("--", "", "No", "Yes"):
            return None
        val = val.replace(",", "")
    return val


def load_activities_csv() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Parse All_Activities_Data_*.csv from data/exports/ and return
    (run_df, swim_df, cycle_df). Each row is one activity session.

    CSV quirks handled:
      - Distance has comma-thousands separators ("2,025")
      - Missing values are "--"
      - Pace format differs: "M:SS" for running, km/h for cycling
      - Swimming distance is in meters; running/cycling in km
    """
    # Find the most recently modified CSV in the exports dir
    csvs = sorted(_CSV_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not csvs:
        empty = pd.DataFrame()
        return empty, empty, empty

    path = csvs[0]
    df = pd.read_csv(path, na_values=["--"], keep_default_na=True)

    # Strip commas from all string columns so numeric parse works
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip().str.replace(",", "", regex=False)

    df["date"] = pd.to_datetime(df["Date"], errors="coerce").dt.normalize()
    df = df.dropna(subset=["date"])

    def num(series):
        return pd.to_numeric(series, errors="coerce")

    runs, swims, cycles = [], [], []

    for _, row in df.iterrows():
        sport = str(row.get("Activity Type", "")).strip()
        d = row["date"]

        dur_min = _parse_duration_to_min(row.get("Time", ""))
        calories = num(pd.Series([row.get("Calories")])).iloc[0]
        avg_hr = num(pd.Series([row.get("Avg HR")])).iloc[0]
        max_hr = num(pd.Series([row.get("Max HR")])).iloc[0]
        aero_te = num(pd.Series([row.get("Aerobic TE")])).iloc[0]

        if sport == "Running":
            dist_km = num(pd.Series([row.get("Distance")])).iloc[0]
            pace = _parse_pace_to_float(row.get("Avg Pace", ""))
            best_pace = _parse_pace_to_float(row.get("Best Pace", ""))
            ascent = num(pd.Series([row.get("Total Ascent")])).iloc[0]
            descent = num(pd.Series([row.get("Total Descent")])).iloc[0]
            stride = num(pd.Series([row.get("Avg Stride Length")])).iloc[0]
            steps_raw = str(row.get("Steps", "")).replace(",", "")
            steps = num(pd.Series([steps_raw])).iloc[0]
            runs.append({
                "date": d,
                "duration_min": round(dur_min, 1) if dur_min else None,
                "distance_km": round(float(dist_km), 2) if pd.notna(dist_km) else None,
                "pace_min_per_km": round(pace, 2) if pace else None,
                "best_pace_min_per_km": round(best_pace, 2) if best_pace else None,
                "avg_hr": avg_hr,
                "max_hr": max_hr,
                "calories": calories,
                "aerobic_te": aero_te,
                "total_ascent_m": ascent,
                "total_descent_m": descent,
                "avg_stride_m": stride,
                "steps": steps,
            })

        elif sport == "Pool Swim":
            dist_m = num(pd.Series([row.get("Distance")])).iloc[0]
            swolf = num(pd.Series([row.get("Avg. Swolf")])).iloc[0]
            stroke_rate = num(pd.Series([row.get("Avg Stroke Rate")])).iloc[0]
            total_strokes = num(pd.Series([row.get("Total Strokes")])).iloc[0]
            laps = num(pd.Series([row.get("Number of Laps")])).iloc[0]
            swims.append({
                "date": d,
                "duration_min": round(dur_min, 1) if dur_min else None,
                "distance_m": float(dist_m) if pd.notna(dist_m) else None,
                "avg_hr": avg_hr,
                "max_hr": max_hr,
                "calories": calories,
                "aerobic_te": aero_te,
                "avg_swolf": swolf,
                "stroke_rate": stroke_rate,
                "total_strokes": total_strokes,
                "laps": laps,
            })

        elif sport == "Cycling":
            dist_km = num(pd.Series([row.get("Distance")])).iloc[0]
            # For cycling, "Avg Pace" is speed in km/h
            avg_speed = num(pd.Series([row.get("Avg Pace")])).iloc[0]
            max_speed = num(pd.Series([row.get("Best Pace")])).iloc[0]
            ascent = num(pd.Series([row.get("Total Ascent")])).iloc[0]
            descent = num(pd.Series([row.get("Total Descent")])).iloc[0]
            cycles.append({
                "date": d,
                "duration_min": round(dur_min, 1) if dur_min else None,
                "distance_km": round(float(dist_km), 2) if pd.notna(dist_km) else None,
                "avg_speed_kmh": avg_speed,
                "max_speed_kmh": max_speed,
                "avg_hr": avg_hr,
                "max_hr": max_hr,
                "calories": calories,
                "aerobic_te": aero_te,
                "total_ascent_m": ascent,
                "total_descent_m": descent,
            })

    run_df = pd.DataFrame(runs).sort_values("date").reset_index(drop=True) if runs else pd.DataFrame()
    swim_df = pd.DataFrame(swims).sort_values("date").reset_index(drop=True) if swims else pd.DataFrame()
    cycle_df = pd.DataFrame(cycles).sort_values("date").reset_index(drop=True) if cycles else pd.DataFrame()
    return run_df, swim_df, cycle_df


# ---------------------------------------------------------------------------
# Helper: filter by date range
# ---------------------------------------------------------------------------

def filter_dates(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Filter a DataFrame with a 'date' column to the given date range."""
    if df.empty:
        return df
    return df[(df["date"] >= start) & (df["date"] <= end)].copy()
