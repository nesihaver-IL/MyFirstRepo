---
name: habits-dashboard
description: Build and publish the Claude Code Habits Dashboard — a snapshot of the work tree, active session, installed base, and archive for this workspace. Use when the user asks to see, refresh, update, or check "the dashboard," "the habits dashboard," "my snapshot," or asks how their workspace/setup looks right now. Works identically from Claude Code Desktop, VS Code, and the web.
---

# Habits Dashboard

On-demand snapshot of this workspace, built fresh every time it's invoked — never edit a
previous run's output by hand, always regenerate from current state. There is no background
process or scheduled job behind this; it runs once, synchronously, when asked.

## Steps

1. **Gather facts.** Run `.claude/skills/habits-dashboard/scripts/gather.sh` from the repo
   root. It prints one JSON object covering git state, directory sizes, the skill/agent
   inventory, per-project stats (auto-discovered under `01-personal/` and `02-work/`, not
   hardcoded), and a set of hygiene checks (tracked venvs, tracked `.claude/worktrees/`,
   backslash-named paths, doc staleness, registry drift, skill-count mismatch). Treat every
   field in this output as ground truth for this run — don't reuse numbers from a prior
   conversation.

2. **Add what the script can't see.** Two things need a human-in-the-loop judgment call each
   run, not a script:
   - **Session facts** — surface (Desktop / VS Code / web), model, working directory. State
     plainly what you can verify vs. can't (you cannot see other surfaces' open files or other
     concurrent sessions — say so rather than guessing).
   - **MCP connector health** — note any connector that dropped, flapped, or failed to connect
     *during this run* (you'll see this directly in tool call results and system reminders).
     This is the "installed base" signal that matters most and a script cannot observe it.

3. **Check branch vs. main first.** Before treating anything as current, confirm this branch's
   relationship to `origin/main` (`gather.sh`'s `repo.aheadOfMain`/`behindMain`). If this
   branch's last PR was already merged, restart it from latest main
   (`git fetch origin main && git checkout -B <branch> origin/main`) before doing anything
   else — this exact gap is what broke an earlier version of this dashboard mid-session.

4. **Render.** Read `.claude/skills/habits-dashboard/template.html`. Inside its `<script>`
   block it has a `// ===== BEGIN DASHBOARD DATA (regenerated each run) =====` ...
   `// ===== END DASHBOARD DATA =====` section. Replace everything between those two comment
   lines with fresh
   `var` declarations built from steps 1–2. Keep the surrounding CSS/JS/component structure
   untouched — that's the visual system this dashboard is supposed to keep consistent across
   runs. Judgment calls that belong in this step, not the script:
   - Group skills into the same rough domains as before (AWS, PM & workflow, data/domain,
     etc.) — adjust groupings only if the actual skill set changed.
   - Write hygiene "why it matters" and "suggested fix" text in plain language, same tone as
     previous runs — terse, concrete, no hedging.
   - Only include a hygiene flag if `gather.sh` actually found evidence for it this run. Don't
     carry forward a flag from a previous conversation's memory once the script shows it's
     clean — that's exactly the kind of stale-doc drift this dashboard exists to catch.
   - Note commit-level detail worth surfacing (e.g. a commit that swept in far more files than
     its message implies) using `git log` / `git show --stat` directly — the script only gives
     aggregate stale-doc timestamps, not per-commit story.

5. **Publish, keeping the same link.** Check whether
   `.claude/config/habits-dashboard.json` exists and has an `artifactUrl` field.
   - If yes: call the Artifact tool with that `url` so this run updates the existing page in
     place rather than minting a new link.
   - If no (first run ever, or the file is missing): publish fresh, then write the returned
     URL into `.claude/config/habits-dashboard.json` (create the file if needed) so future
     runs update the same link. Use favicon `🧭`, title "Claude Code Habits Dashboard."
   - **Always also write the rendered file to disk and send it directly** (e.g. via a
     send-file tool) regardless of whether publishing succeeded. The Artifact-publishing tool
     is confirmed available from Claude Code on the web; it is not confirmed available from
     Desktop or VS Code sessions. A local file works from every surface, so don't make the
     dashboard depend on the web-only path.
   - If the Artifact tool errors or isn't available in this session, don't treat that as a
     failure of the skill — just skip straight to the local-file delivery and say so.

6. **State what changed.** In your reply, don't just say "done" — name the two or three things
   that actually moved since the last known snapshot (a hygiene flag that cleared, a doc that
   got staler, a project that went quiet). That's the point of running this repeatedly instead
   of once.

## Files

- `scripts/gather.sh` — fact-gathering, safe to re-run anytime, read-only (never modifies the
  repo).
- `template.html` — the visual shell + most recent data. Only the marked data block should
  change between runs; if you find yourself editing CSS or the JS component logic to make a
  new run "fit," that's a sign the schema needs a real update, not a one-off patch — update
  this file deliberately and explain why in the commit, don't drift it silently.

## Keeping this skill itself from drifting

This skill is only as trustworthy as the other docs it reports on. If you rename, add, or
archive skills in `.claude/skills/`, that changes `gather.sh`'s output automatically — no
action needed there. But if you change what this skill *does* (new hygiene check, new tab,
new data field), update this file and bump the skill count reference in `CLAUDE.md` and
`.claude/COMMAND_REGISTRY.md` in the same commit. Don't leave that for "next time."
