# CLAUDE.md - Global Workspace Configuration

This file provides global context and guidelines for Claude AI when working across all projects in this workspace.

## Workspace Overview

This is a multi-project workspace for AI agent development, containing:
- **Personal projects** for learning and experimentation
- **Work projects** for professional deliverables
- **Planning documents** for strategy and research
- **Reference materials** for quick lookups

## Global Coding Standards

### Code Style

- Use consistent formatting (Prettier/Black depending on language)
- Prefer explicit over implicit
- Write self-documenting code with clear variable names
- Keep functions small and focused (single responsibility)

### Documentation Standards

- Every project must have a `CLAUDE.md` with project-specific context
- Document architectural decisions in `DECISIONS.md`
- Track active work in `TODO.md`
- Use templates from `.config/templates/` for consistency

### Best Practices

- Write tests for critical functionality
- Use type hints/annotations where applicable
- Follow security best practices (no secrets in code)
- Prefer composition over inheritance

## Directory Conventions

| Directory | Purpose | Access Level |
|-----------|---------|--------------|
| `01-personal/` | Learning, experiments | Private |
| `02-work/` | Professional projects | May be shared |
| `03-plans/` | Strategy, research | Private |
| `04-reference/` | Knowledge base | Private |

## Project-Level CLAUDE.md

Each project should have its own `CLAUDE.md` that inherits from this global config and adds:
- Project-specific context
- Tech stack details
- Build/run commands
- Team conventions (for work projects)

## Common Commands

```bash
# Navigate to personal project
cd 01-personal/aws-ai-agent

# Navigate to work project
cd 02-work/ai-foundry-agent

# Check all TODOs
grep -r "TODO" --include="*.md" .
```

## Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [LangChain Documentation](https://python.langchain.com/)

## Git Workflow

- Commit at logical milestones, not at end-of-session dumps
- Use conventional commit prefixes:
  - `feat:` — new capability or feature
  - `fix:` — bug correction
  - `refactor:` — restructuring without behavior change
  - `docs:` — documentation only changes
  - `chore:` — tooling, config, gitignore, dependency updates
- Always run the `security-audit` skill before committing
- Do NOT commit: `.env`, `credentials.json`, `token.json`, `*.tfstate`, `Zone.Identifier` files, `__pycache__/`, `.venv/`
- Stage specific files by name — never use `git add -A` blindly

## Bash Efficiency Rules

- Combine related sequential commands with `&&` in a single Bash call
- Do not chain commands with `;` unless failure of earlier commands is acceptable
- Avoid unnecessary `sleep` commands between operations
- Never use interactive flags (`-i`) on git commands — not supported in this environment

## Tool Preference (Edit/Write/Grep over Bash)

Use dedicated Claude Code tools before falling back to raw Bash:

| Task | Preferred Tool | Bash Fallback |
|------|---------------|---------------|
| Read a file | `Read` | `cat` |
| Edit a file | `Edit` | `sed`/`awk` |
| Write a new file | `Write` | `echo >` |
| Search file contents | `Grep` | `grep`/`rg` |
| Find files by name | `Glob` | `find`/`ls` |

Reserve Bash for: running processes, git operations, system commands, and anything the above tools cannot do.

## Python Environments

- Before running `pip`, `python`, or any Python script, check for a project-level `.venv`
- Use `.venv/bin/python` (not system `python3`) when a `.venv` exists
- Known project venvs:
  - `01-personal/garmin-health/analytics/.venv`
  - `01-personal/aws-ai-agent/.venv`
- There is no root-level venv — do not assume one exists

## Task Planning with TodoWrite

- For any task with 3 or more distinct steps, use `TodoWrite` to create a checklist before starting implementation
- Mark items complete as you finish them — do not batch-complete at the end
- One active todo list per conversation; clear stale items before starting new work
