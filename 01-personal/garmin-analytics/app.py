"""
Garmin Health Analytics Dashboard
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta

# Must be first Streamlit call
st.set_page_config(
    page_title="Garmin Health Analytics",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.data_loader import (
    load_activities, load_sleep, load_wellness,
    load_vo2max, load_race_predictions, load_training_history, filter_dates
)
from src.metrics import (
    running_weekly, swimming_weekly, sleep_weekly_score,
    compute_acwr, wellness_weekly, combined_weekly_volume,
    running_with_zones, sleep_vs_next_load
)
from src.charts import (
    weekly_volume_bar, steps_trend_bar, resting_hr_trend,
    pace_trend_line, distance_trend_line, hr_distribution_scatter,
    cadence_trend_line, race_predictions_line,
    swolf_trend_line,
    sleep_duration_bar, sleep_stages_stacked_bar,
    sleep_stage_pct_line, respiration_trend,
    vo2max_trend_line, acwr_chart, intensity_minutes_bar,
    sleep_vs_load_scatter, resting_hr_vs_vo2max
)
from src.ai_insights import generate_insights


# ---------------------------------------------------------------------------
# Load all data (cached)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Loading training data...")
def load_all():
    run_df, swim_df = load_activities()
    sleep_df = load_sleep()
    well_df = load_wellness()
    vo2_df = load_vo2max()
    race_df = load_race_predictions()
    train_df = load_training_history()
    acwr_df = compute_acwr(train_df)
    return run_df, swim_df, sleep_df, well_df, vo2_df, race_df, train_df, acwr_df


run_df, swim_df, sleep_df, well_df, vo2_df, race_df, train_df, acwr_df = load_all()


# ---------------------------------------------------------------------------
# Sidebar — date range & navigation
# ---------------------------------------------------------------------------

st.sidebar.title("🏃 Garmin Analytics")
st.sidebar.markdown("**Athlete:** Nesi Haver · 47yr · 70kg")
st.sidebar.divider()

date_options = {
    "Last 30 days":  30,
    "Last 90 days":  90,
    "Last 6 months": 180,
    "Last 12 months":365,
    "All time":      None,
}
range_label = st.sidebar.selectbox("Date Range", list(date_options.keys()), index=1)
days = date_options[range_label]

data_end = pd.Timestamp.now().normalize()
data_start = (data_end - pd.Timedelta(days=days)) if days else pd.Timestamp("2020-01-01")

st.sidebar.divider()
st.sidebar.caption("Data source: Garmin Connect exports")


# ---------------------------------------------------------------------------
# Filter all data to selected range
# ---------------------------------------------------------------------------

def f(df):
    return filter_dates(df, data_start, data_end)

run_f    = f(run_df)
swim_f   = f(swim_df)
sleep_f  = f(sleep_df)
well_f   = f(well_df)
vo2_f    = f(vo2_df)
race_f   = f(race_df)
train_f  = f(train_df)
acwr_f   = f(acwr_df)


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tabs = st.tabs([
    "📊 Overview",
    "🏃 Running",
    "🏊 Swimming",
    "😴 Sleep",
    "💪 Fitness & Recovery",
    "🔗 Cross-Pillar",
    "🤖 AI Recommendations",
])


# ── Tab 1: Overview ──────────────────────────────────────────────────────────
with tabs[0]:
    st.header("Overview")

    # KPI cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        runs = len(run_f)
        st.metric("Running Sessions", runs)
    with c2:
        swims = len(swim_f)
        st.metric("Swim Sessions", swims)
    with c3:
        avg_sleep = sleep_f["total_sleep_h"].mean() if not sleep_f.empty else 0
        st.metric("Avg Sleep", f"{avg_sleep:.1f}h",
                  delta="✓ Good" if avg_sleep >= 7 else "⚠ Low",
                  delta_color="normal" if avg_sleep >= 7 else "inverse")
    with c4:
        cur_vo2 = vo2_f["vo2max"].iloc[-1] if not vo2_f.empty else "—"
        st.metric("VO2Max", f"{cur_vo2:.0f}" if cur_vo2 != "—" else "—")
    with c5:
        cur_acwr = acwr_f["acwr"].iloc[-1] if not acwr_f.empty else None
        zone = acwr_f["risk_zone"].iloc[-1] if not acwr_f.empty else "—"
        acwr_delta_color = "inverse" if zone == "Injury Risk" else "normal"
        st.metric("ACWR", f"{cur_acwr:.2f}" if cur_acwr else "—",
                  delta=zone, delta_color=acwr_delta_color)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        vol = combined_weekly_volume(run_f, swim_f)
        if not vol.empty:
            st.plotly_chart(weekly_volume_bar(vol), use_container_width=True)
        else:
            st.info("No training data for this period.")

    with col2:
        if not well_f.empty:
            st.plotly_chart(resting_hr_trend(well_f), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        if not well_f.empty:
            st.plotly_chart(steps_trend_bar(well_f), use_container_width=True)
    with col4:
        if not acwr_f.empty:
            st.plotly_chart(acwr_chart(acwr_f.tail(365)), use_container_width=True)


# ── Tab 2: Running ───────────────────────────────────────────────────────────
with tabs[1]:
    st.header("Running")

    if run_f.empty:
        st.info("No running data for this period.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Sessions", len(run_f))
        with c2:
            st.metric("Total Distance", f"{run_f['distance_km'].sum():.0f} km")
        with c3:
            avg_pace = run_f["pace_min_per_km"].mean()
            m, s = int(avg_pace), int((avg_pace % 1) * 60)
            st.metric("Avg Pace", f"{m}:{s:02d} /km")
        with c4:
            st.metric("Avg HR", f"{run_f['avg_hr'].mean():.0f} bpm" if run_f["avg_hr"].notna().any() else "—")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(pace_trend_line(run_f), use_container_width=True)
        with col2:
            st.plotly_chart(distance_trend_line(run_f, "Running"), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(cadence_trend_line(run_f), use_container_width=True)
        with col4:
            st.plotly_chart(hr_distribution_scatter(run_f, pd.DataFrame()), use_container_width=True)

        st.subheader("Race Predictions (Garmin Estimates)")
        if not race_f.empty:
            latest = race_f.iloc[-1]
            rc1, rc2, rc3, rc4 = st.columns(4)
            for col_w, col_d, label in [
                (rc1, "5k_fmt",       "5K"),
                (rc2, "10k_fmt",      "10K"),
                (rc3, "half_fmt",     "Half Marathon"),
                (rc4, "marathon_fmt", "Marathon"),
            ]:
                val = latest.get(col_d, "—")
                col_w.metric(label, val)
            st.plotly_chart(race_predictions_line(race_f), use_container_width=True)


# ── Tab 3: Swimming ───────────────────────────────────────────────────────────
with tabs[2]:
    st.header("Swimming")

    if swim_f.empty:
        st.info("No swimming data for this period.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Sessions", len(swim_f))
        with c2:
            st.metric("Total Distance", f"{swim_f['distance_m'].sum()/1000:.1f} km")
        with c3:
            st.metric("Avg Session", f"{swim_f['duration_min'].mean():.0f} min")
        with c4:
            avg_swolf = swim_f["avg_swolf"].dropna()
            st.metric("Avg SWOLF", f"{avg_swolf.mean():.1f}" if not avg_swolf.empty else "—")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(distance_trend_line(swim_f, "Swimming"), use_container_width=True)
        with col2:
            st.plotly_chart(swolf_trend_line(swim_f), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(hr_distribution_scatter(pd.DataFrame(), swim_f), use_container_width=True)
        with col4:
            # Calories per session
            import plotly.express as px
            fig_cal = px.bar(swim_f, x="date", y="calories", color_discrete_sequence=["#2196F3"],
                             title="Swimming Calories Per Session", labels={"calories": "Calories (kcal)"})
            st.plotly_chart(fig_cal, use_container_width=True)


# ── Tab 4: Sleep ─────────────────────────────────────────────────────────────
with tabs[3]:
    st.header("Sleep")

    if sleep_f.empty:
        st.info("No sleep data for this period.")
    else:
        avg_h  = sleep_f["total_sleep_h"].mean()
        avg_dp = sleep_f["deep_pct"].mean()
        avg_rp = sleep_f["rem_pct"].mean()
        nights_low = (sleep_f["total_sleep_h"] < 7).sum()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Avg Sleep", f"{avg_h:.1f}h",
                      delta="Good" if avg_h >= 7 else "⚠ Under 7h",
                      delta_color="normal" if avg_h >= 7 else "inverse")
        with c2:
            st.metric("Avg Deep Sleep", f"{avg_dp:.1f}%",
                      delta="✓" if avg_dp >= 15 else "⚠ Low (<15%)",
                      delta_color="normal" if avg_dp >= 15 else "inverse")
        with c3:
            st.metric("Avg REM Sleep", f"{avg_rp:.1f}%",
                      delta="✓" if avg_rp >= 20 else "⚠ Low (<20%)",
                      delta_color="normal" if avg_rp >= 20 else "inverse")
        with c4:
            st.metric("Nights < 7h", nights_low,
                      delta=f"{100*nights_low/len(sleep_f):.0f}% of nights",
                      delta_color="inverse" if nights_low > 0 else "normal")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(sleep_duration_bar(sleep_f), use_container_width=True)
        with col2:
            st.plotly_chart(sleep_stages_stacked_bar(sleep_f), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(sleep_stage_pct_line(sleep_f), use_container_width=True)
        with col4:
            st.plotly_chart(respiration_trend(sleep_f), use_container_width=True)

        # Alerts
        alerts = []
        if avg_h < 7:
            alerts.append(f"⚠️ Average sleep ({avg_h:.1f}h) is below the 7h minimum. Target 8–8.5h for peak recovery.")
        if avg_dp < 10:
            alerts.append(f"🔴 Deep sleep ({avg_dp:.1f}%) is critically low. Deep sleep is when physical repair occurs.")
        if avg_rp < 15:
            alerts.append(f"⚠️ REM sleep ({avg_rp:.1f}%) is below target. REM is critical for recovery and performance consolidation.")
        if nights_low > len(sleep_f) * 0.4:
            alerts.append(f"🔴 {nights_low} nights under 7h in this period ({100*nights_low/len(sleep_f):.0f}%). This is a significant recovery deficit.")

        if alerts:
            st.subheader("Sleep Alerts")
            for a in alerts:
                st.warning(a)


# ── Tab 5: Fitness & Recovery ─────────────────────────────────────────────────
with tabs[4]:
    st.header("Fitness & Recovery")

    col1, col2 = st.columns(2)
    with col1:
        if not vo2_f.empty:
            st.plotly_chart(vo2max_trend_line(vo2_f), use_container_width=True)
        else:
            st.info("No VO2Max data for this period.")
    with col2:
        if not acwr_f.empty:
            st.plotly_chart(acwr_chart(acwr_f), use_container_width=True)
        else:
            st.info("No ACWR data.")

    col3, col4 = st.columns(2)
    with col3:
        if not well_f.empty:
            well_w = wellness_weekly(well_f)
            st.plotly_chart(intensity_minutes_bar(well_w), use_container_width=True)
    with col4:
        if not well_f.empty:
            st.plotly_chart(resting_hr_trend(well_f), use_container_width=True)

    # Training Status table
    if not train_f.empty:
        st.subheader("Recent Training Status")
        status_df = (
            train_f[train_f["training_status"] != "NO_STATUS"]
            .groupby(["date", "training_status"])
            .first()
            .reset_index()
            [["date", "sport", "training_status", "weekly_load"]]
            .tail(20)
            .sort_values("date", ascending=False)
        )
        if not status_df.empty:
            st.dataframe(status_df, use_container_width=True, hide_index=True)


# ── Tab 6: Cross-Pillar ───────────────────────────────────────────────────────
with tabs[5]:
    st.header("Cross-Pillar Correlations")
    st.caption("Exploring how sleep, fitness, and training interact.")

    col1, col2 = st.columns(2)
    with col1:
        merged = sleep_vs_next_load(sleep_f, train_f)
        if not merged.empty:
            st.plotly_chart(sleep_vs_load_scatter(merged), use_container_width=True)
        else:
            st.info("Not enough overlapping sleep + training data.")
    with col2:
        if not well_f.empty and not vo2_f.empty:
            st.plotly_chart(resting_hr_vs_vo2max(well_f, vo2_f), use_container_width=True)

    # Sleep score vs weekly run volume
    if not sleep_f.empty and not run_f.empty:
        sleep_w = sleep_weekly_score(sleep_f)
        run_w   = running_weekly(run_f)
        merged2 = sleep_w.merge(run_w, on="week", how="inner", suffixes=("_sleep","_run"))
        if not merged2.empty:
            import plotly.express as px
            fig = px.scatter(
                merged2,
                x="sleep_score",
                y="total_km",
                size="nights",
                color="avg_deep_pct",
                color_continuous_scale="Blues",
                title="Weekly Sleep Quality Score vs Running Volume",
                labels={
                    "sleep_score": "Weekly Sleep Score (0–100)",
                    "total_km": "Weekly Running km",
                    "avg_deep_pct": "Deep Sleep %",
                },
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)


# ── Tab 7: AI Recommendations ─────────────────────────────────────────────────
with tabs[6]:
    st.header("AI Recommendations")
    st.markdown(
        "Claude AI analyzes your Garmin data **against your personal sports science knowledge base** "
        "(Swimming, Running, and Sleep expertise documents) to generate grounded, personalized recommendations."
    )

    ai_days = st.selectbox("Analysis window", [30, 60, 90], index=2,
                           format_func=lambda x: f"Last {x} days")

    if st.button("Generate Personalized Analysis", type="primary"):
        with st.spinner("Analyzing your data and generating recommendations..."):
            result = generate_insights(
                run_df=run_f,
                swim_df=swim_f,
                sleep_df=sleep_f,
                well_df=well_f,
                vo2_df=vo2_f,
                race_df=race_f,
                acwr_df=acwr_f,
                days=ai_days,
            )
        st.markdown("---")
        st.markdown(result)
    else:
        st.info(
            "Click **Generate Personalized Analysis** to receive a 4-section AI analysis:\n\n"
            "1. **Training Load Assessment** — ACWR and injury risk\n"
            "2. **Running Analysis** — pace, cadence, race predictions\n"
            "3. **Swimming Analysis** — session consistency, SWOLF, HR zones\n"
            "4. **Sleep & Recovery** — stage quality, behavioral recommendations"
        )
        st.caption("Requires `ANTHROPIC_API_KEY` in your `.env` file.")
