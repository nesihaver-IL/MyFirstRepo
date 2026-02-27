"""
Derived metrics computed from the normalized DataFrames.
All functions accept DataFrames produced by data_loader.py and return
new DataFrames or scalar values ready for chart rendering.
"""

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# HR Zone helpers (for 47-yr-old, Max HR ~173 bpm)
# ---------------------------------------------------------------------------

ZONES = {
    "Z1 Recovery":    (0,   120),
    "Z2 Aerobic":     (120, 140),
    "Z3 Threshold":   (140, 155),
    "Z4 Anaerobic":   (155, 165),
    "Z5 Max Effort":  (165, 999),
}


def assign_hr_zone(hr: float | None) -> str:
    if hr is None or pd.isna(hr):
        return "Unknown"
    for name, (lo, hi) in ZONES.items():
        if lo <= hr < hi:
            return name
    return "Z5 Max Effort"


# ---------------------------------------------------------------------------
# Running metrics
# ---------------------------------------------------------------------------

def running_weekly(run_df: pd.DataFrame) -> pd.DataFrame:
    """Weekly aggregation: total km, sessions, avg pace, avg HR."""
    if run_df.empty:
        return pd.DataFrame()
    df = run_df.copy()
    df["week"] = df["date"].dt.to_period("W").dt.start_time
    agg = df.groupby("week").agg(
        sessions=("distance_km", "count"),
        total_km=("distance_km", "sum"),
        avg_pace=("pace_min_per_km", "mean"),
        avg_hr=("avg_hr", "mean"),
        avg_cadence=("cadence_spm", "mean"),
    ).reset_index()
    agg["total_km"] = agg["total_km"].round(1)
    agg["avg_pace"] = agg["avg_pace"].round(2)
    agg["avg_hr"] = agg["avg_hr"].round(1)
    agg["avg_cadence"] = agg["avg_cadence"].round(0)
    return agg


def running_with_zones(run_df: pd.DataFrame) -> pd.DataFrame:
    """Add HR zone column to running sessions."""
    df = run_df.copy()
    df["hr_zone"] = df["avg_hr"].apply(assign_hr_zone)
    return df


# ---------------------------------------------------------------------------
# Swimming metrics
# ---------------------------------------------------------------------------

def swimming_weekly(swim_df: pd.DataFrame) -> pd.DataFrame:
    """Weekly aggregation: total distance, sessions, avg duration, avg HR."""
    if swim_df.empty:
        return pd.DataFrame()
    df = swim_df.copy()
    df["week"] = df["date"].dt.to_period("W").dt.start_time
    agg = df.groupby("week").agg(
        sessions=("distance_m", "count"),
        total_m=("distance_m", "sum"),
        avg_duration_min=("duration_min", "mean"),
        avg_hr=("avg_hr", "mean"),
        avg_swolf=("avg_swolf", "mean"),
    ).reset_index()
    agg["total_m"] = agg["total_m"].round(0)
    agg["avg_duration_min"] = agg["avg_duration_min"].round(1)
    agg["avg_hr"] = agg["avg_hr"].round(1)
    agg["avg_swolf"] = agg["avg_swolf"].round(1)
    return agg


# ---------------------------------------------------------------------------
# Sleep metrics
# ---------------------------------------------------------------------------

def sleep_weekly_score(sleep_df: pd.DataFrame) -> pd.DataFrame:
    """
    Weekly sleep quality score (weighted: deep×3 + rem×2 + light×1)
    normalized to 0-100 scale.
    """
    if sleep_df.empty:
        return pd.DataFrame()
    df = sleep_df.copy()
    df["week"] = df["date"].dt.to_period("W").dt.start_time
    df["raw_score"] = df["deep_min"] * 3 + df["rem_min"] * 2 + df["light_min"] * 1

    agg = df.groupby("week").agg(
        nights=("total_sleep_h", "count"),
        avg_total_h=("total_sleep_h", "mean"),
        avg_deep_pct=("deep_pct", "mean"),
        avg_rem_pct=("rem_pct", "mean"),
        avg_respiration=("respiration_avg", "mean"),
        raw_score=("raw_score", "mean"),
        nights_under_7h=("total_sleep_h", lambda x: (x < 7).sum()),
    ).reset_index()

    # Normalize score to 0-100 (max raw ≈ 60min deep×3 + 90min rem×2 + 300min light×1 = 660)
    max_raw = 660
    agg["sleep_score"] = (agg["raw_score"] / max_raw * 100).clip(0, 100).round(1)
    agg["avg_total_h"] = agg["avg_total_h"].round(2)
    agg["avg_deep_pct"] = agg["avg_deep_pct"].round(1)
    agg["avg_rem_pct"] = agg["avg_rem_pct"].round(1)
    return agg


# ---------------------------------------------------------------------------
# ACWR — Acute-to-Chronic Workload Ratio
# ---------------------------------------------------------------------------

def compute_acwr(train_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute ACWR from training_history data.
    Acute load = 7-day rolling sum, Chronic load = 28-day rolling avg.
    Returns daily ACWR with risk zone labels.
    """
    if train_df.empty:
        return pd.DataFrame()

    # Aggregate across sports to get total daily load
    daily = (
        train_df.groupby("date")["weekly_load"]
        .max()  # already weekly, take latest reading per day
        .reset_index()
        .sort_values("date")
    )
    daily = daily.set_index("date").reindex(
        pd.date_range(daily["date"].min(), daily["date"].max(), freq="D")
    ).fillna(0).reset_index()
    daily.columns = ["date", "weekly_load"]

    # Use weekly_load as a proxy for daily load (divide by 7)
    daily["daily_load"] = daily["weekly_load"] / 7
    daily["acute_7d"] = daily["daily_load"].rolling(7, min_periods=1).sum()
    daily["chronic_28d"] = daily["daily_load"].rolling(28, min_periods=7).mean() * 7

    daily["acwr"] = (daily["acute_7d"] / daily["chronic_28d"].replace(0, np.nan)).round(2)
    daily["risk_zone"] = daily["acwr"].apply(_acwr_zone)
    return daily.dropna(subset=["acwr"])


def _acwr_zone(ratio: float) -> str:
    if pd.isna(ratio):
        return "Unknown"
    if ratio < 0.8:
        return "Undertraining"
    if ratio <= 1.3:
        return "Safe"
    if ratio <= 1.5:
        return "Caution"
    return "Injury Risk"


# ---------------------------------------------------------------------------
# Wellness weekly
# ---------------------------------------------------------------------------

def wellness_weekly(well_df: pd.DataFrame) -> pd.DataFrame:
    """Weekly aggregation of wellness metrics."""
    if well_df.empty:
        return pd.DataFrame()
    df = well_df.copy()
    df["week"] = df["date"].dt.to_period("W").dt.start_time
    agg = df.groupby("week").agg(
        avg_steps=("steps", "mean"),
        avg_resting_hr=("resting_hr", "mean"),
        total_active_kcal=("active_kcal", "sum"),
        total_moderate_min=("moderate_min", "sum"),
        total_vigorous_min=("vigorous_min", "sum"),
    ).reset_index()
    agg["avg_steps"] = agg["avg_steps"].round(0)
    agg["avg_resting_hr"] = agg["avg_resting_hr"].round(1)
    # WHO target: 150 min moderate OR 75 min vigorous per week
    agg["intensity_goal_pct"] = (
        (agg["total_moderate_min"] + agg["total_vigorous_min"] * 2) / 150 * 100
    ).clip(0, 200).round(1)
    return agg


# ---------------------------------------------------------------------------
# Cross-pillar: Sleep → Next-day training load
# ---------------------------------------------------------------------------

def sleep_vs_next_load(sleep_df: pd.DataFrame, train_df: pd.DataFrame) -> pd.DataFrame:
    """
    Join sleep quality with next-day training load for correlation analysis.
    """
    if sleep_df.empty or train_df.empty:
        return pd.DataFrame()

    sleep = sleep_df[["date", "total_sleep_h", "deep_pct", "rem_pct"]].copy()
    sleep["next_date"] = sleep["date"] + pd.Timedelta(days=1)

    daily_load = (
        train_df.groupby("date")["weekly_load"]
        .max()
        .reset_index()
        .rename(columns={"weekly_load": "load"})
    )

    merged = sleep.merge(daily_load, left_on="next_date", right_on="date", suffixes=("", "_load"))
    merged = merged.rename(columns={"date": "sleep_date"})
    merged = merged.dropna(subset=["load"])
    return merged[["sleep_date", "total_sleep_h", "deep_pct", "rem_pct", "load"]]


# ---------------------------------------------------------------------------
# Combined weekly volume (running km + swimming km)
# ---------------------------------------------------------------------------

def combined_weekly_volume(run_df: pd.DataFrame, swim_df: pd.DataFrame) -> pd.DataFrame:
    """Weekly combined training volume in km."""
    rows = []
    if not run_df.empty:
        r = run_df.copy()
        r["week"] = r["date"].dt.to_period("W").dt.start_time
        r_agg = r.groupby("week")["distance_km"].sum().reset_index()
        r_agg["sport"] = "Running"
        rows.append(r_agg.rename(columns={"distance_km": "km"}))

    if not swim_df.empty:
        s = swim_df.copy()
        s["week"] = s["date"].dt.to_period("W").dt.start_time
        s["distance_km"] = s["distance_m"] / 1000
        s_agg = s.groupby("week")["distance_km"].sum().reset_index()
        s_agg["sport"] = "Swimming"
        rows.append(s_agg.rename(columns={"distance_km": "km"}))

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows).sort_values("week").reset_index(drop=True)
