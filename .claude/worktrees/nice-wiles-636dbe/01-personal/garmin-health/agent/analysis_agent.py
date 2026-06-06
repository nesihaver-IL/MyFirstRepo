"""
AnalysisAgent — wraps ai_insights.generate_insights().

Unpacks DataBundle into the 7 DataFrames that generate_insights expects,
calls the Claude API, and returns the 4-section text.

Gracefully degrades: if ANTHROPIC_API_KEY is absent or the call fails,
returns a message string so the report still renders (no pipeline crash).
"""

import logging
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agent.models import DataBundle

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """Generates a 4-section AI analysis via Claude API."""

    def run(self, bundle: DataBundle, days: int = 90) -> str:
        logger.info("AnalysisAgent: calling Claude API...")

        try:
            from analytics.src.ai_insights import generate_insights
        except ImportError as e:
            msg = f"Could not import ai_insights: {e}"
            logger.error(msg)
            return f"⚠️ AI analysis unavailable: {msg}"

        try:
            result = generate_insights(
                run_df=bundle.run_df,
                swim_df=bundle.swim_df,
                sleep_df=bundle.sleep_df,
                well_df=bundle.well_df,
                vo2_df=bundle.vo2_df,
                race_df=bundle.race_df,
                acwr_df=bundle.acwr_df,
                days=days,
            )
            logger.info("AnalysisAgent: analysis complete")
            return result

        except Exception as e:
            msg = str(e)
            if "ANTHROPIC_API_KEY" in msg or "api_key" in msg.lower():
                logger.warning("AnalysisAgent: API key not set")
                return (
                    "⚠️ AI analysis unavailable — ANTHROPIC_API_KEY not set.\n\n"
                    "To enable AI insights:\n"
                    "1. Copy `analytics/.env.example` to `.env`\n"
                    "2. Add: `ANTHROPIC_API_KEY=sk-ant-...`\n"
                    "3. Re-run: `python run_pipeline.py`"
                )
            logger.error(f"AnalysisAgent: API call failed: {e}")
            return f"⚠️ AI analysis failed: {msg}"
