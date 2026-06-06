"""
GarminHealthOrchestrator — sequences all 4 pipeline agents.
"""

import logging

from agent.data_agent     import DataAgent
from agent.alert_agent    import AlertAgent
from agent.analysis_agent import AnalysisAgent
from agent.report_agent   import ReportAgent

logger = logging.getLogger(__name__)


class GarminHealthOrchestrator:
    """
    Runs the full Garmin health insight pipeline:
      DataAgent → AlertAgent → AnalysisAgent → ReportAgent
    """

    def run(self, days: int = 90) -> dict:
        """
        Execute the pipeline.

        Args:
            days: Number of days to include in the analysis window.

        Returns:
            dict with keys:
              "alerts" — List[Alert]
              "paths"  — {"md": str, "html": str}
        """
        bundle   = DataAgent().run(days=days)
        alerts   = AlertAgent().run(bundle)
        analysis = AnalysisAgent().run(bundle, days=days)
        paths    = ReportAgent().run(bundle, alerts, analysis, days=days)

        return {"alerts": alerts, "paths": paths}
