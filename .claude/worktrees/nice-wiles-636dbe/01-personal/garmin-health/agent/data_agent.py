"""
DataAgent — loads all 6 Garmin JSON files and returns a DataBundle.

Imports from analytics/src/ (data_loader + metrics) by inserting
garmin-health/ root into sys.path so the analytics package is importable.
"""

import sys
import logging
from pathlib import Path

# Make analytics/ importable when run from garmin-health/ root
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from analytics.src import data_loader, metrics
from agent.models import DataBundle

logger = logging.getLogger(__name__)


class DataAgent:
    """Loads and validates all Garmin data into a DataBundle."""

    def run(self, days: int = 90) -> DataBundle:
        logger.info("DataAgent: loading data...")

        run_df, swim_df = data_loader.load_activities()
        sleep_df        = data_loader.load_sleep()
        well_df         = data_loader.load_wellness()
        vo2_df          = data_loader.load_vo2max()
        race_df         = data_loader.load_race_predictions()
        train_df        = data_loader.load_training_history()
        acwr_df         = metrics.compute_acwr(train_df)

        bundle = DataBundle(
            run_df=run_df,
            swim_df=swim_df,
            sleep_df=sleep_df,
            well_df=well_df,
            vo2_df=vo2_df,
            race_df=race_df,
            train_df=train_df,
            acwr_df=acwr_df,
            days_back=days,
        )

        self._warn_empty(bundle)
        logger.info(f"DataAgent: loaded — {bundle.summary()}")
        return bundle

    def _warn_empty(self, bundle: DataBundle) -> None:
        checks = {
            "running sessions": bundle.run_df,
            "swimming sessions": bundle.swim_df,
            "sleep records": bundle.sleep_df,
            "wellness records": bundle.well_df,
            "VO2Max records": bundle.vo2_df,
            "ACWR rows": bundle.acwr_df,
        }
        for label, df in checks.items():
            if df.empty:
                logger.warning(f"DataAgent: no {label} found")
