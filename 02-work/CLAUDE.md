# CLAUDE.md - Work Projects

## Output Formatting Rules

- **NEVER use em dash "—"** in any output, content, or deliverable. Always use a regular hyphen "-" instead.

## Purpose

This directory contains work-related projects that may be shared with team members or stakeholders.

## Team Conventions

- Follow company coding standards
- Document all architectural decisions
- Maintain clear status updates
- Create handoff documentation

## Projects

| Project | Status | Description |
|---------|--------|-------------|
| `ai-foundry-agent/` | Active | Azure AI Foundry Agent |
| `automation-integrations/` | Ongoing | JIRA/Confluence integrations |

## Documentation Standards

### For Stakeholders
- Keep `STATUS.md` updated with current progress
- Document decisions in `DECISIONS.md` with business context
- Maintain `HANDOFF-NOTES.md` for team transitions

### For Development
- Follow project-specific `CLAUDE.md` guidelines
- Write comprehensive tests
- Document API specifications

## Code Quality Requirements

- All code must pass linting
- Unit test coverage > 80%
- Integration tests for critical paths
- Code reviews required before merge

## Security Requirements

- No secrets in code (use environment variables)
- Follow least privilege principle
- Regular dependency updates
- Security scanning in CI/CD
