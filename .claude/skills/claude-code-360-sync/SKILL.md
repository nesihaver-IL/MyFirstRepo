---
name: claude-code-360-sync
description: Scheduled maintenance pass for the Claude Code 360° GitHub Pages dashboard. Finds project folders in this repo that look like new GitHub-Pages-ready static sites, wires the safe ones into the deploy workflow and the Showcase list, flags anything that looks personal/financial for human review instead of auto-publishing it, and opens a PR. Use when running the twice-weekly claude-code-360-sync routine, or when the user asks to "sync the 360 page," "check for new deliverables," or "run the dashboard sync."
---

# Claude Code 360° Sync

## Why this exists

`01-personal/claude-code-360/index.html` (the public GitHub Pages dashboard) has two kinds of
content:

- **Live tabs** (Overview, Work Tree, Projects, Skills & Agents, Hygiene) — these fetch
  straight from GitHub's API in the visitor's browser on every page load. They need **no
  maintenance**. Don't "update" them from this skill; there's nothing to update.
- **The Showcase section of the Deliverables tab** — a hardcoded `SHOWCASE` array in that same
  file, because GitHub's API has no way to see what other GitHub-Pages-hosted projects exist in
  this repo until they're deployed. This drifts stale as new projects get added. **This is the
  only thing this skill touches.**

This skill does not touch the claude.ai-hosted Habits Dashboard artifact
(`.claude/skills/habits-dashboard/template.html`) or its own Showcase list — that one is
published interactively, with every item individually confirmed share-ready by the user before
it goes out (see `DECISIONS.md`). Don't extend this skill to auto-update that file.

## Scope — deliberately narrow, and never a silent publish

Chosen 2026-09-30 when this skill was built, to bound an **unattended, twice-weekly** process to
one reviewable kind of change:

1. It only ever opens a **pull request** — it never pushes to `main` directly, no matter what it
   finds. The PR is the entire review gate.
2. It never wires a folder into GitHub Pages without a human merging that PR. Running this skill
   does not, by itself, publish anything.
3. It holds back anything that looks personal/financial/credential-bearing rather than wiring it
   up "for review" — see **Sensitivity check** below. The first real scan this skill ever ran
   (during development, against this exact repo) found `01-personal/electricity-dashboard`
   (a Gmail bill-scraping tool with a `.env.example` right next to its `index.html`) and
   `01-personal/tzofim-payments` (a scouts payment tracker) sitting unwired. Neither should ever
   be auto-proposed as a one-click-mergeable "publish this" diff. That's not a hypothetical risk
   this scope note is guarding against — it's what the repo actually contained on day one.

## Steps

1. **Check for an already-open sync PR first.** List open PRs with
   `head: "nesihaver-IL:claude/claude-code-360-sync-*"` (GitHub's PR list API doesn't support
   wildcard heads directly — list open PRs and filter by branch name prefix client-side, or
   `search_pull_requests` with `head:claude/claude-code-360-sync in:nesihaver-IL/MyFirstRepo`).
   If one is still open, **stop here** — note its URL in your final reply and don't scan or open
   a second one. Piling up duplicate PRs between review cycles is worse than waiting.

2. **Start clean.** `git fetch origin main && git checkout -B claude/claude-code-360-sync-<YYYY-MM-DD> origin/main`
   (append `-2`, `-3`, … only if that exact branch name already exists remotely from a same-day
   retry).

3. **Scan.** Run `python3 .claude/skills/claude-code-360-sync/scripts/scan-static-sites.py` from
   the repo root. It prints a JSON array of candidates — folders under `01-personal/` or
   `02-work/` with an `index.html` at their root, not already referenced in
   `.github/workflows/deploy-pages.yml`, and not already in this file's known-folders list (see
   below). Each candidate carries `sensitive: true/false` and `sensitiveReasons`.
   - **If the array is empty: stop.** No commit, no branch push (delete the local branch),
     nothing in your reply beyond "nothing new to sync." This is the expected, boring outcome
     most runs.

4. **Split candidates into `safe` (`sensitive: false`) and `flagged` (`sensitive: true`).** The
   sensitivity check is a filename/doc-text heuristic, not a content audit — treat `false` as
   "no red flag found," not as "confirmed safe." Still read each safe candidate's actual
   `index.html` yourself before wiring it in; the heuristic only replaces the first pass, not
   your own judgment.

5. **For each `safe` candidate**, make both edits below in the same commit:
   - Add it to `.github/workflows/deploy-pages.yml`'s `Build combined site` step, following the
     exact existing pattern (see the `claude-code-360` block for the simplest example — no
     special-casing needed unless the folder has its own asset-stripping requirements like
     `thailand-memory-book` does):
     ```
     if [ -d "<path>" ]; then
       mkdir -p _site/<folder>
       cp -r <path>/. _site/<folder>/
     fi
     ```
     and add `"<path>/**"` to the `on.push.paths` list.
   - Add an entry to the `SHOWCASE` array in `01-personal/claude-code-360/index.html`:
     `{title:"<Guessed Title>", url:"https://nesihaver-il.github.io/MyFirstRepo/<folder>/"}` —
     derive the title from the folder name (kebab-case → Title Case) and note the script's
     `readmeHint` for that candidate in the PR body as a suggested better title/description for
     the reviewer to swap in if it's off.
   - Add `<folder>` to `knownDeliverableFolders` in
     `.claude/config/claude-code-360-sync.json` — once wired, never proposed again.

6. **For each `flagged` candidate**, do *not* touch the workflow or `index.html`. Instead, check
   `.claude/skills/claude-code-360-sync/needs-review.md` (create it with a one-line header if
   missing) and, only if that folder isn't already listed there, append a line: folder, path,
   and `sensitiveReasons`. This is idempotent on purpose — a flagged folder stays listed once
   until a human disposes of it (see **Dismissing a candidate** below), so it's never silently
   re-surfaced as "new" every run, but also never auto-published.

7. **If nothing changed this run** (no safe candidates wired, no new flagged entries to log),
   stop here — same as step 3's empty case.

8. **Commit, push, open the PR.** One commit covering whatever combination of
   `.github/workflows/deploy-pages.yml`, `01-personal/claude-code-360/index.html`,
   `.claude/skills/claude-code-360-sync/needs-review.md`, and
   `.claude/config/claude-code-360-sync.json` actually changed. Conventional prefix
   `chore(claude-code-360-sync):`. Push the branch, open a PR against `main` titled
   `chore(claude-code-360-sync): sync pass — <date>`. The PR body must:
   - List what got wired (safe), each with the live URL it'll get once merged, and say plainly:
     **"Merging this makes `<path>` publicly reachable at `<url>`. This skill checked filenames
     and docs for red flags, not the rendered page — open it yourself before merging."**
   - List what got flagged-only (if any), with reasons, and say plainly: **nothing below this
     line is published by this PR.**
   - Link back to this skill file so a reviewer unfamiliar with it has context.

9. **Append a Run Log entry to this file** (same commit) — see below. This is the mechanism for
   this skill to actually get better over time instead of repeating the same mistakes; don't
   skip it just because a run found nothing; a "found nothing, no changes to the process" line is
   fine, but a run that *did* learn something (a new false-positive pattern, a folder shape the
   scanner mishandled, a title guess that needed fixing) must record it here, specifically,
   before ending the session — not just mention it in the PR body where the next run will never
   see it.

## Dismissing a candidate without publishing it

To permanently stop a flagged (or any) candidate from being proposed again — because it's
confirmed never meant to be public, not because it was fixed — add its folder name to
`knownDeliverableFolders` in `.claude/config/claude-code-360-sync.json` by hand, or ask Claude to
do it in an interactive session. It will then be treated exactly like an already-wired folder:
never scanned again.

## Files

- `scripts/scan-static-sites.py` — the detector. Read-only, safe to re-run anytime. If you
  change its sensitivity patterns, say so in that run's Run Log entry, not just in the diff —
  the *reason* a pattern was added or loosened is the part worth keeping.
- `needs-review.md` — accumulates flagged candidates across runs until a human disposes of each
  one. Not a changelog; keep it to current open items only (remove a line once its folder is
  either wired or added to `knownDeliverableFolders`).
- `.claude/config/claude-code-360-sync.json` — state: which folders are permanently "handled"
  (wired or explicitly dismissed) and should never be re-proposed.

## Run Log

Append one entry per run that found or changed anything (skip pure no-op runs). Newest first.
Each entry: date, what was found/wired/flagged, and — this is the point — anything that would
make the *next* run smarter: a new sensitivity pattern worth adding, a candidate whose title
guess was wrong, a folder shape the scanner doesn't handle yet, a false positive worth loosening.

- **2026-09-30 (build time, not a scheduled run):** First-ever scan against this repo found 3
  unwired candidates: `electricity-dashboard` and `tzofim-payments` correctly flagged sensitive
  (a Gmail-fetching script + `.env.example` sitting next to the former's `index.html`; "payment"
  in both the latter's folder name and its `CLAUDE.md`). `math-practice` was *also* flagged, but
  as a false positive — its `CLAUDE.md` contains the phrase "Question Bank" (curriculum
  terminology), which the bare `bank\b` pattern can't distinguish from "bank account." Left the
  pattern as-is rather than special-casing it immediately: over-flagging is the safe failure
  mode here (a human reviews one extra harmless folder), under-flagging is not. If `bank\b`
  keeps producing false positives across real runs, tighten it to something like
  `bank\s*(account|details|routing|iban)` instead of removing it outright.
