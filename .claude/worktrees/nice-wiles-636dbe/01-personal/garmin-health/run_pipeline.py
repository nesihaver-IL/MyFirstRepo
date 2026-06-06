#!/usr/bin/env python3
"""
Garmin Health Insight Pipeline — CLI entry point.

Usage:
    python run_pipeline.py              # last 90 days (default)
    python run_pipeline.py --days 30
    python run_pipeline.py --days 180

Output:
    data/exports/health-report-YYYY-MM-DD.md
    data/exports/health-report-YYYY-MM-DD.html
"""

import argparse
import logging
import sys
from pathlib import Path

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("pipeline")

# ── Load .env before anything imports anthropic ───────────────────────────────
_ENV_FILE = Path(__file__).parent / ".env"
if _ENV_FILE.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_ENV_FILE)
    except ImportError:
        pass  # python-dotenv not installed — env vars must be set in shell


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a Garmin health insight report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Output: data/exports/health-report-<date>.html",
    )
    parser.add_argument(
        "--days", type=int, default=90,
        help="Number of days to include in the analysis window (default: 90)"
    )
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Garmin Health Pipeline  |  Last {args.days} days")
    print(f"{'='*60}")

    try:
        from agent.orchestrator import GarminHealthOrchestrator
    except Exception as e:
        logger.error(f"Failed to load pipeline: {e}")
        return 1

    try:
        print("\n⏳ Loading data...")
        # Orchestrator prints its own sub-step logs via logging
        orchestrator = GarminHealthOrchestrator()

        print("⏳ Checking alerts...")
        print("⏳ Running AI analysis  (this may take ~15s)...")
        print("⏳ Writing report...")

        result = orchestrator.run(days=args.days)

    except FileNotFoundError as e:
        print(f"\n❌ Data file not found: {e}")
        print("   Ensure Garmin JSON files are in 01-personal/aws-ai-agent/docs/")
        return 1
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        logger.exception("Unhandled error")
        return 1

    # ── Print alert summary ───────────────────────────────────────────────────
    alerts = result["alerts"]
    print(f"\n── Alerts ({len(alerts)}) ──────────────────────────────────────")
    if alerts:
        for alert in alerts:
            print(f"  {alert}")
    else:
        print("  ✅ No alerts — all metrics within target ranges.")

    # ── Print output paths ────────────────────────────────────────────────────
    paths = result["paths"]
    print(f"\n── Report saved ────────────────────────────────────────────")
    print(f"  📄 Markdown : {paths['md']}")
    print(f"  🌐 HTML     : {paths['html']}")
    print(f"\n  Open in browser:\n  file://{paths['html']}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
