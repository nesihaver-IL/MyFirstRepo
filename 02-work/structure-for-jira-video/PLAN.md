# Structure for Jira: Team Video Clip Plan (Cognyte)

Status: DRAFT v0.2, plan and storyboard only. No video has been produced yet.
Date: 2026-10-30
Confirmed by owner: Jira edition = Data Center. Language = English only.
Still open: narration (own voice or synthetic), hosting location, Cognyte brand template (see BRAND.md).

---

## 0. Read this first: what is verified and what is not

Research for this plan was limited. The session's network policy blocked the
Atlassian Marketplace listing, the ALM Works documentation wiki, and a
third-party guide, so most product facts below come from search snippets and
older pages. Treat every item as "to verify in a live trial" before it goes
on screen.

| Item | Status | Source or note |
|---|---|---|
| Structure builds custom issue hierarchies from Jira issues, across projects | Supported by several sources | ALM Works product pages, vendor wiki snippets |
| Multiple structures can be created and shared | Supported by a snippet | ALM Works product page (older) |
| Excel-like formulas (Expr language), built-in RICE and WSJF formulas | Supported by vendor marketing snippet | Vendor marketing; check current version |
| Generators (automation that fills a structure from JQL) | Supported by vendor marketing snippet | Verify the exact name and UI in the current version |
| Gantt view via the Structure.Gantt extension | Supported, but pricing changed (paid from v2.0) | Snippet from a 2024-era review; re-check |
| Structure.Testy (test checklists) | Mentioned in older material | Verify it is still offered |
| Vendor ownership (ALM Works, now part of Tempo) | Unverified | One third-party article. Verify before naming the owner in the video |
| Cloud vs Data Center feature parity | NOT verified | Cloud migration write-ups are dated (2021). Must test on the edition the team uses |
| Current prices | NOT verified | I found no reliable Structure price. Get a quote or read the Marketplace page |
| Exact UI labels, menu paths, button names | NOT verified | Must be taken from a live trial, not from this document |

Pricing context (third-party sources, not verified): one source says Atlassian
stopped selling new Data Center subscriptions to new customers on
2026-03-30. If the company is on Data Center, this affects the edition
decision. Verify against Atlassian's own announcement.

Unknown and blocking: which edition the team uses (Cloud or Data Center).
Everything in the scenes depends on it.

---

## 1. Objective and audience

- Goal: a team member who has never used Structure can build a working
  project structure (epics, features, tasks, owners, progress) in under 15
  minutes after watching the clip.
- Audience: the development team and the people who plan with them
  (product, delivery, managers). Internal use, Cognyte.
- Message to land: "Jira shows issues. Structure shows the plan. Build the
  plan once, and let the work keep it current."
- Non-goal: a sales or marketing video. No pricing, no competitor claims.

Success check (test after publishing): ask 3 team members to build a
10-issue structure from the clip alone. Target: 3 of 3 finish without asking
for help. Record the questions they ask; each question becomes a fix to the
clip or a pinned FAQ.

---

## 2. Deliverables

| # | Deliverable | Length | Use |
|---|---|---|---|
| D1 | Main clip: "Build a project plan in Structure" | ~6 to 7 min, with chapters | Onboarding, linked from the team wiki |
| D2 | Three tip clips (each 45 to 60 s) | 3 x ~1 min | Short reminders in team channels |
| D3 | One-page quick reference (text) | 1 page | Printed or pinned next to the clip |
| D4 | Sample project file (Jira project, 25 to 40 issues) | n/a | Used in the clip and handed to trainees |

Scope cut if time is short: D1 + D3 only. D2 and D4 are optional.

---

## 3. Storyboard for D1 (main clip, about 6.5 min)

Format: 16:9, 1080p, captions on by default (team may watch muted).
Voice: one presenter (you), plain language, no jargon without a 3-second
definition. Every scene has one on-screen claim and one action.

| Scene | Time | On screen | Narration (draft) | Notes |
|---|---|---|---|---|
| 1. Hook | 0:00 to 0:20 | Flat Jira issue list, 40 issues, no hierarchy | "This is our backlog. It has everything in it, and nothing shows how it fits together." | Hook. Show the problem first. |
| 2. What Structure is | 0:20 to 0:50 | Title card, then a Structure view with the same issues grouped | "Structure is an add-on that organizes Jira issues into the hierarchy you need, without changing the issues themselves." | Say "without changing the issues". Confirm this is true in trial. |
| 3. Our example project | 0:50 to 1:15 | Sample project: goal, 3 features, 12 stories | "We will build one plan for a security-product release. Here is the target." | Use a neutral sample, not real customer data. |
| 4. Create a structure | 1:15 to 2:00 | Create a new structure, name it, pick a source | "Start a new structure. Give it a name your team will recognize." | Exact menu names from trial. |
| 5. Add issues | 2:00 to 2:45 | Add issues by search (JQL) and by selecting from Jira | "Add issues by query or by hand. A query keeps the list current as new issues appear." | Show both methods in 15 s each. |
| 6. Build the hierarchy | 2:45 to 3:45 | Indent and outdent, drag to reorder, group under the goal | "Build the tree by dragging. Parents show their children's totals." | Show roll-up only if verified in trial. |
| 7. Columns and formulas | 3:45 to 4:30 | Add a column, add one formula (e.g. percent done) | "Columns read the data already in Jira. Formulas calculate values without exports." | One formula only. Keep it simple. |
| 8. Generator (automation) | 4:30 to 5:10 | Set one generator from a JQL query | "A generator adds new issues to the plan automatically. Set it once." | Optional. Cut if the edition does not support it. |
| 9. Share and save | 5:10 to 5:35 | Save the view, share with the team | "Save the view so everyone sees the same plan." | Check sharing rules and permissions first. |
| 10. Pro tips summary | 5:35 to 6:20 | Three tips on screen | See section 4 | Keep to three tips. |
| 11. Close | 6:20 to 6:40 | Quick reference card | "The one-page guide is linked below. Your first structure takes 15 minutes." | Link the quick reference. |

Chapter markers (for the video platform): Hook, What it is, Create, Add issues,
Hierarchy, Columns and formulas, Generators, Share, Tips, Close.

---

## 4. Pro tips (to validate in trial before recording)

Each tip gets a 10 to 20 second on-screen demo. Only include a tip after
you have seen it work in the team's edition.

1. Start with the goal, not the tasks. Add the top-level outcome first, then
   attach features and stories beneath it. Plans built top-down are easier to
   read.
2. Use a query for anything that changes. A JQL-based source stays current;
   hand-picked lists go stale. Label each structure with its source.
3. Keep one structure per decision audience. A delivery view for managers, a
   sprint view for the team. Do not put every field in every view.
4. Use one formula, then stop. Percent done or days remaining is enough. More
   formulas mean more explaining.
5. Check the roll-up against Jira before you trust it. Pick one parent, add up
   its children by hand, and compare. This builds trust fast.
6. Name views by question, not by project. "What ships in Q1?" beats
   "Project X view 2".
7. Use Structure for planning, Jira for doing. Teams update issues in Jira;
   the structure reflects them. Do not ask people to edit the structure to
   report status.

---

## 5. Timeline (project plan)

Assumes one owner (you) working part-time, about 6 to 8 hours per week. Dates
are estimates from a start date of 2026-11-03 (Monday). Adjust once the
edition and the trial are confirmed.

| Phase | Work | Effort (h, estimate) | Target dates | Exit criteria |
|---|---|---|---|---|
| P0. Decide and access | Confirm edition (Cloud or DC), get trial or license, confirm the team can open it | 2 to 3 | Nov 3 to Nov 5 | Edition known, trial works |
| P1. Trial and verification | Build the sample project, record every menu name, check each claim in section 0 | 6 to 8 | Nov 5 to Nov 12 | Verification table fully filled in |
| P2. Script and storyboard | Finalize section 3, cut or keep scene 8 based on P1 | 3 to 4 | Nov 12 to Nov 14 | Script approved by you |
| P3. Sample project | Build D4 (25 to 40 issues) in a sandbox Jira project | 3 to 4 | Nov 12 to Nov 17 | Project loads cleanly, no real data |
| P4. Screen capture | Record the screens in a clean run, two takes | 3 to 4 | Nov 17 to Nov 19 | Raw footage, 2 takes per scene |
| P5. Animation and edit | Build title cards, callouts, transitions, chapter markers (see section 6) | 12 to 16 | Nov 19 to Nov 26 | Rough cut, 6 to 7 min |
| P6. Voice and captions | Record narration (or decide on synthetic voice), captions, checks | 3 to 4 | Nov 26 to Nov 28 | Captions match audio |
| P7. Review and fix | Two reviews: one by a peer, one by a non-user. Fix top issues | 3 to 4 | Nov 28 to Dec 2 | Peer review passed |
| P8. Publish and test | Post the clip and quick reference, run the 3-person test (section 1) | 2 to 3 | Dec 2 to Dec 5 | 3 of 3 test users finish the task |

Total effort: about 36 to 48 hours (estimate). Calendar: about 5 weeks at part
time, or 2 weeks full time.

Milestones:
- M1, Nov 5: edition confirmed and trial running (go / no-go on the plan).
- M2, Nov 14: script approved (scope locked).
- M3, Nov 26: rough cut ready.
- M4, Dec 5: published and tested.

---

## 6. Budget

Time is the main cost. Money is unknown until the edition and the tools are
confirmed.

| Line | Estimate | Confidence |
|---|---|---|
| Your time (P0 to P8) | 36 to 48 h | Medium. Animation time is the biggest variable |
| Structure licence or trial | Unknown | Low. Needs a quote from the vendor or Marketplace |
| Video tooling | Unknown | Low. The HyperFrames open-source framework is one option. Check its license and terms before use |
| Narration (synthetic voice, if used) | Unknown | Low. Depends on the tool and plan you choose |
| Hosting | Internal wiki or video platform | Confirm the company's standard |

Budget guard: if P5 runs over 16 hours, cut scene 8 and tip 7, and ship D1
with D3 only.

---

## 7. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Edition differs from the one the clip shows (Cloud vs DC) | Medium | High | Decide in P0. Record only on the team's edition |
| UI changes between trial and publish | Medium | Medium | Record in the final week; note the version number in the clip description |
| Feature in the script is missing or renamed | Medium | Medium | Verify each scene in P1. Mark unverified scenes "cut if not available" |
| Clip becomes outdated | High (over time) | Medium | Review every 6 months; keep the quick reference as the source of truth |
| Real customer or internal data appears on screen | Low | High | Sample project only (D4). Check every frame before publishing |
| Team does not watch | Medium | Medium | Short tip clips (D2); link the clip in onboarding |

---

## 8. Decisions I need from you

1. Edition: Cloud or Data Center? (Blocks P1.)
2. Language: English only, or a Hebrew version too? (Changes P5 and P6 effort.)
3. Narration: your voice recorded, or a synthetic voice?
4. Hosting: where will the team find the clip?
5. Branding: does Cognyte have a template or colors I should use?

Once you answer 1 to 3, I can build the sample project spec (D4), finish the
script, and start the animation build.

---

## 9. Next steps (my side)

1. Write the verification checklist for P1 (every claim in section 0 as a yes/no).
2. Draft the full narration script with the final scene timings.
3. When you confirm the edition and provide trial access, record the real
   menu names and update the storyboard.
4. Build the animation (P5) from the approved storyboard.

Note on the animation: I have not built any animation yet. Building it
before the P1 verification would put unverified screens and menu names into
the video, so I recommend waiting for P1.
