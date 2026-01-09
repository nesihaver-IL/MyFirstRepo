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
