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
    "🏆 Personal Bests",
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


# ── Tab 8: Personal Bests ──────────────────────────────────────────────────────
with tabs[7]:
    import plotly.graph_objects as go

    st.header("🏆 Personal Bests & All-Time Records")
    st.caption(
        "Peak achievements across all three pillars — **Swimming · Running · Sleep** — "
        "no date filter applied. These are your all-time records."
    )

    # ── Hero banner ───────────────────────────────────────────────────────────
    st.markdown("### All-Time Peaks")

    h1, h2, h3, h4, h5 = st.columns(5)

    with h1:
        peak_vo2 = vo2_df["vo2max"].max() if not vo2_df.empty else None
        cur_vo2  = vo2_df["vo2max"].iloc[-1] if not vo2_df.empty else None
        delta_vo2 = int(cur_vo2 - peak_vo2) if (peak_vo2 and cur_vo2) else None
        st.metric(
            "Peak VO2Max",
            f"{peak_vo2:.0f} ml/kg/min" if peak_vo2 else "—",
            delta=f"{delta_vo2:+d} vs today" if delta_vo2 is not None else None,
            delta_color="inverse",
        )

    with h2:
        fit_age = vo2_df["fitness_age"].min() if not vo2_df.empty else None
        st.metric(
            "Fitness Age",
            f"{int(fit_age)} yrs" if fit_age else "—",
            delta="vs 47 chronological",
            delta_color="normal",
        )

    with h3:
        if not race_df.empty:
            best_5k_sec = race_df["5k_sec"].min()
            bm, bs = divmod(int(best_5k_sec), 60)
            st.metric("Best 5K Prediction", f"{bm}:{bs:02d}", delta_color="off")

    with h4:
        if not swim_df.empty:
            max_swim_m = swim_df["distance_m"].max()
            pct = max_swim_m / 2000 * 100
            st.metric(
                "Longest Swim",
                f"{max_swim_m:.0f} m",
                delta=f"{pct:.0f}% of 2000m goal",
                delta_color="normal" if max_swim_m >= 2000 else "inverse",
            )

    with h5:
        if not sleep_df.empty:
            st.metric(
                "Best Sleep Night",
                f"{sleep_df['total_sleep_h'].max():.1f} h",
                delta="All-time max",
                delta_color="off",
            )

    st.divider()

    # ── SWIMMING ──────────────────────────────────────────────────────────────
    st.markdown("### 🏊 Swimming — Progress to 2000m Goal")

    sw1, sw2 = st.columns([1, 2])

    with sw1:
        if not swim_df.empty:
            avg_swim_m = swim_df["distance_m"].mean()

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=avg_swim_m,
                delta={"reference": 2000, "valueformat": ".0f", "suffix": " m vs goal"},
                number={"suffix": " m", "valueformat": ".0f", "font": {"size": 36}},
                title={"text": "Avg Session Distance", "font": {"size": 15}},
                gauge={
                    "axis": {"range": [0, 2200], "tickwidth": 1, "tickcolor": "#555"},
                    "bar": {"color": "#2196F3", "thickness": 0.3},
                    "bgcolor": "white",
                    "steps": [
                        {"range": [0,    1000], "color": "#FFF9C4"},
                        {"range": [1000, 1500], "color": "#B3E5FC"},
                        {"range": [1500, 2000], "color": "#81D4FA"},
                        {"range": [2000, 2200], "color": "#C8E6C9"},
                    ],
                    "threshold": {
                        "line": {"color": "#1A237E", "width": 4},
                        "thickness": 0.85,
                        "value": 2000,
                    },
                },
            ))
            fig_gauge.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=50, b=10),
                font=dict(family="Inter, Arial, sans-serif"),
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

            s1, s2 = st.columns(2)
            s1.metric("Sessions ≥ 1500m", int((swim_df["distance_m"] >= 1500).sum()))
            s2.metric("Sessions ≥ 1800m", int((swim_df["distance_m"] >= 1800).sum()))
            st.metric("Total Swim Sessions", len(swim_df))

    with sw2:
        if not swim_df.empty:
            top_swims = swim_df.nlargest(15, "distance_m").copy()
            top_swims["date_str"] = top_swims["date"].dt.strftime("%b %d %Y")
            top_swims["label"]    = top_swims["date_str"] + "  ·  " + top_swims["distance_m"].astype(int).astype(str) + " m"
            bar_colors = [
                "#1A237E" if d >= 2000 else "#2196F3" if d >= 1500 else "#90CAF9"
                for d in top_swims["distance_m"]
            ]

            fig_top_swim = go.Figure(go.Bar(
                x=top_swims["distance_m"],
                y=top_swims["label"],
                orientation="h",
                marker_color=bar_colors,
                text=top_swims["distance_m"].astype(int).astype(str) + " m",
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>%{x:.0f} m<extra></extra>",
            ))
            fig_top_swim.add_vline(
                x=2000, line_dash="dash", line_color="#1A237E", line_width=2,
                annotation_text="2000m Goal", annotation_position="top right",
                annotation_font=dict(color="#1A237E", size=11),
            )
            fig_top_swim.update_layout(
                template="plotly_white",
                title="Top 15 Swim Sessions — All Time",
                xaxis_title="Distance (m)",
                xaxis_range=[0, max(swim_df["distance_m"].max() * 1.15, 2100)],
                yaxis={"autorange": "reversed"},
                height=420,
                margin=dict(l=180, r=60, t=50, b=40),
                font=dict(family="Inter, Arial, sans-serif", size=12),
                showlegend=False,
            )
            st.plotly_chart(fig_top_swim, use_container_width=True)

    st.divider()

    # ── RUNNING ───────────────────────────────────────────────────────────────
    st.markdown("### 🏃 Running — Race Predictions & Records")

    rr1, rr2 = st.columns([2, 1])

    with rr1:
        if not race_df.empty:
            fig_race = go.Figure()
            for col, fmt_col, label, color in [
                ("5k_sec",   "5k_fmt",   "5K",            "#FF6B35"),
                ("half_sec", "half_fmt", "Half Marathon",  "#E91E63"),
            ]:
                d = race_df[race_df[col].notna()].copy()
                d["minutes"] = d[col] / 60
                fig_race.add_trace(go.Scatter(
                    x=d["date"],
                    y=d["minutes"],
                    name=label,
                    mode="lines",
                    line=dict(color=color, width=2.5),
                    customdata=d[fmt_col],
                    hovertemplate=(
                        f"<b>{label}</b><br>"
                        "%{x|%Y-%m-%d}<br>"
                        "Time: %{customdata}<extra></extra>"
                    ),
                ))

            # Mark best predictions
            for col, fmt_col, label, color in [
                ("5k_sec",   "5k_fmt",   "5K",            "#FF6B35"),
                ("half_sec", "half_fmt", "Half Marathon",  "#E91E63"),
            ]:
                d = race_df[race_df[col].notna()]
                if d.empty:
                    continue
                best_idx  = d[col].idxmin()
                best_row  = d.loc[best_idx]
                fig_race.add_annotation(
                    x=best_row["date"],
                    y=best_row[col] / 60,
                    text=f"🏆 {best_row[fmt_col]}",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor=color,
                    bgcolor="white",
                    bordercolor=color,
                    borderwidth=1,
                    font=dict(size=11, color=color),
                    ax=0, ay=-36,
                )

            fig_race.update_layout(
                template="plotly_white",
                title="Race Prediction Trend — All Time",
                xaxis_title="Date",
                yaxis_title="Predicted Time (minutes)",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                font=dict(family="Inter, Arial, sans-serif", size=13),
                margin=dict(l=50, r=20, t=60, b=40),
            )
            st.plotly_chart(fig_race, use_container_width=True)

    with rr2:
        st.markdown("**All-Time Running Stats**")
        if not run_df.empty:
            valid_runs = run_df[
                run_df["pace_min_per_km"].notna() &
                (run_df["pace_min_per_km"] > 2) &
                (run_df["distance_km"] >= 3)
            ]
            if not valid_runs.empty:
                best_pace = valid_runs["pace_min_per_km"].min()
                bpm2, bps2 = int(best_pace), int((best_pace % 1) * 60)
                st.metric("Best Pace (≥3km)", f"{bpm2}:{bps2:02d} /km")

            st.metric("Longest Run", f"{run_df['distance_km'].max():.1f} km")
            st.metric("Total Sessions",  len(run_df))
            st.metric("Total km Run",    f"{run_df['distance_km'].sum():.0f} km")

        if not race_df.empty:
            st.markdown("---")
            st.markdown("**Best Predicted Times**")
            for col, fmt_col, label in [
                ("5k_sec",       "5k_fmt",       "5K"),
                ("10k_sec",      "10k_fmt",      "10K"),
                ("half_sec",     "half_fmt",     "Half Marathon"),
                ("marathon_sec", "marathon_fmt", "Marathon"),
            ]:
                best = race_df.loc[race_df[col].idxmin(), fmt_col] if race_df[col].notna().any() else "—"
                st.metric(f"Best {label}", best)

    st.divider()

    # ── SLEEP ─────────────────────────────────────────────────────────────────
    st.markdown("### 😴 Sleep — Best Recovery Nights")

    if not sleep_df.empty:
        sl1, sl2, sl3 = st.columns(3)

        for col_widget, night_label, sort_col, chart_title, badge in [
            (sl1, "Best Total Sleep",  "total_sleep_h",
             lambda r: f"{r['total_sleep_h']:.1f}h Total",   "💤"),
            (sl2, "Best Deep Sleep",   "deep_min",
             lambda r: f"{r['deep_min']:.0f} min Deep",       "🧠"),
            (sl3, "Best REM Night",    "rem_min",
             lambda r: f"{r['rem_min']:.0f} min REM",         "🌙"),
        ]:
            with col_widget:
                night = sleep_df.loc[sleep_df[sort_col].idxmax()]
                st.markdown(f"**{badge} {night_label}**")
                st.caption(night["date"].strftime("%B %d, %Y"))

                fig_pie = go.Figure(go.Pie(
                    labels=["Deep", "REM", "Light"],
                    values=[night["deep_min"], night["rem_min"], night["light_min"]],
                    hole=0.45,
                    marker_colors=["#1A237E", "#7B1FA2", "#64B5F6"],
                    textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>%{value:.0f} min<extra></extra>",
                    direction="clockwise",
                ))
                fig_pie.update_layout(
                    title=dict(text=chart_title(night), font=dict(size=14)),
                    height=260,
                    margin=dict(l=10, r=10, t=50, b=10),
                    font=dict(family="Inter, Arial, sans-serif", size=12),
                    showlegend=False,
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        sa1, sa2, sa3, sa4 = st.columns(4)
        sa1.metric("Best Total Sleep",   f"{sleep_df['total_sleep_h'].max():.1f} h")
        sa2.metric("Best Deep Sleep",    f"{sleep_df['deep_min'].max():.0f} min")
        sa3.metric("Best REM Sleep",     f"{sleep_df['rem_min'].max():.0f} min")
        sa4.metric("Best Deep % Night",  f"{sleep_df['deep_pct'].max():.1f}%")

    st.divider()

    # ── VO2MAX PEAK ───────────────────────────────────────────────────────────
    st.markdown("### 💪 Fitness Peak — VO2Max All-Time History")

    if not vo2_df.empty:
        peak_row = vo2_df.loc[vo2_df["vo2max"].idxmax()]
        cur_row  = vo2_df.iloc[-1]

        fig_vo2_peak = go.Figure()

        # Area fill
        fig_vo2_peak.add_trace(go.Scatter(
            x=vo2_df["date"],
            y=vo2_df["vo2max"],
            fill="tozeroy",
            fillcolor="rgba(33, 150, 243, 0.12)",
            line=dict(color="#2196F3", width=2.5),
            mode="lines",
            name="VO2Max",
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>VO2Max: %{y:.0f} ml/kg/min<extra></extra>",
        ))

        # Peak marker
        fig_vo2_peak.add_trace(go.Scatter(
            x=[peak_row["date"]],
            y=[peak_row["vo2max"]],
            mode="markers",
            marker=dict(size=14, color="#1A237E", symbol="star"),
            name="Peak",
            hovertemplate="<b>Peak</b><br>%{x|%Y-%m-%d}<br>%{y:.0f} ml/kg/min<extra></extra>",
        ))

        # Peak annotation
        fig_vo2_peak.add_annotation(
            x=peak_row["date"], y=peak_row["vo2max"],
            text=f"🏆 Peak: {peak_row['vo2max']:.0f}<br>{peak_row['date'].strftime('%b %Y')}",
            showarrow=True, arrowhead=2, arrowcolor="#1A237E",
            bgcolor="#E3F2FD", bordercolor="#1A237E", borderwidth=1,
            font=dict(size=12, color="#1A237E"),
            ax=40, ay=-45,
        )

        # Current annotation
        fig_vo2_peak.add_annotation(
            x=cur_row["date"], y=cur_row["vo2max"],
            text=f"Now: {cur_row['vo2max']:.0f}",
            showarrow=True, arrowhead=2, arrowcolor="#FF6B35",
            bgcolor="#FFF3E0", bordercolor="#FF6B35", borderwidth=1,
            font=dict(size=12, color="#FF6B35"),
            ax=-40, ay=-45,
        )

        # Excellent zone reference band
        fig_vo2_peak.add_hrect(
            y0=42, y1=56,
            fillcolor="rgba(76, 175, 80, 0.06)",
            line_width=0,
            annotation_text="Excellent range for age 47 (>42)",
            annotation_position="top left",
            annotation_font=dict(size=10, color="#4CAF50"),
        )

        fig_vo2_peak.update_layout(
            template="plotly_white",
            title="VO2Max Trend — All Time  |  Fitness Age = 20",
            xaxis_title="Date",
            yaxis_title="VO2Max (ml/kg/min)",
            yaxis=dict(range=[40, 56]),
            hovermode="x unified",
            font=dict(family="Inter, Arial, sans-serif", size=13),
            margin=dict(l=50, r=20, t=60, b=40),
            showlegend=False,
        )
        st.plotly_chart(fig_vo2_peak, use_container_width=True)

        # Summary strip
        v1, v2, v3, v4 = st.columns(4)
        v1.metric(
            "Peak VO2Max", f"{vo2_df['vo2max'].max():.0f} ml/kg/min",
            delta=f"↑{vo2_df['vo2max'].max() - vo2_df['vo2max'].iloc[0]:.0f} from first reading",
            delta_color="normal",
        )
        v2.metric(
            "Current VO2Max", f"{cur_row['vo2max']:.0f} ml/kg/min",
            delta=f"{cur_row['vo2max'] - vo2_df['vo2max'].max():.0f} from peak",
            delta_color="inverse",
        )
        v3.metric(
            "Fitness Age", f"{int(vo2_df['fitness_age'].min())} yrs",
            delta="vs 47 chronological", delta_color="normal",
        )
        v4.metric(
            "5-Year Change",
            f"{vo2_df['vo2max'].iloc[-1] - vo2_df['vo2max'].iloc[0]:+.0f} ml/kg/min",
            delta="since May 2020", delta_color="inverse",
        )
