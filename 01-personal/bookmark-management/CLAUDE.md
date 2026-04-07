# Bookmark Management Project — CLAUDE.md

## Project Overview

**Goal:** Reorganize Chrome bookmarks using a collaborative AI-assisted system that keeps mission-critical tools always visible and aggressively archives outdated content.

**Timeline:** ~2 hours total (mostly hands-off), with ~15 minutes of active work (Phase 2 approval)

**Model:** Collaborative (3-phase: ANALYZE → PLAN [user review] → EXECUTE)

## Configuration (Locked In)

| Setting | Your Choice |
|---------|-------------|
| **Visibility** | Option C (all 8 hourly-use tools visible at top level) |
| **Archiving Strategy** | Strict (3+ months untouched = archive immediately) |
| **Approval Gate** | Yes (user reviews Phase 2 before Phase 3 executes) |

## Your 8 Mission-Critical Tools (Never Archive)

These stay visible at the top level forever:
1. **WhatsApp Web** — Communication (hourly)
2. **Gmail** — Email & task management (hourly)
3. **Confluence Pages** — Documentation (hourly)
4. **JIRA** — Project tracking (hourly)
5. **ChatGPT** — AI assistance (hourly)
6. **Gemini** — AI assistance (hourly)
7. **Mako** — Hebrew news (hourly check)
8. **Ynet** — Hebrew news (hourly check)

**Supporting:** Hilanet (Information/news, always one-click)

## The 3-Phase Process

### Phase 1: ANALYZE (~45 min, hands-off)
Claude Code will:
- Read your bookmark export (HTML/JSON)
- Classify each bookmark (Tier 1, 2, 3)
- Identify dead links, duplicates, old items
- Generate audit report + analytics CSV
- Flag items untouched 3+ months (STRICT mode candidates)

**You do:** Nothing. Wait for completion.

### Phase 2: PLAN (~5 min, user review — CRITICAL STEP)
Claude Code will:
- Design new folder structure (6 top-level folders)
- Create migration map (old path → new path)
- Visualize structure with your tools highlighted in GREEN
- Show samples: "10 dev tools → REFERENCE", "45 duplicates → consolidated"
- **Ask for your approval before proceeding**

**You do:** Review the plan. Confirm:
- ✅ All 8 hourly-use tools are at top level?
- ✅ Folder structure makes sense?
- ✅ Strict 3-month archiving acceptable?

**Send:** "YES" to proceed, or describe changes needed

### Phase 3: EXECUTE (~35 min, hands-off)
Claude Code will:
- Create new folder structure in Chrome
- Move 847 bookmarks to new locations
- Delete dead links (5)
- Archive dormant items (3+ months untouched)
- Consolidate duplicates
- Validate all links
- Generate CLAUDE.md with maintenance SOPs

**You do:** Nothing. Wait for completion, then verify in Chrome.

## New Folder Structure (Post-Execution)

```
Bookmarks Bar (8 items — always visible):
├─ WhatsApp Web
├─ Gmail
├─ Confluence Pages
├─ JIRA
├─ ChatGPT
├─ Gemini
├─ Mako
└─ Ynet

Root Folders (6 top-level folders, max 2-level depth):
├─ Hilanet                    ← Information/news
├─ REFERENCE                  ← Documentation, specs, guides
├─ LEARNING                   ← Tutorials, courses, training
├─ PROJECTS                   ← Active project folders [by name + date]
│  ├─ Project-A [2026-03]
│  ├─ Project-B [2026-03]
│  └─ Project-C [2026-03]
├─ READING                    ← Articles, research, long-form
└─ ARCHIVE                    ← Untouched 3+ months, completed projects
   ├─ [2026-03] Completed-Projects
   ├─ [2026-03] Outdated-Articles
   └─ Dead-Links
```

**Rationale:**
- Max 2 levels deep (shallow = findable)
- All 8 hourly-use tools instant access (zero navigation)
- Aggressive archiving keeps active bookmarks lean (<300 items)
- ARCHIVE is not permanent deletion (can restore anytime)

## Archiving Philosophy: STRICT MODE

- **Delete immediately:** Dead links, duplicates, completely obsolete items
- **Archive to ARCHIVE folder:** Anything untouched for 3+ months (NOT 6, NOT 12)
- **No "Maybe Later" folder:** Ambiguous items clarified in Phase 2
- **Rationale:** Keep active bookmarks discoverable; don't let clutter accumulate

## How to Execute (Step-by-Step)

See [NESI_EXECUTION_GUIDE.md](./NESI_EXECUTION_GUIDE.md) for detailed Steps 1–8.

**Abbreviated:**

1. **Export bookmarks:** Chrome → Settings → Bookmarks → Manager → Export Bookmarks (5 min)
2. **Open Claude Code:** Go to claude.ai in Chrome, open Claude Code extension
3. **Paste prompt:** Copy entire `NESI_FINAL_BOOKMARK_PROMPT.md` into Claude Code chat
4. **Send command:**
   ```
   Analyze and reorganize my bookmarks using the COLLABORATIVE model.
   Export file: [PASTE YOUR FILE PATH HERE]
   Configuration: Option C (maximal visibility) + Strict archiving (3 months)
   Target: Keep my 8 hourly-use tools always visible, aggressively archive old items, show me the plan before execution.
   ```
5. **Wait for Phase 1** (~45 min, hands-off)
6. **Review Phase 2 plan** (5 min active — this is YOUR critical step)
7. **Approve:** Reply "YES" to execute Phase 3
8. **Wait for Phase 3** (~35 min, hands-off)
9. **Verify in Chrome** and set 3 calendar reminders (maintenance)

## Maintenance After Execution

### Weekly (5 min)
- [ ] Check Bookmarks Bar (all 8 tools still there?)
- [ ] Look for duplicates (delete if found)

### Monthly (10 min)
- [ ] Audit PROJECTS folder (still active?)
- [ ] Move completed projects → ARCHIVE/[date]
- [ ] Move old articles → ARCHIVE/[date]

### Quarterly (15 min)
- [ ] Full audit: find items untouched 3+ months
- [ ] Move stale items → ARCHIVE
- [ ] Delete truly obsolete archived items (6+ months old)
- [ ] Review folder names (still make sense?)

**Calendar Reminders:**
- Recurring "Weekly: Bookmark maintenance" (Sunday 18:00)
- Recurring "Monthly: Archive old items" (1st Monday, 09:00)
- Recurring "Quarterly: Full bookmark audit" (Jan 1, Apr 1, Jul 1, Oct 1)

## Files in This Project

| File | Purpose |
|------|---------|
| **NESI_EXECUTION_GUIDE.md** | Step-by-step walkthrough (read first) |
| **README_START_HERE.md** | Quick reference & overview |
| **NESI_FINAL_BOOKMARK_PROMPT.md** | Full prompt for Claude Code (copy-paste) |
| **CLAUDE.md** | This file (project config) |
| **README.md** | Project homepage |

## Key Constraints & Rules

### ✅ MUST ENFORCE
- All 8 hourly-use tools **always visible at top level** (no nesting, no archiving)
- Max folder depth = 2 levels (no sub-folders inside sub-folders)
- Strict 3-month archiving (not 6, not 12)
- Phase 2 approval gate required before Phase 3 executes
- All tools must be clearly marked in GREEN during Phase 2 review

### ❌ NEVER DO
- Archive any of the 8 hourly-use tools
- Nest any of the 8 hourly-use tools under subfolders
- Delete bookmarks (move to ARCHIVE instead)
- Proceed to Phase 3 without user approval

## Troubleshooting

**Q: Claude Code can't access my bookmark file**
A: Ensure:
1. File is saved as HTML (not JSON if Chrome doesn't support)
2. No spaces or special characters in file path
3. Paste full file path (e.g., `/Users/Nesi/Downloads/nesi_bookmarks_2026-03-24.html`)

**Q: Something I use frequently got archived**
A: Before Phase 3 executes, in Phase 2 review say:
"Move [item] from ARCHIVE to [folder]. Then proceed."
Claude Code will re-plan and show you again for approval.

**Q: Can I change the folder structure later?**
A: Yes, anytime. Just maintain:
- All 8 hourly-use tools always at top level
- Max 2-level depth
- ARCHIVE for anything untouched 3+ months

## Status

- **Project Start:** 2026-03-24
- **Configuration:** Locked in
- **Phase:** Ready for Phase 1 (awaiting user bookmark export)
- **Next Step:** Export bookmarks, send command, review Phase 2 plan

---

**Ready to start?** Follow NESI_EXECUTION_GUIDE.md, Step 1.
