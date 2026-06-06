"""
ReportAgent — assembles Markdown and HTML health reports.

Writes two files to data/exports/:
  health-report-YYYY-MM-DD.md
  health-report-YYYY-MM-DD.html

Returns a dict with paths to both files.
"""

import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agent.models import Alert, DataBundle

logger = logging.getLogger(__name__)

EXPORTS_DIR = _ROOT / "data" / "exports"


class ReportAgent:
    """Assembles DataBundle + alerts + analysis text into dated report files."""

    def run(self, bundle: DataBundle, alerts: List[Alert], analysis: str, days: int) -> dict:
        logger.info("ReportAgent: assembling report...")
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

        today   = datetime.now().strftime("%Y-%m-%d")
        gen_at  = datetime.now().strftime("%Y-%m-%d %H:%M")
        metrics = self._build_metrics_rows(bundle, days)

        md_path   = EXPORTS_DIR / f"health-report-{today}.md"
        html_path = EXPORTS_DIR / f"health-report-{today}.html"

        md_text   = self._render_markdown(bundle, alerts, analysis, metrics, days, gen_at)
        html_text = self._render_html(alerts, analysis, metrics, days, today, gen_at)

        md_path.write_text(md_text, encoding="utf-8")
        html_path.write_text(html_text, encoding="utf-8")

        logger.info(f"ReportAgent: wrote {html_path}")
        return {"md": str(md_path), "html": str(html_path)}

    # -----------------------------------------------------------------------
    # Metrics table rows
    # -----------------------------------------------------------------------
    def _build_metrics_rows(self, bundle: DataBundle, days: int) -> list:
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
        rows   = []

        # ── Running ──────────────────────────────────────────────────────────
        r = bundle.run_df[bundle.run_df["date"] >= cutoff] if not bundle.run_df.empty else pd.DataFrame()
        if not r.empty:
            rows.append({"pillar": "Running", "metric": "Sessions",
                         "value": str(len(r)), "context": ""})
            km = r["distance_km"].sum()
            rows.append({"pillar": "Running", "metric": "Total distance",
                         "value": f"{km:.1f} km", "context": ""})
            if r["pace_min_per_km"].notna().any():
                pace = r["pace_min_per_km"].mean()
                m, s = int(pace), int((pace % 1) * 60)
                rows.append({"pillar": "Running", "metric": "Avg pace",
                             "value": f"{m}:{s:02d} min/km", "context": ""})
            if r["avg_hr"].notna().any():
                rows.append({"pillar": "Running", "metric": "Avg HR",
                             "value": f"{r['avg_hr'].mean():.0f} bpm", "context": ""})

        # ── Swimming ─────────────────────────────────────────────────────────
        s = bundle.swim_df[bundle.swim_df["date"] >= cutoff] if not bundle.swim_df.empty else pd.DataFrame()
        if not s.empty:
            rows.append({"pillar": "Swimming", "metric": "Sessions",
                         "value": str(len(s)), "context": ""})
            avg_dist = s["distance_m"].mean()
            rows.append({"pillar": "Swimming", "metric": "Avg session distance",
                         "value": f"{avg_dist:.0f} m", "context": "Goal: 2,000 m"})
            if s["avg_hr"].notna().any():
                rows.append({"pillar": "Swimming", "metric": "Avg HR",
                             "value": f"{s['avg_hr'].mean():.0f} bpm", "context": ""})

        # ── Sleep ─────────────────────────────────────────────────────────────
        sl = bundle.sleep_df[bundle.sleep_df["date"] >= cutoff] if not bundle.sleep_df.empty else pd.DataFrame()
        if not sl.empty:
            rows.append({"pillar": "Sleep", "metric": "Avg duration",
                         "value": f"{sl['total_sleep_h'].mean():.1f} h",
                         "context": "Target: 7–9 h"})
            rows.append({"pillar": "Sleep", "metric": "Avg deep sleep",
                         "value": f"{sl['deep_pct'].mean():.1f}%",
                         "context": "Target: >15%"})
            rows.append({"pillar": "Sleep", "metric": "Avg REM sleep",
                         "value": f"{sl['rem_pct'].mean():.1f}%",
                         "context": "Target: >20%"})
            nights_low = int((sl["total_sleep_h"] < 7).sum())
            if nights_low:
                rows.append({"pillar": "Sleep", "metric": "Nights < 7 h",
                             "value": str(nights_low),
                             "context": f"out of {len(sl)} tracked nights"})

        # ── Fitness ───────────────────────────────────────────────────────────
        v = bundle.vo2_df[bundle.vo2_df["date"] >= cutoff] if not bundle.vo2_df.empty else pd.DataFrame()
        if not v.empty and v["vo2max"].notna().any():
            latest_vo2 = v["vo2max"].dropna().iloc[-1]
            rows.append({"pillar": "Fitness", "metric": "VO2Max",
                         "value": f"{latest_vo2:.0f} ml/kg/min", "context": ""})
            fa = v["fitness_age"].dropna()
            if not fa.empty:
                rows.append({"pillar": "Fitness", "metric": "Fitness Age",
                             "value": f"{fa.iloc[-1]:.0f} years",
                             "context": "Chronological: 47"})

        if not bundle.acwr_df.empty:
            latest_acwr = bundle.acwr_df.dropna(subset=["acwr"]).iloc[-1]
            rows.append({"pillar": "Fitness", "metric": "ACWR",
                         "value": str(round(float(latest_acwr["acwr"]), 2)),
                         "context": f"Zone: {latest_acwr['risk_zone']} (target 0.8–1.3)"})

        return rows

    # -----------------------------------------------------------------------
    # Markdown render
    # -----------------------------------------------------------------------
    def _render_markdown(self, bundle, alerts, analysis, metrics, days, gen_at) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        lines = [
            f"# Garmin Health Report — {today}",
            f"**Analysis period**: Last {days} days  |  **Generated**: {gen_at}",
            "",
            "---",
            "",
            "## Alerts",
            "",
        ]

        if alerts:
            lines.append("| Severity | Alert |")
            lines.append("|----------|-------|")
            for a in alerts:
                lines.append(f"| {a.emoji()} {a.severity} | {a.message} |")
        else:
            lines.append("✅ No alerts — all metrics within target ranges.")

        lines += ["", "---", "", "## Key Metrics Snapshot", "",
                  f"Last {days} days.", "",
                  "| Pillar | Metric | Value | Context |",
                  "|--------|--------|-------|---------|"]

        for row in metrics:
            lines.append(
                f"| {row['pillar']} | {row['metric']} | {row['value']} | {row['context']} |"
            )

        lines += ["", "---", "", "## AI Analysis", "", analysis, "",
                  "---",
                  f"*Generated by Garmin Health Pipeline | Model: claude-sonnet-4-6*"]

        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # HTML render via Jinja2
    # -----------------------------------------------------------------------
    def _render_html(self, alerts, analysis, metrics, days, today, gen_at) -> str:
        try:
            from jinja2 import Environment, FileSystemLoader
        except ImportError:
            logger.error("jinja2 not installed — pip install jinja2")
            return f"<pre>jinja2 not installed. Install with: pip install jinja2\n\n{analysis}</pre>"

        try:
            import markdown as md_lib
            analysis_html = md_lib.markdown(analysis, extensions=["nl2br"])
        except ImportError:
            # Fallback: simple newline → <br> conversion
            analysis_html = self._simple_md_to_html(analysis)

        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
        template = env.get_template("report.html.jinja2")

        return template.render(
            report_date=today,
            generated_at=gen_at,
            days=days,
            alerts=alerts,
            metrics_rows=metrics,
            analysis_html=analysis_html,
        )

    def _simple_md_to_html(self, text: str) -> str:
        """Minimal Markdown → HTML when the markdown library is unavailable."""
        html = text
        # h3
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        # h2
        html = re.sub(r'^## (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        # bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        # bullets
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        # paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f"<p>{html}</p>"
        return html
