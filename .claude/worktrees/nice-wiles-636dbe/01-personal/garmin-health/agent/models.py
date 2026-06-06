"""
Shared data models for the Garmin Health pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import pandas as pd


@dataclass
class Alert:
    """A single health alert produced by AlertAgent."""
    severity: str      # "RED" | "YELLOW" | "INFO"
    category: str      # "ACWR" | "SLEEP" | "TRAINING_GAP" | "VO2MAX"
    message: str

    def emoji(self) -> str:
        return {"RED": "🔴", "YELLOW": "🟡", "INFO": "🔵"}.get(self.severity, "⚪")

    def __str__(self) -> str:
        return f"{self.emoji()} [{self.severity}] {self.message}"


@dataclass
class DataBundle:
    """
    All normalised DataFrames loaded from the 6 Garmin JSON files,
    plus derived metrics (ACWR). Passed between pipeline agents.
    """
    run_df: pd.DataFrame
    swim_df: pd.DataFrame
    sleep_df: pd.DataFrame
    well_df: pd.DataFrame
    vo2_df: pd.DataFrame
    race_df: pd.DataFrame
    train_df: pd.DataFrame
    acwr_df: pd.DataFrame
    days_back: int
    loaded_at: datetime = field(default_factory=datetime.now)

    def summary(self) -> str:
        """One-line load summary for logging."""
        return (
            f"runs={len(self.run_df)} swims={len(self.swim_df)} "
            f"sleep={len(self.sleep_df)} wellness={len(self.well_df)} "
            f"vo2max={len(self.vo2_df)} acwr_rows={len(self.acwr_df)}"
        )
