# Slash Commands Guide - AI Development Workflow

This repository includes a comprehensive set of slash commands inspired by professional AI-assisted development workflows. These commands help structure the software development process from exploration to documentation.

## 📋 Table of Contents

- [Overview](#overview)
- [Available Commands](#available-commands)
- [Installation](#installation)
- [Workflow](#workflow)
- [Usage](#usage)
- [For Claude Code Users](#for-claude-code-users)
- [For Cursor IDE Users](#for-cursor-ide-users)
- [Command Details](#command-details)
- [Best Practices](#best-practices)
- [Examples](#examples)

---

## Overview

This command suite implements a structured AI development workflow:

1. **Exploration** - Understand the task and codebase
2. **Planning** - Create detailed implementation plans
3. **Execution** - Implement code following the plan
4. **Review** - Self-review for bugs and issues
5. **Peer Review** - Multi-perspective code review
6. **Documentation** - Update all relevant docs
7. **Issue Tracking** - Log bugs and features

---

## Available Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/create-issue` | Record bugs, features, or ideas | Found a bug or have a feature idea |
| `/exploration-phase` | Understand task and codebase | Before starting implementation |
| `/create-plan` | Create implementation plan | After exploration, before coding |
| `/execute-plan` | Implement the code | Execute approved plan |
| `/review` | Self-review code | After implementation |
| `/peer-review` | Multi-model code review | After self-review |
| `/update-docs` | Update documentation | After peer review approval |

---

## Installation

### For Claude Code

Commands are automatically available as Skills. They're located in:
```
.claude/skills/
├── create-issue/
├── exploration-phase/
├── create-plan/
├── execute-plan/
├── review/
├── peer-review/
└── update-docs/
```

No setup required - just use them!

### For Cursor IDE

Commands are located in:
```
.cursor/commands/
├── create-issue.md
├── exploration-phase.md
├── create-plan.md
├── execute-plan.md
├── review.md
├── peer-review.md
└── update-docs.md
```

Access by typing `/` in Cursor's chat input.

---

## Workflow

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  💡 Have a Task                                 │
│  ↓                                              │
│  1. /create-issue (optional)                    │
│     └─ Document the requirement                 │
│  ↓                                              │
│  2. /exploration-phase                          │
│     ├─ Understand requirements                  │
│     ├─ Analyze codebase                         │
│     ├─ Ask questions                            │
│     └─ Identify challenges                      │
│  ↓                                              │
│  3. /create-plan                                │
│     ├─ Define technical approach                │
│     ├─ Break into phases                        │
│     ├─ List all files                           │
│     └─ Get approval                             │
│  ↓                                              │
│  4. /execute-plan                               │
│     ├─ Implement phase by phase                 │
│     ├─ Track progress                           │
│     ├─ Test as you go                           │
│     └─ Commit regularly                         │
│  ↓                                              │
│  5. /review                                     │
│     ├─ Check logic & correctness                │
│     ├─ Find security issues                     │
│     ├─ Identify performance problems            │
│     ├─ Verify code quality                      │
│     └─ Create review report                     │
│  ↓                                              │
│  6. Fix Critical Issues                         │
│  ↓                                              │
│  7. /peer-review                                │
│     ├─ Security perspective                     │
│     ├─ Performance perspective                  │
│     ├─ Accessibility perspective                │
│     ├─ Code quality perspective                 │
│     └─ Consolidated report                      │
│  ↓                                              │
│  8. Fix All Issues                              │
│  ↓                                              │
│  9. /update-docs                                │
│     ├─ Update README                            │
│     ├─ Update API docs                          │
│     ├─ Update component docs                    │
│     ├─ Update CHANGELOG                         │
│     └─ Create migration guide                   │
│  ↓                                              │
│  ✅ Ready for Production                        │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Usage

### Quick Start

1. **Start with exploration:**
   ```
   /exploration-phase
   ```

2. **Create a plan:**
   ```
   /create-plan
   ```

3. **Execute the plan:**
   ```
   /execute-plan
   ```

4. **Review your work:**
   ```
   /review
   ```

5. **Get peer review:**
   ```
   /peer-review
   ```

6. **Update docs:**
   ```
   /update-docs
   ```

### Creating Issues

```
/create-issue

"I found a bug where the login button doesn't work on mobile"
```

The AI will create a properly formatted issue report.

---

## For Claude Code Users

### Accessing Skills

Skills are automatically available in `.claude/skills/`. Claude will suggest them based on context or you can invoke explicitly:

```
"Use the exploration-phase skill to analyze this feature request"
```

Or simply describe what you want:
```
"I need to add user authentication, help me explore the current setup first"
```

### Skills Trigger Keywords

- **create-issue**: "create issue", "log bug", "track feature"
- **exploration-phase**: "explore codebase", "understand task", "analyze requirements"
- **create-plan**: "create plan", "implementation plan", "design plan"
- **execute-plan**: "execute plan", "implement plan", "build feature"
- **review**: "review code", "self review", "check code"
- **peer-review**: "peer review", "second opinion", "cross review"
- **update-docs**: "update docs", "update documentation", "document changes"

---

## For Cursor IDE Users

### Accessing Commands

Type `/` in Cursor's chat input to see all available commands.

```
/create-plan
```

Commands are stored as markdown files in `.cursor/commands/` and will appear in Cursor's command palette.

### Customizing Commands

Edit the `.md` files in `.cursor/commands/` to customize prompts:

```bash
# Edit a command
nano .cursor/commands/create-plan.md
```

---

## Command Details

### /create-issue

**Purpose**: Document bugs, features, and ideas

**What it does:**
- Asks clarifying questions
- Creates properly formatted issue
- Categorizes (Bug/Feature/Enhancement)
- Sets priority
- Suggests labels
- Can submit to GitHub/Linear/Jira

**Output**:
- Formatted issue report
- Saved to `.issues/` directory
- Optional direct submission

---

### /exploration-phase

**Purpose**: Understand before implementing

**What it does:**
- Clarifies requirements
- Analyzes existing codebase
- Identifies patterns and conventions
- Maps dependencies
- Finds potential challenges
- Asks questions
- Provides recommendations

**Output**:
- Exploration report
- List of questions
- Risk assessment
- Recommended approach

---

### /create-plan

**Purpose**: Plan the implementation

**What it does:**
- Synthesizes exploration findings
- Defines technical decisions
- Breaks work into phases
- Identifies all files to create/modify
- Estimates effort
- Documents risks
- Establishes success criteria

**Output**:
- Detailed implementation plan
- Saved to `.plans/` directory
- Ready for approval

---

### /execute-plan

**Purpose**: Implement the code

**What it does:**
- Loads the approved plan
- Implements phase by phase
- Tracks progress
- Tests continuously
- Commits regularly
- Documents deviations
- Updates plan with status

**Output**:
- Working code
- Tests
- Git commits
- Updated plan with progress

---

### /review

**Purpose**: Self-review for quality

**What it does:**
- Checks logic and correctness
- Scans for security vulnerabilities
- Identifies performance issues
- Assesses code quality
- Verifies error handling
- Checks accessibility
- Creates review report

**Output**:
- Review report
- Categorized issues (Critical/High/Medium)
- Specific fixes
- Saved to `.reviews/` directory

---

### /peer-review

**Purpose**: Multi-perspective review

**What it does:**
- Security-focused review
- Performance-focused review
- Accessibility-focused review
- Code quality review
- Cross-validates findings
- Creates consolidated report
- Approval/blocking decision

**Output**:
- Multiple perspective reviews
- Consolidated findings
- Priority matrix
- Action items

---

### /update-docs

**Purpose**: Synchronize documentation

**What it does:**
- Updates README
- Documents API changes
- Updates component docs
- Updates CHANGELOG
- Creates migration guides
- Updates architecture docs
- Adds usage examples

**Output**:
- Updated documentation files
- Version-tagged changes
- Migration guide (if needed)

---

## Best Practices

### 1. Don't Skip Exploration

Always start with `/exploration-phase` for non-trivial tasks. Understanding saves time.

### 2. Get Plan Approval

Review the plan before executing. It's easier to change a plan than code.

### 3. Track Progress

Update the plan file as you execute to track what's done.

### 4. Test Continuously

Don't wait until the end to test. Test after each phase.

### 5. Fix Critical Issues Immediately

Don't proceed with peer review if self-review finds critical bugs.

### 6. Document As You Go

Update docs right after implementation, not weeks later.

### 7. Use Issues for Tracking

Create issues for bugs discovered during review to track fixes.

---

## Examples

### Example 1: Adding a New Feature

```bash
# Step 1: Explore
User: "I need to add a shopping cart feature"
AI: /exploration-phase

# Step 2: Plan
User: "Create a plan for the shopping cart"
AI: /create-plan

# Step 3: Execute
User: "Execute the shopping cart plan"
AI: /execute-plan

# Step 4: Review
User: "Review the shopping cart code"
AI: /review

# Step 5: Peer Review
User: "Get peer review on the shopping cart"
AI: /peer-review

# Step 6: Document
User: "Update docs for the shopping cart feature"
AI: /update-docs
```

### Example 2: Fixing a Bug

```bash
# Document the bug
User: "Create an issue - login button not working on mobile"
AI: /create-issue

# Understand the problem
User: "Explore why the login button fails on mobile"
AI: /exploration-phase

# Plan the fix
User: "Create a plan to fix the mobile login issue"
AI: /create-plan

# Implement
User: "Execute the login fix plan"
AI: /execute-plan

# Review
User: "Review the login fix"
AI: /review

# Update docs
User: "Update docs with the login fix"
AI: /update-docs
```

### Example 3: Refactoring

```bash
# Explore current code
User: "Explore the authentication module for refactoring"
AI: /exploration-phase

# Create refactoring plan
User: "Create a plan to refactor auth to use JWT"
AI: /create-plan

# Execute refactoring
User: "Execute the auth refactoring plan"
AI: /execute-plan

# Review changes
User: "Review the refactored auth code"
AI: /review

# Peer review (important for security changes)
User: "Peer review the authentication changes"
AI: /peer-review

# Document changes
User: "Update docs for the new auth system"
AI: /update-docs
```

---

## File Structure

```
MyFirstRepo/
├── .claude/
│   └── skills/
│       ├── create-issue/
│       │   └── SKILL.md
│       ├── exploration-phase/
│       │   └── SKILL.md
│       ├── create-plan/
│       │   └── SKILL.md
│       ├── execute-plan/
│       │   └── SKILL.md
│       ├── review/
│       │   └── SKILL.md
│       ├── peer-review/
│       │   └── SKILL.md
│       └── update-docs/
│           └── SKILL.md
├── .cursor/
│   └── commands/
│       ├── create-issue.md
│       ├── exploration-phase.md
│       ├── create-plan.md
│       ├── execute-plan.md
│       ├── review.md
│       ├── peer-review.md
│       └── update-docs.md
├── .plans/              (Created during workflow)
├── .reviews/            (Created during workflow)
├── .issues/             (Created during workflow)
└── SLASH_COMMANDS_GUIDE.md (This file)
```

---

## Workflow Benefits

### ✅ Systematic Approach
- No skipped steps
- Consistent quality
- Clear progress tracking

### ✅ Better Code Quality
- Multiple review passes
- Catches bugs early
- Security considered
- Performance optimized

### ✅ Comprehensive Documentation
- Always up to date
- Clear examples
- Migration guides
- Architecture documented

### ✅ Team Alignment
- Plans can be reviewed
- Progress is visible
- Decisions documented
- Knowledge shared

### ✅ AI-Friendly
- Structured prompts
- Clear expectations
- Measurable outcomes
- Consistent results

---

## Tips for Success

1. **Be Thorough in Exploration**: Ask all questions upfront
2. **Review Plans Carefully**: Easier to change plans than code
3. **Commit Often**: Atomic commits with clear messages
4. **Test Everything**: Unit, integration, and manual tests
5. **Fix Issues Immediately**: Don't defer critical bugs
6. **Document Everything**: Future you will thank present you
7. **Use Issues**: Track all bugs and features
8. **Follow the Workflow**: Don't skip steps

---

## Inspiration

This workflow is inspired by professional AI-assisted development practices, particularly the methodology discussed by Zevi Arnovitz (Meta PM) in his approach to building with AI coding assistants.

**Key Principles:**
- Structure reduces cognitive load
- Multiple review passes catch more issues
- Documentation prevents knowledge loss
- Process creates consistency

---

## Support

- For Claude Code issues: https://github.com/anthropics/claude-code/issues
- For Cursor issues: https://cursor.com/docs
- For this workflow: Create an issue in this repository

---

## License

These commands are provided as-is for use in your projects. Modify and adapt as needed for your workflow.

---

**Happy Coding! 🚀**

Remember: The best code is well-planned, thoroughly tested, comprehensively reviewed, and properly documented.
