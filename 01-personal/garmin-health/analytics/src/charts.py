"""
Plotly chart builders for the Garmin Health Analytics Dashboard.
Each function accepts pre-computed DataFrames and returns a plotly Figure.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Shared color palette
COLORS = {
    "running": "#FF6B35",
    "swimming": "#2196F3",
    "deep": "#1A237E",
    "rem": "#7B1FA2",
    "light": "#64B5F6",
    "awake": "#FFCA28",
    "safe": "#4CAF50",
    "caution": "#FF9800",
    "injury": "#F44336",
    "under": "#9E9E9E",
}

_LAYOUT = dict(
    template="plotly_white",
    font=dict(family="Inter, Arial, sans-serif", size=13),
    margin=dict(l=50, r=20, t=50, b=40),
    hovermode="x unified",
)


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

def weekly_volume_bar(volume_df: pd.DataFrame) -> go.Figure:
    """Stacked bar: running km + swimming km per week."""
    fig = go.Figure()
    for sport, color in [("Running", COLORS["running"]), ("Swimming", COLORS["swimming"])]:
        d = volume_df[volume_df["sport"] == sport]
        fig.add_trace(go.Bar(
            x=d["week"], y=d["km"],
            name=sport, marker_color=color,
        ))
    fig.update_layout(
        **_LAYOUT,
        barmode="stack",
        title="Weekly Training Volume (km)",
        xaxis_title="Week",
        yaxis_title="Distance (km)",
    )
    return fig


def steps_trend_bar(well_df: pd.DataFrame) -> go.Figure:
    """Daily steps vs 10k goal."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=well_df["date"], y=well_df["steps"],
        name="Steps",
        marker_color=[COLORS["safe"] if s >= 10000 else COLORS["caution"]
                      for s in well_df["steps"]],
    ))
    fig.add_hline(y=10000, line_dash="dash", line_color="gray",
                  annotation_text="Goal: 10,000", annotation_position="top right")
    fig.update_layout(**_LAYOUT, title="Daily Steps vs Goal", yaxis_title="Steps")
    return fig


def resting_hr_trend(well_df: pd.DataFrame) -> go.Figure:
    """Resting HR trend from wellness data."""
    d = well_df.dropna(subset=["resting_hr"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["resting_hr"],
        mode="lines", name="Resting HR",
        line=dict(color=COLORS["swimming"], width=2),
        fill="tozeroy", fillcolor="rgba(33,150,243,0.1)",
    ))
    fig.update_layout(**_LAYOUT, title="Resting Heart Rate Trend",
                      yaxis_title="HR (bpm)")
    return fig


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------

def pace_trend_line(run_df: pd.DataFrame) -> go.Figure:
    """Running pace trend (min/km). Lower = faster."""
    d = run_df.dropna(subset=["pace_min_per_km"])

    def fmt_pace(p):
        m = int(p)
        s = int((p - m) * 60)
        return f"{m}:{s:02d}"

    hover = d["pace_min_per_km"].apply(fmt_pace)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["pace_min_per_km"],
        mode="lines+markers",
        name="Pace",
        line=dict(color=COLORS["running"], width=2),
        marker=dict(size=5),
        text=hover,
        hovertemplate="%{x|%b %d, %Y}<br>Pace: %{text} min/km<extra></extra>",
    ))
    # 30-day rolling average
    d_sorted = d.sort_values("date").copy()
    d_sorted["rolling_pace"] = d_sorted["pace_min_per_km"].rolling(5, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=d_sorted["date"], y=d_sorted["rolling_pace"],
        mode="lines", name="5-session avg",
        line=dict(color="rgba(255,107,53,0.4)", width=2, dash="dash"),
    ))
    fig.update_layout(
        **_LAYOUT,
        title="Running Pace Trend (lower = faster)",
        yaxis_title="Pace (min/km)",
        yaxis_autorange="reversed",
    )
    return fig


def distance_trend_line(run_df: pd.DataFrame, sport: str = "Running") -> go.Figure:
    """Session distance trend."""
    color = COLORS["running"] if sport == "Running" else COLORS["swimming"]
    dist_col = "distance_km" if sport == "Running" else "distance_m"
    unit = "km" if sport == "Running" else "m"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=run_df["date"], y=run_df[dist_col],
        mode="lines+markers", name=f"Distance ({unit})",
        line=dict(color=color, width=2),
        marker=dict(size=5),
    ))
    fig.update_layout(
        **_LAYOUT,
        title=f"{sport} Distance Per Session",
        yaxis_title=f"Distance ({unit})",
    )
    return fig


def hr_distribution_scatter(run_df: pd.DataFrame, swim_df: pd.DataFrame) -> go.Figure:
    """Avg HR per session, colored by sport."""
    fig = go.Figure()
    for df, name, color in [(run_df, "Running", COLORS["running"]),
                             (swim_df, "Swimming", COLORS["swimming"])]:
        if df.empty or "avg_hr" not in df.columns:
            continue
        d = df.dropna(subset=["avg_hr"])
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["avg_hr"],
            mode="markers", name=name,
            marker=dict(color=color, size=6, opacity=0.7),
        ))
    for zone, (lo, hi) in [("Z2 Aerobic", (120, 140)), ("Z3 Threshold", (140, 155))]:
        fig.add_hrect(y0=lo, y1=hi, fillcolor="rgba(100,200,100,0.07)",
                      line_width=0, annotation_text=zone,
                      annotation_position="top right")
    fig.update_layout(**_LAYOUT, title="Average Heart Rate Per Session",
                      yaxis_title="Avg HR (bpm)")
    return fig


def cadence_trend_line(run_df: pd.DataFrame) -> go.Figure:
    """Running cadence trend (steps per minute). Target: 170–185 spm."""
    d = run_df.dropna(subset=["cadence_spm"])
    d = d[d["cadence_spm"] > 0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["cadence_spm"],
        mode="lines+markers", name="Cadence",
        line=dict(color=COLORS["running"], width=2),
        marker=dict(size=5),
    ))
    fig.add_hrect(y0=170, y1=185, fillcolor="rgba(76,175,80,0.12)",
                  line_width=0, annotation_text="Target: 170–185 spm",
                  annotation_position="top right")
    fig.update_layout(**_LAYOUT, title="Running Cadence (steps/min)",
                      yaxis_title="Cadence (spm)")
    return fig


def race_predictions_line(race_df: pd.DataFrame) -> go.Figure:
    """Race prediction times over time. Lower = better."""
    races = [
        ("5k_sec",      "5K",         "#FF6B35"),
        ("10k_sec",     "10K",        "#E91E63"),
        ("half_sec",    "Half Marathon", "#9C27B0"),
        ("marathon_sec","Marathon",   "#3F51B5"),
    ]
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=["5K", "10K", "Half Marathon", "Marathon"],
                        shared_xaxes=False)
    positions = [(1,1),(1,2),(2,1),(2,2)]
    for (col, label, color), (row, c) in zip(races, positions):
        d = race_df.dropna(subset=[col])
        # Format seconds to HH:MM:SS for hover
        def to_min(s):
            return s / 60
        fig.add_trace(
            go.Scatter(
                x=d["date"],
                y=d[col] / 60,  # display in minutes
                mode="lines",
                name=label,
                line=dict(color=color, width=2),
                hovertemplate="%{x|%b %d}<br>" + label + ": %{customdata}<extra></extra>",
                customdata=d[label.lower().replace(" ", "_") + "_fmt"]
                    if label.lower().replace(" ", "_") + "_fmt" in d.columns
                    else d[col].apply(lambda s: f"{int(s//60)}:{int(s%60):02d}"),
            ),
            row=row, col=c,
        )
    fig.update_layout(
        **_LAYOUT,
        title="Garmin Race Predictions Over Time (lower = faster)",
        showlegend=False,
    )
    fig.update_yaxes(title_text="Minutes", autorange="reversed")
    return fig


# ---------------------------------------------------------------------------
# Swimming
# ---------------------------------------------------------------------------

def swolf_trend_line(swim_df: pd.DataFrame) -> go.Figure:
    """SWOLF score trend. Lower = more efficient."""
    d = swim_df.dropna(subset=["avg_swolf"])
    d = d[d["avg_swolf"] > 0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["avg_swolf"],
        mode="lines+markers", name="SWOLF",
        line=dict(color=COLORS["swimming"], width=2),
        marker=dict(size=5),
    ))
    fig.add_hline(y=40, line_dash="dash", line_color="green",
                  annotation_text="Elite: <40", annotation_position="bottom right")
    fig.update_layout(
        **_LAYOUT,
        title="SWOLF Score Trend (lower = more efficient)",
        yaxis_title="SWOLF",
        yaxis_autorange="reversed",
    )
    return fig


# ---------------------------------------------------------------------------
# Sleep
# ---------------------------------------------------------------------------

def sleep_duration_bar(sleep_df: pd.DataFrame) -> go.Figure:
    """Nightly total sleep hours with 7h/8.5h reference lines."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sleep_df["date"], y=sleep_df["total_sleep_h"],
        name="Total Sleep",
        marker_color=[
            COLORS["safe"] if h >= 8 else (COLORS["caution"] if h >= 7 else COLORS["injury"])
            for h in sleep_df["total_sleep_h"]
        ],
    ))
    fig.add_hline(y=8.5, line_dash="dash", line_color="green",
                  annotation_text="Optimal: 8.5h", annotation_position="top right")
    fig.add_hline(y=7, line_dash="dot", line_color="orange",
                  annotation_text="Minimum: 7h", annotation_position="bottom right")
    fig.update_layout(**_LAYOUT, title="Nightly Sleep Duration",
                      yaxis_title="Hours", yaxis=dict(range=[0, 12]))
    return fig


def sleep_stages_stacked_bar(sleep_df: pd.DataFrame) -> go.Figure:
    """Stacked bar: Deep / REM / Light / Awake per night (minutes)."""
    fig = go.Figure()
    for col, name, color in [
        ("deep_min",  "Deep",  COLORS["deep"]),
        ("rem_min",   "REM",   COLORS["rem"]),
        ("light_min", "Light", COLORS["light"]),
        ("awake_min", "Awake", COLORS["awake"]),
    ]:
        fig.add_trace(go.Bar(
            x=sleep_df["date"], y=sleep_df[col],
            name=name, marker_color=color,
        ))
    fig.update_layout(
        **_LAYOUT,
        barmode="stack",
        title="Sleep Stage Breakdown (minutes per night)",
        yaxis_title="Minutes",
    )
    return fig


def sleep_stage_pct_line(sleep_df: pd.DataFrame) -> go.Figure:
    """Deep% and REM% trends with target reference lines."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sleep_df["date"], y=sleep_df["deep_pct"],
        mode="lines", name="Deep %",
        line=dict(color=COLORS["deep"], width=2),
    ))
    fig.add_trace(go.Scatter(
        x=sleep_df["date"], y=sleep_df["rem_pct"],
        mode="lines", name="REM %",
        line=dict(color=COLORS["rem"], width=2),
    ))
    fig.add_hline(y=15, line_dash="dash", line_color=COLORS["deep"],
                  annotation_text="Deep target: 15%", annotation_position="top left")
    fig.add_hline(y=20, line_dash="dash", line_color=COLORS["rem"],
                  annotation_text="REM target: 20%", annotation_position="top right")
    fig.update_layout(
        **_LAYOUT,
        title="Sleep Stage Quality (% of total sleep)",
        yaxis_title="% of Sleep",
        yaxis=dict(range=[0, 60]),
    )
    return fig


def respiration_trend(sleep_df: pd.DataFrame) -> go.Figure:
    """Average respiration rate per night."""
    d = sleep_df.dropna(subset=["respiration_avg"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d["respiration_avg"],
        mode="lines", name="Respiration",
        line=dict(color="#26A69A", width=2),
    ))
    fig.add_hrect(y0=12, y1=20, fillcolor="rgba(76,175,80,0.1)",
                  line_width=0, annotation_text="Normal range (12–20)",
                  annotation_position="top right")
    fig.update_layout(**_LAYOUT, title="Avg Respiration Rate During Sleep",
                      yaxis_title="Breaths/min")
    return fig


# ---------------------------------------------------------------------------
# Fitness & Recovery
# ---------------------------------------------------------------------------

def vo2max_trend_line(vo2_df: pd.DataFrame) -> go.Figure:
    """VO2Max and Fitness Age on dual-axis chart."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=vo2_df["date"], y=vo2_df["vo2max"],
        mode="lines", name="VO2Max",
        line=dict(color=COLORS["running"], width=2),
    ), secondary_y=False)

    d2 = vo2_df.dropna(subset=["fitness_age"])
    fig.add_trace(go.Scatter(
        x=d2["date"], y=d2["fitness_age"],
        mode="lines", name="Fitness Age",
        line=dict(color=COLORS["swimming"], width=2, dash="dash"),
    ), secondary_y=True)

    fig.update_yaxes(title_text="VO2Max (ml/kg/min)", secondary_y=False)
    fig.update_yaxes(title_text="Fitness Age (years)", secondary_y=True)
    fig.update_layout(**_LAYOUT, title="VO2Max & Fitness Age Over Time")
    return fig


def acwr_chart(acwr_df: pd.DataFrame) -> go.Figure:
    """ACWR ratio with color-coded risk zones."""
    fig = go.Figure()

    # Background risk zones
    fig.add_hrect(y0=0,   y1=0.8, fillcolor="rgba(158,158,158,0.15)", line_width=0,
                  annotation_text="Undertraining (<0.8)", annotation_position="top left")
    fig.add_hrect(y0=0.8, y1=1.3, fillcolor="rgba(76,175,80,0.15)",  line_width=0,
                  annotation_text="Safe Zone (0.8–1.3)", annotation_position="top left")
    fig.add_hrect(y0=1.3, y1=1.5, fillcolor="rgba(255,152,0,0.15)", line_width=0,
                  annotation_text="Caution (1.3–1.5)", annotation_position="top left")
    fig.add_hrect(y0=1.5, y1=3.5, fillcolor="rgba(244,67,54,0.10)",  line_width=0,
                  annotation_text="Injury Risk (>1.5)", annotation_position="top right")

    # ACWR line colored by zone
    zone_colors = {
        "Undertraining": COLORS["under"],
        "Safe":          COLORS["safe"],
        "Caution":       COLORS["caution"],
        "Injury Risk":   COLORS["injury"],
    }
    fig.add_trace(go.Scatter(
        x=acwr_df["date"], y=acwr_df["acwr"],
        mode="lines",
        name="ACWR",
        line=dict(color="#333", width=2),
        hovertemplate="%{x|%b %d}<br>ACWR: %{y:.2f}<extra></extra>",
    ))
    fig.add_hline(y=1.0, line_dash="dot", line_color="gray")
    fig.update_layout(
        **_LAYOUT,
        title="Acute-to-Chronic Workload Ratio (ACWR)",
        yaxis_title="ACWR",
        yaxis=dict(range=[0, 3.5]),
    )
    return fig


def intensity_minutes_bar(well_weekly: pd.DataFrame) -> go.Figure:
    """Weekly intensity minutes (moderate + vigorous) vs WHO 150 min target."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=well_weekly["week"], y=well_weekly["total_moderate_min"],
        name="Moderate", marker_color=COLORS["caution"],
    ))
    fig.add_trace(go.Bar(
        x=well_weekly["week"], y=well_weekly["total_vigorous_min"],
        name="Vigorous", marker_color=COLORS["running"],
    ))
    fig.add_hline(y=150, line_dash="dash", line_color="green",
                  annotation_text="WHO Target: 150 min moderate/wk",
                  annotation_position="top right")
    fig.update_layout(
        **_LAYOUT,
        barmode="stack",
        title="Weekly Intensity Minutes vs WHO Target",
        yaxis_title="Minutes",
    )
    return fig


# ---------------------------------------------------------------------------
# Cross-Pillar
# ---------------------------------------------------------------------------

def sleep_vs_load_scatter(merged_df: pd.DataFrame) -> go.Figure:
    """Sleep hours vs next-day training load (scatter)."""
    fig = px.scatter(
        merged_df,
        x="total_sleep_h",
        y="load",
        color="deep_pct",
        color_continuous_scale="Blues",
        labels={
            "total_sleep_h": "Sleep Duration (hours)",
            "load": "Next-Day Training Load",
            "deep_pct": "Deep Sleep %",
        },
        title="Sleep Duration vs Next-Day Training Load",
        hover_data={"sleep_date": True, "rem_pct": True},
    )
    fig.add_vline(x=7, line_dash="dash", line_color="orange",
                  annotation_text="Min sleep: 7h", annotation_position="top right")
    fig.update_layout(**_LAYOUT)
    return fig


def resting_hr_vs_vo2max(well_df: pd.DataFrame, vo2_df: pd.DataFrame) -> go.Figure:
    """Resting HR vs VO2Max on dual-axis timeline."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    d1 = well_df.dropna(subset=["resting_hr"])
    fig.add_trace(go.Scatter(
        x=d1["date"], y=d1["resting_hr"],
        mode="lines", name="Resting HR",
        line=dict(color=COLORS["running"], width=1.5),
        opacity=0.8,
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=vo2_df["date"], y=vo2_df["vo2max"],
        mode="lines", name="VO2Max",
        line=dict(color=COLORS["swimming"], width=2),
    ), secondary_y=True)

    fig.update_yaxes(title_text="Resting HR (bpm)", secondary_y=False)
    fig.update_yaxes(title_text="VO2Max (ml/kg/min)", secondary_y=True)
    fig.update_layout(**_LAYOUT,
                      title="Resting HR vs VO2Max — Inverse Correlation Expected")
    return fig
