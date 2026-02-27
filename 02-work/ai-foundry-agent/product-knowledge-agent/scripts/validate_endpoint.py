"""
validate_endpoint.py
Tests the deployed Prompt Flow endpoint by sending all 15 questions from
test_questions.txt and writing results to tests/test_results_auto.md.

Run after deploying the flow (Phase 3, Step 3.12):
    python validate_endpoint.py

Prerequisites:
    pip install -r requirements.txt
    Set PROMPT_FLOW_ENDPOINT and PROMPT_FLOW_KEY in .env

How to find the values:
    PROMPT_FLOW_ENDPOINT:
        AI Foundry → Deployments → product-knowledge-endpoint
        Copy the "REST endpoint" URL (ends in /score)
    PROMPT_FLOW_KEY:
        Same page → "Authentication" tab → Primary key
"""

import os
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── FILL THESE IN (or set in .env) ────────────────────────────────────────────
ENDPOINT_URL = os.getenv(
    "PROMPT_FLOW_ENDPOINT",
    "https://product-knowledge-endpoint.eastus2.inference.ml.azure.com/score"
)
ENDPOINT_KEY = os.getenv("PROMPT_FLOW_KEY", "YOUR_PROMPT_FLOW_PRIMARY_KEY")
# ─────────────────────────────────────────────────────────────────────────────

QUESTIONS_FILE = Path(__file__).parent.parent / "tests" / "test_questions.txt"
RESULTS_FILE   = Path(__file__).parent.parent / "tests" / "test_results_auto.md"

HEADERS = {
    "Authorization": f"Bearer {ENDPOINT_KEY}",
    "Content-Type":  "application/json",
}

REQUIRED_SECTIONS = [
    "## Answer",
    "## Business Context",
    "## Subsystem Explanation",
    "## Related Components",
]

DIAGRAM_QUESTIONS = {13, 14, 15}   # question numbers that expect a diagram


def load_questions() -> list[tuple[int, str]]:
    """Parse test_questions.txt → list of (number, question_text)."""
    questions = []
    for line in QUESTIONS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Lines like: "1. How does the payment gateway..."
        if ". " in line and line[0].isdigit():
            num_str, text = line.split(". ", 1)
            try:
                questions.append((int(num_str), text.strip()))
            except ValueError:
                continue
    return questions


def call_endpoint(question: str) -> tuple[str, float]:
    """Send one question, return (response_text, elapsed_seconds)."""
    payload = {"inputs": {"question": question}}
    start = time.time()
    try:
        resp = requests.post(ENDPOINT_URL, headers=HEADERS, json=payload, timeout=60)
        elapsed = time.time() - start
        resp.raise_for_status()
        data = resp.json()
        # Prompt Flow returns: { "outputs": { "final_response": "..." } }
        text = data.get("outputs", {}).get("final_response", "")
        if not text:
            text = str(data)  # fallback — show raw response
        return text, elapsed
    except requests.exceptions.Timeout:
        return "ERROR: Request timed out after 60 seconds", time.time() - start
    except requests.exceptions.HTTPError as e:
        return f"ERROR: HTTP {e.response.status_code} — {e.response.text[:200]}", time.time() - start
    except Exception as e:
        return f"ERROR: {str(e)}", time.time() - start


def validate_response(num: int, question: str, response: str, elapsed: float) -> dict:
    """Check response against expected criteria."""
    result = {
        "num":          num,
        "question":     question,
        "elapsed":      elapsed,
        "has_sections": all(s in response for s in REQUIRED_SECTIONS),
        "has_diagram":  "![" in response if num in DIAGRAM_QUESTIONS else None,
        "has_error":    response.startswith("ERROR:"),
        "is_colored":   None,   # can't auto-check — manual verification
        "raw_response": response,
    }

    # Time targets
    if num in DIAGRAM_QUESTIONS:
        result["time_ok"] = elapsed <= 25
        result["time_target"] = "≤ 25s"
    else:
        result["time_ok"] = elapsed <= 10
        result["time_target"] = "≤ 10s"

    result["pass"] = (
        result["has_sections"]
        and not result["has_error"]
        and result["time_ok"]
        and (result["has_diagram"] is not False)
    )

    return result


def write_results(results: list[dict]) -> None:
    passed  = sum(1 for r in results if r["pass"])
    total   = len(results)

    lines = [
        f"# Automated Test Results",
        f"",
        f"**Run date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Endpoint**: {ENDPOINT_URL}",
        f"**Result**: {passed}/{total} passed",
        f"",
        f"## Summary Table",
        f"",
        f"| # | Question (truncated) | Sections | Diagram | Time | Pass |",
        f"|---|----------------------|---------|---------|------|------|",
    ]

    for r in results:
        q_short   = r["question"][:50] + ("..." if len(r["question"]) > 50 else "")
        sections  = "✅" if r["has_sections"]    else "❌"
        diagram   = "✅" if r["has_diagram"]     else ("N/A" if r["has_diagram"] is None else "❌")
        time_cell = f"{'✅' if r['time_ok'] else '⚠️'} {r['elapsed']:.1f}s"
        passed    = "✅ PASS" if r["pass"] else "❌ FAIL"
        lines.append(f"| {r['num']} | {q_short} | {sections} | {diagram} | {time_cell} | {passed} |")

    lines += [
        f"",
        f"## Detailed Responses",
        f"",
    ]

    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        lines += [
            f"### Q{r['num']} [{status}] — {r['question']}",
            f"*Time: {r['elapsed']:.2f}s | Target: {r['time_target']}*",
            f"",
            "```",
            r["raw_response"][:1500] + ("..." if len(r["raw_response"]) > 1500 else ""),
            "```",
            f"",
        ]

    lines += [
        f"## Go / No-Go for Demo",
        f"",
        f"- {'✅' if passed == total else '❌'} All {total} questions pass",
        f"- {'✅' if any(r['has_diagram'] for r in results if r['has_diagram']) else '☐'} "
        f"At least 1 diagram returned",
        f"- ☐ Diagram is colored and labeled (manual check required)",
        f"- ☐ Markdown renders correctly in Copilot Studio (manual check required)",
        f"- ☐ Fallback demo video recorded",
        f"",
    ]

    RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✅ Results written to: {RESULTS_FILE}")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    questions = load_questions()
    if not questions:
        print(f"❌ No questions found in {QUESTIONS_FILE}")
        exit(1)

    print(f"Running {len(questions)} test questions against endpoint...")
    print(f"Endpoint: {ENDPOINT_URL}\n")

    if "YOUR_PROMPT_FLOW_PRIMARY_KEY" in ENDPOINT_KEY:
        print("⚠️  WARNING: PROMPT_FLOW_KEY not set. Edit .env or the script.")
        print("   Requests will fail with 401 Unauthorized.\n")

    results = []
    for num, question in questions:
        print(f"Q{num:02d}: {question[:60]}...")
        response, elapsed = call_endpoint(question)
        result = validate_response(num, question, response, elapsed)
        status = "✅ PASS" if result["pass"] else "❌ FAIL"
        print(f"     {status}  ({elapsed:.1f}s)")
        results.append(result)
        time.sleep(0.5)   # avoid rate limiting

    passed = sum(1 for r in results if r["pass"])
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{len(results)} passed")
    print(f"{'='*50}")

    write_results(results)
