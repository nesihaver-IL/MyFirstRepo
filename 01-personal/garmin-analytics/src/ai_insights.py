"""
Claude AI insights module.

Builds a compact summary of the athlete's recent performance data,
loads the 3 expertise documents as the AI knowledge base,
and sends a structured prompt to Claude for personalized recommendations.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

_DOCS_DIR = Path(__file__).parent.parent.parent / "aws-ai-agent" / "docs"

ATHLETE_PROFILE = {
    "age": 47,
    "height_m": 1.80,
    "weight_kg": 70,
    "max_hr_est": 173,
    "sports": ["Running", "Swimming"],
    "running_goal": "Half-Marathon",
    "swimming_goal": "2000m sessions",
}

EXPERTISE_FILES = [
    ("Research_Summary_Swimming.md",   "Swimming Science"),
    ("Research_Summary_Running-EN.md", "Running Science"),
    ("Research_Summary_sleeping-1.md", "Sleep & Recovery Science"),
]


def load_expertise_docs() -> str:
    """Read all 3 research documents and combine into one text block."""
    parts = []
    for filename, title in EXPERTISE_FILES:
        path = _DOCS_DIR / filename
        if path.exists():
            text = path.read_text(encoding="utf-8")
            parts.append(f"## EXPERTISE DOCUMENT: {title}\n\n{text}")
        else:
            parts.append(f"## EXPERTISE DOCUMENT: {title}\n\n[File not found: {filename}]")
    return "\n\n---\n\n".join(parts)


def build_data_summary(
    run_df: pd.DataFrame,
    swim_df: pd.DataFrame,
    sleep_df: pd.DataFrame,
    well_df: pd.DataFrame,
    vo2_df: pd.DataFrame,
    race_df: pd.DataFrame,
    acwr_df: pd.DataFrame,
    days: int = 90,
) -> str:
    """
    Aggregate the last `days` of data into a compact text summary.
    Only aggregated statistics are sent — no raw records.
    """
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
    lines = [f"# Athlete Data Summary — Last {days} Days\n"]

    # --- Athlete Profile ---
    lines.append("## Athlete Profile")
    p = ATHLETE_PROFILE
    lines.append(f"- Age: {p['age']} | Height: {p['height_m']}m | Weight: {p['weight_kg']}kg")
    lines.append(f"- Estimated Max HR: {p['max_hr_est']} bpm")
    lines.append(f"- Sports: {', '.join(p['sports'])}")
    lines.append(f"- Running goal: {p['running_goal']}")
    lines.append(f"- Swimming goal: {p['swimming_goal']}\n")

    # --- Running ---
    lines.append("## Running")
    r = run_df[run_df["date"] >= cutoff] if not run_df.empty else pd.DataFrame()
    if not r.empty:
        lines.append(f"- Sessions: {len(r)}")
        lines.append(f"- Total distance: {r['distance_km'].sum():.1f} km")
        lines.append(f"- Avg distance per session: {r['distance_km'].mean():.1f} km")
        lines.append(f"- Avg pace: {r['pace_min_per_km'].mean():.2f} min/km" if r["pace_min_per_km"].notna().any() else "- Avg pace: N/A")
        lines.append(f"- Avg HR: {r['avg_hr'].mean():.0f} bpm" if r["avg_hr"].notna().any() else "- Avg HR: N/A")
        lines.append(f"- Avg cadence: {r['cadence_spm'].mean():.0f} spm" if r["cadence_spm"].notna().any() else "- Avg cadence: N/A")
        # Pace trend: compare first half vs second half
        mid = r["date"].median()
        r1 = r[r["date"] < mid]["pace_min_per_km"].mean()
        r2 = r[r["date"] >= mid]["pace_min_per_km"].mean()
        if not (np.isnan(r1) or np.isnan(r2)):
            trend = "improving" if r2 < r1 else "declining"
            lines.append(f"- Pace trend: {trend} (early avg {r1:.2f} → recent avg {r2:.2f} min/km)")
    else:
        lines.append("- No running data in this period\n")
    lines.append("")

    # --- Swimming ---
    lines.append("## Swimming")
    s = swim_df[swim_df["date"] >= cutoff] if not swim_df.empty else pd.DataFrame()
    if not s.empty:
        lines.append(f"- Sessions: {len(s)}")
        lines.append(f"- Total distance: {s['distance_m'].sum()/1000:.1f} km")
        lines.append(f"- Avg session duration: {s['duration_min'].mean():.0f} min")
        lines.append(f"- Avg distance per session: {s['distance_m'].mean():.0f} m")
        if s["avg_hr"].notna().any():
            lines.append(f"- Avg HR: {s['avg_hr'].mean():.0f} bpm")
        if s["avg_swolf"].notna().any():
            lines.append(f"- Avg SWOLF: {s['avg_swolf'].mean():.1f} (lower = more efficient)")
    else:
        lines.append("- No swimming data in this period")
    lines.append("")

    # --- Sleep ---
    lines.append("## Sleep & Recovery")
    sl = sleep_df[sleep_df["date"] >= cutoff] if not sleep_df.empty else pd.DataFrame()
    if not sl.empty:
        lines.append(f"- Nights tracked: {len(sl)}")
        lines.append(f"- Avg total sleep: {sl['total_sleep_h'].mean():.2f} hours")
        lines.append(f"- Nights under 7h: {(sl['total_sleep_h'] < 7).sum()} ({100*(sl['total_sleep_h'] < 7).mean():.0f}%)")
        lines.append(f"- Avg Deep Sleep: {sl['deep_pct'].mean():.1f}% (target: >15%)")
        lines.append(f"- Avg REM Sleep: {sl['rem_pct'].mean():.1f}% (target: >20%)")
        if sl["respiration_avg"].notna().any():
            lines.append(f"- Avg respiration: {sl['respiration_avg'].mean():.1f} breaths/min")
        # Nights with deep_pct < 10% (concerning)
        low_deep = (sl["deep_pct"] < 10).sum()
        if low_deep > 0:
            lines.append(f"- Nights with very low deep sleep (<10%): {low_deep}")
    else:
        lines.append("- No sleep data in this period")
    lines.append("")

    # --- VO2Max ---
    lines.append("## Fitness Indicators")
    v = vo2_df[vo2_df["date"] >= cutoff] if not vo2_df.empty else pd.DataFrame()
    if not v.empty:
        latest_vo2 = v["vo2max"].iloc[-1]
        earliest_vo2 = v["vo2max"].iloc[0]
        fa = v["fitness_age"].dropna()
        lines.append(f"- VO2Max: {latest_vo2:.0f} ml/kg/min (start of period: {earliest_vo2:.0f})")
        if not fa.empty:
            lines.append(f"- Fitness Age: {fa.iloc[-1]:.0f} years (chronological: 47)")
    else:
        lines.append("- No VO2Max data in this period")

    # --- ACWR ---
    if not acwr_df.empty:
        ac = acwr_df[acwr_df["date"] >= cutoff]
        if not ac.empty:
            latest_acwr = ac["acwr"].iloc[-1]
            avg_acwr = ac["acwr"].mean()
            zone = ac["risk_zone"].iloc[-1]
            lines.append(f"- Current ACWR: {latest_acwr:.2f} ({zone})")
            lines.append(f"- Avg ACWR over period: {avg_acwr:.2f}")
    lines.append("")

    # --- Race Predictions ---
    lines.append("## Race Predictions (Garmin Estimates)")
    rp = race_df[race_df["date"] >= cutoff] if not race_df.empty else pd.DataFrame()
    if not rp.empty:
        latest = rp.iloc[-1]
        earliest = rp.iloc[0]
        for col, label in [("half_sec", "Half Marathon"), ("5k_sec", "5K"), ("10k_sec", "10K")]:
            if pd.notna(latest.get(col)):
                old_sec = earliest.get(col, None)
                improvement = ""
                if old_sec and not np.isnan(old_sec):
                    diff = old_sec - latest[col]
                    if diff > 0:
                        improvement = f" (improved by {int(diff//60)}:{int(diff%60):02d})"
                    elif diff < 0:
                        improvement = f" (slower by {int(abs(diff)//60)}:{int(abs(diff)%60):02d})"
                def fmt(s):
                    if pd.isna(s): return "—"
                    s = int(s)
                    h, rem = divmod(s, 3600)
                    m, sec = divmod(rem, 60)
                    return f"{h}:{m:02d}:{sec:02d}" if h > 0 else f"{m}:{sec:02d}"
                lines.append(f"- {label}: {fmt(latest[col])}{improvement}")
    lines.append("")

    return "\n".join(lines)


def generate_insights(
    run_df: pd.DataFrame,
    swim_df: pd.DataFrame,
    sleep_df: pd.DataFrame,
    well_df: pd.DataFrame,
    vo2_df: pd.DataFrame,
    race_df: pd.DataFrame,
    acwr_df: pd.DataFrame,
    days: int = 90,
) -> str:
    """
    Call Claude API and return a structured 4-section analysis.
    Returns the AI response text, or an error message.
    """
    try:
        import anthropic
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        return "Error: `anthropic` or `python-dotenv` package not installed."

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return (
            "ANTHROPIC_API_KEY not set.\n\n"
            "To enable AI insights:\n"
            "1. Copy `.env.example` to `.env`\n"
            "2. Add your Anthropic API key: `ANTHROPIC_API_KEY=sk-ant-...`\n"
            "3. Restart the app."
        )

    data_summary = build_data_summary(
        run_df, swim_df, sleep_df, well_df, vo2_df, race_df, acwr_df, days=days
    )
    expertise = load_expertise_docs()

    prompt = f"""You are a personal performance coach and sports scientist for a masters athlete.
You have access to the athlete's recent Garmin training data AND their personal knowledge base of sports science research documents.

Your task: analyze the athlete's data against the science in the expertise documents, then provide a structured, actionable 4-section analysis.

Be specific — reference actual numbers from the data summary. Reference specific recommendations from the expertise documents.
Keep each section focused and actionable (3–5 bullet points each).

---

{data_summary}

---

# EXPERTISE KNOWLEDGE BASE

{expertise}

---

# YOUR ANALYSIS (respond with exactly these 4 sections):

## 1. Training Load Assessment
Analyze the ACWR ratio and overall training volume. Is the athlete in a safe zone? Any injury risk signals?

## 2. Running Analysis
Analyze pace trends, cadence, HR zones, and race prediction progress. Compare to the 80/20 rule, 10% rule, and cadence targets from the expertise documents.

## 3. Swimming Analysis
Analyze session consistency, distance trends, HR zones, and SWOLF efficiency. Reference the CSS and biomechanics guidance from the Swimming expertise document.

## 4. Sleep & Recovery Recommendations
Analyze sleep stage quality (deep %, REM %), total duration, and any patterns. Cross-reference with the sleep optimization protocols. Flag any concerning patterns (e.g., consistently low deep sleep, nights under 7h).
"""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
