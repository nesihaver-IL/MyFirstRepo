# ADR Template — Architecture Decision Record

Use this template when making significant architectural decisions in a project. ADRs create a trail of reasoning for future developers (and future you).

---

## [ADR-XXX] — [Decision Title]

**Date**: YYYY-MM-DD  
**Status**: [Proposed | Accepted | Deprecated | Superseded By ADR-YYY]  
**Deciders**: [Names or roles of decision-makers]  
**Priority**: [High | Medium | Low]

### Problem Statement

[One paragraph describing the problem or question that prompted this decision. What constraint or requirement drove the need to choose?]

**Examples:**
- "We need to store activity data from Garmin webhooks and serve it to a dashboard"
- "Conversation history must persist across sessions without database overhead"

### Decision

[One clear statement of what was decided. This should be specific enough that someone else could implement it.]

**Format: "We will [action] [because/with/using] [constraint or technology]."**

### Rationale

Explain the reasoning behind the decision. This should cover:

- **Why this choice?**: What makes it suitable for this problem?
- **What were we optimizing for?**: Cost? Performance? Developer experience? Time to market?
- **What constraints shaped this?** Existing systems, team expertise, compliance requirements?

### Consequences

#### Positive Outcomes
- [Benefit 1] — [Why this matters for the project]
- [Benefit 2]
- [Benefit 3]

#### Tradeoffs & Risks
- [Tradeoff 1] — [Mitigation if available]
- [Risk 2] — [When this becomes a problem]
- [Limitation 3] — [Acceptable because...]

### Alternatives Considered

| Alternative | Why Not Chosen | Key Difference |
|-------------|---|---|
| [Alt 1] | [Reason] | [vs. our decision] |
| [Alt 2] | [Reason] | [vs. our decision] |
| [Alt 3] | [Reason] | [vs. our decision] |

### Implementation Notes

- **When was this implemented?**: If different from decision date
- **Who led implementation?**: Name/team
- **Key files/PRs**: Links to relevant code changes
- **Deployment impact**: Any breaking changes? Migration needed?

### Related Decisions

- Links to other ADRs this decision depends on or conflicts with
- [ADR-XXX] — [Related title]

### Future Review Date

**Suggested review**: [Date or condition, e.g., "Q3 2026" or "if performance > 500ms"]

Review this decision if:
- [Condition 1: e.g., "if user base grows beyond X"]
- [Condition 2: e.g., "if new framework Y becomes available"]
- [Condition 3: e.g., "if compliance requirements change"]

### Approval & Sign-Off

| Role | Approval | Notes |
|------|----------|-------|
| Tech Lead | ☐ | |
| Project Owner | ☐ | |
| Security Review | ☐ | |

---

## Examples of Good ADRs in This Workspace

See existing ADRs in:
- `01-personal/garmin-health/DECISIONS.md` — Architecture for health analytics system
- `01-personal/math-practice/DECISIONS.md` — Web app technology choices
- `01-personal/interview-coach/DECISIONS.md` — Coaching system design

When in doubt, reference one of these as a pattern.
