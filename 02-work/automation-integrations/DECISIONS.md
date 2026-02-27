# Architectural Decisions — Automation Integrations

## ADR-001: Monorepo for all integrations
**Decision**: Keep JIRA, Confluence, and shared utilities in a single project rather than separate repos.
**Reason**: Shared auth tokens, common retry/error handling utilities, easier cross-tool workflows.
**Status**: Active

## ADR-002: Python as primary language
**Decision**: Python over Node.js or PowerShell for automation scripts.
**Reason**: Better JIRA/Confluence SDK support (atlassian-python-api); consistent with rest of workspace.
**Status**: Pending validation

## ADR-003: Separate modules per integration
**Decision**: `jira/`, `confluence/`, `shared/` as first-class modules, not a flat file structure.
**Reason**: Each integration can evolve independently; shared utilities remain reusable.
**Status**: Active
