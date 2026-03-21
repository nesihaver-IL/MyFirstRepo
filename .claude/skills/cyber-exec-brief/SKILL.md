---
name: cyber-exec-brief
description: Craft executive-level presentations and status updates for cybersecurity R&D projects in the B2C market. Content is always short, bullet-driven, and written for senior management. Triggers on keywords like exec brief, executive update, status report, cyber project update, management presentation, project status, roadmap summary, risk brief, milestone update, board presentation, steering committee.
---

# Cyber Exec Brief

Craft sharp, executive-ready communications for **cybersecurity R&D projects** in the B2C market.
Every output follows a single rule: **one idea per bullet, no noise, high signal**.

---

## Audience

**Who reads this**: C-suite, VP Engineering, VP Product, Board, Steering Committee.
**What they want**: Status, risk, decision — in 60 seconds or less.
**What they don't want**: Technical deep-dives, jargon, background, qualifications.

---

## Writing Rules (Non-Negotiable)

| Rule | Bad | Good |
|------|-----|------|
| **One bullet = one fact** | "We are investigating an issue with the auth service that may affect login flows for users who use SSO..." | "SSO auth degraded — impacting ~12% of B2C logins" |
| **Lead with status, not activity** | "The team is working on..." | "On track / At risk / Delayed" |
| **Numbers over adjectives** | "significant delay" | "3 weeks behind plan" |
| **Decision first** | "We would like to propose..." | "Decision needed: extend timeline or reduce scope" |
| **No passive voice** | "It has been decided that..." | "We decided..." |
| **Max 6 bullets per section** | — | Ruthlessly cut anything non-critical |

---

## Output Templates

### 1. Weekly / Sprint Status Update

```
PROJECT: [Name]  |  WEEK [N] / [Sprint N]  |  [Date]
STATUS: 🟢 ON TRACK  /  🟡 AT RISK  /  🔴 DELAYED

PROGRESS THIS PERIOD
• [Milestone or deliverable completed]
• [Key decision made]
• [Dependency unblocked or resolved]

NEXT PERIOD
• [Top 1-3 planned actions — must-have only]

RISKS & BLOCKERS       IMPACT     ACTION OWNER    DUE
• [Risk in one line]   HIGH/MED   [Name]          [Date]

DECISIONS NEEDED FROM MANAGEMENT
• [Specific ask — what you need, by when, and why it matters]
```

---

### 2. Milestone / Gate Review

```
GATE [N] REVIEW — [Phase Name]
Project: [Name]  |  Date: [Date]  |  Outcome: PASS / CONDITIONAL / HOLD

WHAT WAS DELIVERED
• [Deliverable 1 — 1 line]
• [Deliverable 2 — 1 line]

GATE CRITERIA SCORECARD
• Security architecture review    ✅ / ⚠️ / ❌
• Threat model completed          ✅ / ⚠️ / ❌
• B2C compliance checkpoints met  ✅ / ⚠️ / ❌
• Performance benchmarks hit      ✅ / ⚠️ / ❌
• Penetration test scope agreed   ✅ / ⚠️ / ❌

OPEN ITEMS (must close before next gate)
• [Item — owner — due date]

NEXT GATE: [Name]  |  Target: [Date]
```

---

### 3. Risk / Issue Brief

```
RISK BRIEF — [Date]
Project: [Name]

TOP RISKS THIS PERIOD

[Risk Name]
  Severity : HIGH / MEDIUM / LOW
  Impact   : [One sentence — what breaks if this happens]
  Trigger  : [What event activates the risk]
  Mitigation: [What we are doing — owner — due]
  Status   : 🟢 Mitigated / 🟡 In progress / 🔴 Unmitigated

RISKS CLOSED THIS PERIOD
• [Risk name] — closed [date] — how resolved

ESCALATION REQUIRED
• [Yes/No — if yes, state what decision or resource is needed]
```

---

### 4. Executive Roadmap Snapshot

```
ROADMAP SNAPSHOT — [Project Name]
As of: [Date]

PHASE          DATES           STATUS        NOTE
───────────────────────────────────────────────────────────
Discovery      Q1 Wk1–4        ✅ COMPLETE   Threat model signed off
Architecture   Q1 Wk5 – Q2 Wk2 🟡 AT RISK   Auth design 1 wk behind
Development    Q2 Wk3 – Q3 Wk6 ⬜ PLANNED   —
Security Test  Q3 Wk7–10       ⬜ PLANNED   Pen test vendor confirmed
Launch         Q4 Wk1          ⬜ PLANNED   B2C go-live

KEY MILESTONES
• [Date] — [Milestone name]
• [Date] — [Milestone name — flagged if at risk]

CRITICAL PATH ITEM
• [Single biggest blocker to on-time launch — one sentence]
```

---

### 5. Board / Steering Committee Slide Notes

```
[SLIDE TITLE — use for presentation headers]

SITUATION (what is true today — 2 bullets max)
•
•

COMPLICATION (what changed or what's at risk — 2 bullets max)
•
•

RESOLUTION (what we are doing about it — 2 bullets max)
•
•

DECISION REQUESTED
• [One clear ask — yes/no or choose A/B]
  Deadline: [Date]  |  Owner: [Name]
```

---

### 6. Cyber Security B2C Project — Specific Sections

Use these sections when the update covers cybersecurity-specific themes:

#### Threat Posture Update
```
THREAT POSTURE
• Active threat surface: [describe in 1 line — e.g., "web + mobile auth flows"]
• New threats identified this period: [N] — [HIGH: N, MEDIUM: N]
• Mitigations shipped: [N]
• Open critical findings: [N] — target closure: [date]
• B2C user exposure: [estimated % of users at risk if unmitigated]
```

#### Compliance & Regulatory
```
COMPLIANCE TRACK
• Frameworks in scope: [e.g., GDPR, SOC 2, ISO 27001, PCI-DSS]
• Status: [On track / Gap identified]
• Next audit / assessment: [date]
• Action required: [yes / no — if yes, what]
```

#### Security Incident (if applicable)
```
INCIDENT SUMMARY — [Severity: P1/P2/P3]
• Detected: [date/time]
• Affected: [what system / how many B2C users impacted]
• Root cause: [one sentence — confirmed or preliminary]
• Containment: [done / in progress]
• Customer communication: [sent / planned / not required]
• Lessons learned: [due date]
```

---

## PM Methodology — R&D Phase Gates

Apply this lifecycle to all cybersecurity R&D projects:

```
PHASE 1 — DISCOVERY
  Outputs: Threat model, requirements, risk register
  Gate criteria: Threat model approved, scope locked

PHASE 2 — ARCHITECTURE & DESIGN
  Outputs: Security architecture doc, data flow diagrams, API contracts
  Gate criteria: Architecture review board sign-off, no HIGH-severity design risks open

PHASE 3 — DEVELOPMENT
  Outputs: Feature builds, unit tests, security controls integrated
  Gate criteria: Code review complete, SAST/DAST clean, no critical CVEs

PHASE 4 — SECURITY VALIDATION
  Outputs: Pen test report, vulnerability remediation, compliance evidence
  Gate criteria: All CRITICAL/HIGH findings closed or accepted with waiver

PHASE 5 — LAUNCH READINESS
  Outputs: Runbook, rollback plan, monitoring in place, comms ready
  Gate criteria: All gates passed, exec sign-off, launch window agreed

PHASE 6 — POST-LAUNCH MONITORING
  Outputs: Incident dashboard, SLA report, retro document
  Gate criteria: 30-day stability window, no P1 incidents
```

---

## Tone Calibration

| Situation | Tone |
|-----------|------|
| Everything on track | Confident, brief — don't over-explain |
| Minor delay, plan in place | Direct, own it, lead with recovery plan |
| Significant risk, no mitigation yet | Honest, factual, ask for decision |
| Security incident | Calm, factual, no speculation, clear timeline |
| Board / investor update | Strategic framing — market impact, not technical detail |

---

## Anti-Patterns to Avoid

❌ "The team has been working hard on..."
❌ "We are currently in the process of evaluating..."
❌ "There are a number of factors that could potentially..."
❌ Slides with more than 5 bullets
❌ Status updates with no RAG (Red / Amber / Green) signal
❌ Risk sections that describe risk without naming an owner
❌ Roadmaps without dates
❌ Asking for multiple decisions in one communication

---

## How to Use This Skill

### Provide the raw facts:
```
"Project Alpha is 2 weeks behind. The auth module redesign took longer.
Pen test is next month. No critical risks open. Need management to
approve a 2-week extension to avoid scope cut."
```

### Skill outputs:
A ready-to-paste executive update in the correct template, correct tone,
correct length — no editing needed.

### Invocation examples:
```
"Write a weekly status update for the B2C auth hardening project"
"Create a gate review brief for Phase 2 — architecture complete"
"Draft a risk brief — the pen test vendor is 3 weeks late"
"Build a board slide for the Q2 cybersecurity roadmap"
"Summarize the incident — auth service down 40 min, 8% of users affected"
"Create an exec update — we're on track, milestone hit this week"
```

---

## Workflow Integration

```
You have project data (status, risks, milestones)
    ↓
/cyber-exec-brief
    ↓
Claude selects the right template (status / risk / gate / board)
    ↓
Applies exec writing rules (short, bullets, RAG, owner, date)
    ↓
Outputs ready-to-use content
    ↓
Optionally: /create-issue  → log a risk as a tracked issue
            /excel-pm-planner → cross-reference against the timeline plan
            /create-plan → build a recovery plan if project is delayed
```
