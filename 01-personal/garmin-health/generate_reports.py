#!/usr/bin/env python3
"""
Generate interactive Plotly charts and save as standalone HTML reports.
Run: python3 generate_reports.py
"""

import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime

# Configuration
DOCS_DIR = Path("../aws-ai-agent/docs")
OUTPUT_DIR = Path("data/exports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    """Load all Garmin data from JSON files."""
    print("Loading data...", end=" ", flush=True)

    # Load activities
    with open(DOCS_DIR / "nesihaver@gmail.com_0_summarizedActivities.json") as f:
        acts_data = json.load(f)
    activities = acts_data[0].get("summarizedActivitiesExport", [])

    # Parse activities
    runs, swims = [], []
    for a in activities:
        sport = a.get("sportType", "")
        ts = a.get("startTimeGmt")
        if not ts:
            continue

        date = pd.to_datetime(ts, unit="ms").normalize()
        dur_min = a.get("duration", 0) / 60000
        dist_cm = a.get("distance", 0)

        if dur_min <= 0 or dist_cm <= 0:
            continue

        if sport == "RUNNING":
            dist_km = dist_cm / 100000
            pace = (dur_min / dist_km) if dist_km > 0 else None
            if pace and 3 < pace < 15:
                runs.append({
                    "date": date,
                    "distance_km": round(dist_km, 2),
                    "duration_min": round(dur_min, 1),
                    "pace": round(pace, 2),
                    "avg_hr": a.get("avgHr"),
                    "max_hr": a.get("maxHr"),
                    "calories": a.get("calories", 0),
                })
        elif sport == "SWIMMING":
            dist_m = dist_cm / 100
            swims.append({
                "date": date,
                "distance_m": round(dist_m, 0),
                "duration_min": round(dur_min, 1),
                "avg_hr": a.get("avgHr"),
                "max_hr": a.get("maxHr"),
                "calories": a.get("calories", 0),
            })

    run_df = pd.DataFrame(runs).sort_values("date").reset_index(drop=True)
    swim_df = pd.DataFrame(swims).sort_values("date").reset_index(drop=True)

    # Load sleep
    with open(DOCS_DIR / "sleep_all_merged.json") as f:
        sleep_data = json.load(f)

    sleep_rows = []
    for r in sleep_data:
        if r.get("sleepWindowConfirmationType") not in {"ENHANCED_CONFIRMED_FINAL", "ENHANCED_CONFIRMED"}:
            continue
        date = pd.to_datetime(r["calendarDate"])
        deep_min = r.get("deepSleepSeconds", 0) / 60
        light_min = r.get("lightSleepSeconds", 0) / 60
        rem_min = r.get("remSleepSeconds", 0) / 60
        total_min = deep_min + light_min + rem_min
        sleep_rows.append({
            "date": date,
            "total_sleep_h": round(total_min / 60, 2),
            "deep_min": round(deep_min, 1),
            "rem_min": round(rem_min, 1),
            "light_min": round(light_min, 1),
            "deep_pct": round(100 * deep_min / total_min, 1) if total_min > 0 else 0,
            "rem_pct": round(100 * rem_min / total_min, 1) if total_min > 0 else 0,
            "light_pct": round(100 * light_min / total_min, 1) if total_min > 0 else 0,
        })
    sleep_df = pd.DataFrame(sleep_rows).sort_values("date").reset_index(drop=True)

    print("OK")
    return run_df, swim_df, sleep_df


def chart_1_running_trends(run_df):
    """Running pace and distance trends over time."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=run_df["date"], y=run_df["distance_km"],
                   name="Distance (km)", mode="markers",
                   marker=dict(size=6, color="green", opacity=0.6)),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=run_df["date"], y=run_df["pace"],
                   name="Pace (min/km)", mode="lines+markers",
                   line=dict(color="blue", width=2),
                   marker=dict(size=4)),
        secondary_y=True,
    )

    fig.update_layout(
        title="Running Performance: Distance vs Pace Over Time",
        hovermode="x unified",
        height=500,
        template="plotly_white",
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Distance (km)", secondary_y=False)
    fig.update_yaxes(title_text="Pace (min/km)", secondary_y=True)

    return fig


def chart_2_swimming_trends(swim_df):
    """Swimming distance and sessions over time."""
    fig = px.bar(swim_df, x="date", y="distance_m",
                 hover_data={"duration_min": ":.0f", "avg_hr": ":.0f"},
                 title="Swimming Sessions: Distance per Session",
                 labels={"distance_m": "Distance (meters)", "date": "Date"})
    fig.update_traces(marker_color="steelblue")
    fig.update_layout(height=500, template="plotly_white", hovermode="x unified")
    return fig


def chart_3_weekly_volume(run_df, swim_df):
    """Weekly training volume comparison."""
    run_weekly = run_df.copy()
    run_weekly["week"] = run_weekly["date"].dt.to_period("W")
    run_agg = run_weekly.groupby("week")["distance_km"].sum().reset_index()
    run_agg["week"] = run_agg["week"].dt.start_time
    run_agg["sport"] = "Running"
    run_agg = run_agg.rename(columns={"distance_km": "km"})

    swim_weekly = swim_df.copy()
    swim_weekly["week"] = swim_weekly["date"].dt.to_period("W")
    swim_agg = swim_weekly.groupby("week")["distance_m"].sum().reset_index()
    swim_agg["week"] = swim_agg["week"].dt.start_time
    swim_agg["sport"] = "Swimming"
    swim_agg["km"] = swim_agg["distance_m"] / 1000
    swim_agg = swim_agg[["week", "km", "sport"]]

    combined = pd.concat([run_agg, swim_agg])

    fig = px.bar(combined, x="week", y="km", color="sport",
                 title="Weekly Training Volume: Running vs Swimming",
                 labels={"km": "Distance (km)", "week": "Week"},
                 barmode="stack")
    fig.update_layout(height=500, template="plotly_white", hovermode="x unified")
    return fig


def chart_4_sleep_analysis(sleep_df):
    """Sleep quality analysis."""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Nightly Sleep Duration", "Sleep Stage Composition"),
        specs=[[{"type": "bar"}], [{"type": "box"}]]
    )

    fig.add_trace(
        go.Bar(x=sleep_df["date"], y=sleep_df["total_sleep_h"],
               name="Sleep Duration", marker_color="navy",
               hovertemplate="%{x|%Y-%m-%d}<br>%{y:.1f}h<extra></extra>"),
        row=1, col=1,
    )

    fig.add_trace(
        go.Box(y=sleep_df["deep_pct"], name="Deep %", marker_color="darkblue"),
        row=2, col=1,
    )
    fig.add_trace(
        go.Box(y=sleep_df["rem_pct"], name="REM %", marker_color="royalblue"),
        row=2, col=1,
    )

    fig.update_yaxes(title_text="Hours", row=1, col=1)
    fig.update_yaxes(title_text="Percentage", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_layout(height=600, title_text="Sleep Analysis", template="plotly_white")

    return fig


def chart_5_heart_rate_zones(run_df):
    """Heart rate distribution during running."""
    fig = px.histogram(run_df, x="avg_hr", nbins=30,
                       title="Running Sessions: Heart Rate Distribution",
                       labels={"avg_hr": "Average HR (bpm)", "count": "Sessions"},
                       marginal="box")
    fig.update_traces(marker_color="coral")
    fig.update_layout(height=500, template="plotly_white")
    return fig


def chart_6_training_summary(run_df, swim_df):
    """Overall training summary metrics."""
    metrics = {
        "Running": [len(run_df), run_df["distance_km"].sum(), run_df["calories"].sum()],
        "Swimming": [len(swim_df), swim_df["distance_m"].sum()/1000, swim_df["calories"].sum()],
    }

    fig = go.Figure(data=[
        go.Bar(name="Sessions", x=list(metrics.keys()), y=[m[0] for m in metrics.values()]),
        go.Bar(name="Distance (km)", x=list(metrics.keys()), y=[m[1] for m in metrics.values()]),
    ])

    fig.update_layout(
        title="Training Summary: Sessions and Distance",
        barmode="group",
        height=500,
        template="plotly_white",
    )
    return fig


def main():
    """Generate all reports."""
    print("\n" + "="*60)
    print("Generating Interactive Health Analytics Reports")
    print("="*60 + "\n")

    run_df, swim_df, sleep_df = load_data()

    charts = [
        ("01_running_trends.html", "Running Performance Trends", chart_1_running_trends(run_df)),
        ("02_swimming_trends.html", "Swimming Performance Trends", chart_2_swimming_trends(swim_df)),
        ("03_weekly_volume.html", "Weekly Training Volume", chart_3_weekly_volume(run_df, swim_df)),
        ("04_sleep_analysis.html", "Sleep Quality Analysis", chart_4_sleep_analysis(sleep_df)),
        ("05_heart_rate_zones.html", "Heart Rate Distribution", chart_5_heart_rate_zones(run_df)),
        ("06_training_summary.html", "Training Summary", chart_6_training_summary(run_df, swim_df)),
    ]

    for filename, title, fig in charts:
        filepath = OUTPUT_DIR / filename
        fig.write_html(filepath)
        print(f"[OK] {title:<40} -> {filename}")

    print("\n" + "="*60)
    print(f"Reports generated in: {OUTPUT_DIR.resolve()}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
