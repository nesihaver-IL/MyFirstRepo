"""
AlertAgent — pure data threshold checks. No AI involved.

Every alert is deterministic: reads numbers from DataBundle,
compares against defined thresholds, returns List[Alert].
Alerts are ordered RED → YELLOW → INFO.
"""

import logging
from datetime import datetime, timedelta
from typing import List

import pandas as pd

from agent.models import Alert, DataBundle

logger = logging.getLogger(__name__)

# --- Thresholds ---
ACWR_INJURY_RISK  = 1.5
ACWR_CAUTION      = 1.3
ACWR_UNDERTRAINING = 0.8

SLEEP_CRITICAL_H   = 6.5   # avg hours last 7 nights
SLEEP_LOW_H        = 7.0
SLEEP_DEEP_CRITICAL = 8.0  # avg deep% last 7 nights
SLEEP_DEEP_LOW      = 12.0

RUN_GAP_RED_DAYS  = 21
RUN_GAP_YELLOW_DAYS = 10
SWIM_GAP_INFO_DAYS  = 14

VO2MAX_DROP_THRESHOLD = 2.0  # ml/kg/min decline in 30 days
VO2MAX_RISE_THRESHOLD = 1.0


class AlertAgent:
    """Scans DataBundle against health thresholds and returns a sorted List[Alert]."""

    def run(self, bundle: DataBundle) -> List[Alert]:
        logger.info("AlertAgent: checking thresholds...")
        alerts: List[Alert] = []

        alerts.extend(self._check_acwr(bundle.acwr_df))
        alerts.extend(self._check_sleep(bundle.sleep_df))
        alerts.extend(self._check_training_gaps(bundle.run_df, bundle.swim_df))
        alerts.extend(self._check_vo2max(bundle.vo2_df))

        # Sort: RED first, then YELLOW, then INFO
        order = {"RED": 0, "YELLOW": 1, "INFO": 2}
        alerts.sort(key=lambda a: order.get(a.severity, 3))

        logger.info(f"AlertAgent: {len(alerts)} alerts "
                    f"({sum(1 for a in alerts if a.severity=='RED')} red, "
                    f"{sum(1 for a in alerts if a.severity=='YELLOW')} yellow, "
                    f"{sum(1 for a in alerts if a.severity=='INFO')} info)")
        return alerts

    # -----------------------------------------------------------------------
    # ACWR
    # -----------------------------------------------------------------------
    def _check_acwr(self, acwr_df: pd.DataFrame) -> List[Alert]:
        if acwr_df.empty:
            return [Alert("INFO", "ACWR", "No training load data available for ACWR calculation.")]

        latest = acwr_df.dropna(subset=["acwr"]).iloc[-1]
        val = round(float(latest["acwr"]), 2)

        if val > ACWR_INJURY_RISK:
            return [Alert("RED", "ACWR",
                f"Injury risk: ACWR {val}. Acute load is {val:.0%} of chronic baseline. "
                "Reduce training volume immediately.")]
        if val > ACWR_CAUTION:
            return [Alert("YELLOW", "ACWR",
                f"Elevated training load: ACWR {val} (caution zone 1.3–1.5). "
                "Monitor fatigue closely.")]
        if val < ACWR_UNDERTRAINING:
            return [Alert("YELLOW", "ACWR",
                f"Detraining risk: ACWR {val} (below 0.8). "
                "Consider gradually increasing training load.")]
        return [Alert("INFO", "ACWR",
            f"Training load is in the optimal zone (ACWR {val}, target 0.8–1.3).")]

    # -----------------------------------------------------------------------
    # Sleep — checks last 7 nights
    # -----------------------------------------------------------------------
    def _check_sleep(self, sleep_df: pd.DataFrame) -> List[Alert]:
        if sleep_df.empty:
            return [Alert("INFO", "SLEEP", "No sleep data available.")]

        cutoff = pd.Timestamp.now() - pd.Timedelta(days=7)
        recent = sleep_df[sleep_df["date"] >= cutoff]

        if recent.empty:
            return [Alert("INFO", "SLEEP", "No sleep data in the last 7 days.")]

        alerts = []
        avg_h    = round(float(recent["total_sleep_h"].mean()), 1)
        avg_deep = round(float(recent["deep_pct"].mean()), 1)

        # Duration checks
        if avg_h < SLEEP_CRITICAL_H:
            alerts.append(Alert("RED", "SLEEP",
                f"Critical sleep deficit: avg {avg_h}h over last 7 nights "
                f"(minimum target: 7h). Recovery is significantly impaired."))
        elif avg_h < SLEEP_LOW_H:
            alerts.append(Alert("YELLOW", "SLEEP",
                f"Below sleep target: avg {avg_h}h over last 7 nights. "
                "Aim for 7–9h nightly for optimal recovery."))

        # Deep sleep checks
        if avg_deep < SLEEP_DEEP_CRITICAL:
            alerts.append(Alert("RED", "SLEEP",
                f"Very low deep sleep: {avg_deep}% avg over last 7 nights "
                f"(target >15%). Sleep architecture is compromised."))
        elif avg_deep < SLEEP_DEEP_LOW:
            alerts.append(Alert("YELLOW", "SLEEP",
                f"Low deep sleep: {avg_deep}% avg over last 7 nights "
                f"(target >15%). Review sleep hygiene and training load."))

        if not alerts:
            alerts.append(Alert("INFO", "SLEEP",
                f"Sleep is within acceptable range (avg {avg_h}h, deep {avg_deep}%)."))

        return alerts

    # -----------------------------------------------------------------------
    # Training gaps
    # -----------------------------------------------------------------------
    def _check_training_gaps(self, run_df: pd.DataFrame, swim_df: pd.DataFrame) -> List[Alert]:
        alerts = []
        today = pd.Timestamp.now().normalize()

        # Running gap
        if run_df.empty:
            alerts.append(Alert("YELLOW", "TRAINING_GAP",
                "No running sessions found in dataset."))
        else:
            last_run = run_df["date"].max()
            gap_days = (today - last_run).days
            if gap_days >= RUN_GAP_RED_DAYS:
                alerts.append(Alert("RED", "TRAINING_GAP",
                    f"No running in {gap_days} days. Significant detraining risk."))
            elif gap_days >= RUN_GAP_YELLOW_DAYS:
                alerts.append(Alert("YELLOW", "TRAINING_GAP",
                    f"Running gap: last session {gap_days} days ago."))

        # Swimming gap
        if swim_df.empty:
            alerts.append(Alert("INFO", "TRAINING_GAP",
                "No swimming sessions found in dataset."))
        else:
            last_swim = swim_df["date"].max()
            swim_gap = (today - last_swim).days
            if swim_gap >= SWIM_GAP_INFO_DAYS:
                alerts.append(Alert("INFO", "TRAINING_GAP",
                    f"No swimming in {swim_gap} days."))

        return alerts

    # -----------------------------------------------------------------------
    # VO2Max trend — last 30 days
    # -----------------------------------------------------------------------
    def _check_vo2max(self, vo2_df: pd.DataFrame) -> List[Alert]:
        if vo2_df.empty or vo2_df["vo2max"].dropna().empty:
            return []

        cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)
        recent = vo2_df[vo2_df["date"] >= cutoff].dropna(subset=["vo2max"])

        if len(recent) < 2:
            return []

        first_val = round(float(recent["vo2max"].iloc[0]), 1)
        last_val  = round(float(recent["vo2max"].iloc[-1]), 1)
        delta     = last_val - first_val

        if delta <= -VO2MAX_DROP_THRESHOLD:
            return [Alert("YELLOW", "VO2MAX",
                f"VO2Max declined from {first_val} to {last_val} ml/kg/min "
                f"over last 30 days. Check training quality and recovery.")]
        if delta >= VO2MAX_RISE_THRESHOLD:
            return [Alert("INFO", "VO2MAX",
                f"VO2Max improving: {first_val} → {last_val} ml/kg/min over last 30 days.")]
        return []
