# Claude Workspace

A structured workspace for organizing AI agent development projects, learning resources, and documentation.

## Structure Overview

```
~/claude-workspace/
├── CLAUDE.md                  # Global preferences & coding standards
├── README.md                  # This file - Overview of all projects
│
├── .config/                   # Shared configurations & templates
│
├── 01-personal/               # Personal learning & practice projects
│   └── aws-ai-agent/          # AWS Bedrock AI Agent project
│
├── 02-work/                   # Work-related projects
│   ├── ai-foundry-agent/      # AI Foundry Agent project
│   └── automation-integrations/
│
├── 03-plans/                  # Plans, roadmaps & research
│
└── 04-reference/              # Knowledge base & cheatsheets
```

## Quick Navigation

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `01-personal/` | Personal learning projects | `aws-ai-agent/`, `sandbox/` |
| `02-work/` | Work projects | `ai-foundry-agent/`, `automation-integrations/` |
| `03-plans/` | Strategy & planning | `roadmaps/`, `research/` |
| `04-reference/` | Knowledge base | `cheatsheets/`, `patterns/` |

## Getting Started

1. Review the global `CLAUDE.md` for coding standards
2. Navigate to the relevant project directory
3. Check the project-specific `CLAUDE.md` and `README.md`
4. Use templates from `.config/templates/` for consistency

## Active Tracking

| File | Purpose |
|------|---------|
| [`TODO.md`](TODO.md) | Active and backlog tasks across all projects |
| [`DECISIONS.md`](DECISIONS.md) | Architectural decision log |
| [`.plans/`](.plans/) | Implementation plans (git-tracked) |
| [`.claude/COMMAND_REGISTRY.md`](.claude/COMMAND_REGISTRY.md) | All 14 available Claude skills |

## Contributing

- Follow the coding standards in `CLAUDE.md`
- Document decisions in `DECISIONS.md` files
- Keep `TODO.md` files updated with active tasks
