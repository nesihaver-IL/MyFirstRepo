#!/usr/bin/env python3
"""claude-code-360-sync: find new GitHub-Pages-shaped project folders.

Scans 01-personal/* and 02-work/* (one level deep, skipping any folder named
"archive") for folders containing an index.html at their root. Excludes any
folder already referenced anywhere in .github/workflows/deploy-pages.yml (by
its "<base>/<name>" path) and anything already listed in this skill's state
file (.claude/config/claude-code-360-sync.json -> knownDeliverableFolders),
so nothing already handled — or already proposed in an earlier run — gets
proposed again.

Each candidate also gets a best-effort "sensitive" flag: a folder is flagged
(never auto-wired, see SKILL.md) if its name, CLAUDE.md/README, or any
sibling filename suggests financial, payment, credential, or otherwise
personal data — a Gmail-fetching script, a .env.example, "payment"/"תשלום"
in the name or docs, etc. This is a heuristic safety net, not a guarantee:
it caught the first two real candidates this skill ever scanned
(electricity-dashboard, tzofim-payments) but a human still has to actually
look before merging anything.

Prints one JSON array of candidates to stdout. Read-only: never modifies
the repo.
"""
import json
import os
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(REPO_ROOT)

WORKFLOW_PATH = ".github/workflows/deploy-pages.yml"
STATE_PATH = ".claude/config/claude-code-360-sync.json"

SENSITIVE_PATTERNS = [
    r"payment", r"תשלום", r"invoice", r"\bbill\b", r"billing",
    r"financ", r"salary", r"credit.?card", r"iban", r"bank\b",
    r"ssn\b", r"תעודת זהות", r"\.env\b", r"credential", r"gmail.?api",
    r"private\b", r"confidential",
]
SENSITIVE_RE = re.compile("|".join(SENSITIVE_PATTERNS), re.IGNORECASE)


def load_known():
    if not os.path.exists(STATE_PATH):
        return set()
    with open(STATE_PATH, encoding="utf-8") as f:
        return set(json.load(f).get("knownDeliverableFolders", []))


def workflow_text():
    if not os.path.exists(WORKFLOW_PATH):
        return ""
    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        return f.read()


def readme_hint(folder):
    """First non-heading, non-empty line of README.md or CLAUDE.md, as a description guess."""
    for fname in ("README.md", "CLAUDE.md"):
        path = os.path.join(folder, fname)
        if os.path.exists(path):
            with open(path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip().lstrip("#").strip()
                    if line:
                        return line
    return ""


def sensitivity_check(folder, name):
    """Returns (flagged: bool, reasons: [str]) from filenames + doc text signals."""
    reasons = []
    if SENSITIVE_RE.search(name):
        reasons.append("folder name")
    for fname in os.listdir(folder):
        if fname == "index.html":
            continue
        if SENSITIVE_RE.search(fname):
            reasons.append(f"sibling file: {fname}")
    for fname in ("README.md", "CLAUDE.md"):
        path = os.path.join(folder, fname)
        if os.path.exists(path):
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
            if SENSITIVE_RE.search(text):
                reasons.append(f"{fname} content")
    return (len(reasons) > 0, reasons)


def main():
    known = load_known()
    wf = workflow_text()
    candidates = []
    for base in ("01-personal", "02-work"):
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            if name == "archive":
                continue
            full = os.path.join(base, name)
            if not os.path.isdir(full):
                continue
            if not os.path.exists(os.path.join(full, "index.html")):
                continue
            rel = f"{base}/{name}"
            if rel in wf:
                continue
            if name in known:
                continue
            flagged, reasons = sensitivity_check(full, name)
            candidates.append({
                "folder": name,
                "path": rel,
                "readmeHint": readme_hint(full),
                "sensitive": flagged,
                "sensitiveReasons": reasons,
            })
    print(json.dumps(candidates, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
