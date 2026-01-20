---
name: create-issue
description: Records a bug, feature, or idea and sends it to a project management tool like Linear, GitHub Issues, or Jira. Triggers on keywords like create issue, log bug, track feature, report issue.
---

# Create Issue

This skill helps you document and track bugs, features, and ideas in your project management system.

## Purpose

Automatically creates well-structured issue reports that can be sent to:
- GitHub Issues
- Linear
- Jira
- Other project management tools

## When to Use

- Discovered a bug while coding
- Want to track a new feature idea
- Need to document a problem for later
- Creating a backlog item

## How It Works

1. **Gather Information**: Collects details about the issue
2. **Categorize**: Determines if it's a bug, feature, or idea
3. **Format**: Creates a properly structured issue description
4. **Submit**: Sends to your configured project management tool

## Usage

Simply invoke this skill when you need to create an issue:

```
/create-issue
```

Or describe the issue naturally:
```
"I found a bug in the authentication flow - users can't reset passwords"
```

## Issue Template

The skill creates issues with the following structure:

### Bug Report
```markdown
## Bug Description
[Clear description of the problem]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [Operating system]
- Browser/Node version: [Version]
- Other relevant details

## Priority
[Low/Medium/High/Critical]

## Possible Solution
[Optional: Suggestions for fixing]
```

### Feature Request
```markdown
## Feature Description
[Clear description of the feature]

## Problem Statement
[What problem does this solve?]

## Proposed Solution
[How should it work?]

## Alternatives Considered
[Other approaches considered]

## User Story
As a [user type], I want [feature] so that [benefit]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Priority
[Low/Medium/High/Critical]
```

### Idea/Enhancement
```markdown
## Idea Description
[Clear description of the idea]

## Context
[Why is this valuable?]

## Implementation Notes
[Technical considerations]

## Impact
[Who benefits and how?]

## Priority
[Low/Medium/High/Critical]
```

## Integration with Tools

### GitHub Issues
```bash
gh issue create --title "Issue title" --body "$(cat issue_description.md)"
```

### Linear
```bash
# Requires Linear CLI or API integration
linear issue create --title "Issue title" --description "Issue description"
```

### Manual Tracking
If no tool is configured, the skill will:
1. Create a markdown file in `.issues/` directory
2. Add to `BACKLOG.md`
3. Provide formatted text to copy/paste

## Configuration

Add to your `.claude/config.yml` or project settings:

```yaml
issue_tracker:
  type: github  # Options: github, linear, jira, manual
  default_labels:
    - bug
    - enhancement
  default_assignee: your-username
  default_project: your-project
```

## Examples

### Example 1: Quick Bug Report
```
User: "Create issue - login button doesn't work on mobile"

AI: I'll create a bug report for the mobile login issue.

📝 Created Issue #123: Login button not functional on mobile devices

Type: Bug
Priority: High
Status: Open

The issue has been logged to GitHub Issues.
```

### Example 2: Feature Request
```
User: "Create issue for adding dark mode support"

AI: I'll create a feature request for dark mode.

📝 Created Issue #124: Add dark mode support

Type: Feature
Priority: Medium
Status: Backlog

Feature request includes:
- User story
- Acceptance criteria
- Implementation considerations

Issue created in Linear.
```

## Best Practices

1. **Be Specific**: Provide clear, detailed descriptions
2. **Add Context**: Include relevant code snippets or screenshots
3. **Set Priority**: Indicate urgency appropriately
4. **Label Properly**: Use consistent labels for easy filtering
5. **Link Related Issues**: Reference related bugs or features

## Workflow Integration

This skill works best when combined with:
- `/exploration-phase` - Understand the issue before logging
- `/create-plan` - Plan the fix after creating the issue
- `/execute-plan` - Implement the solution
- `/update-docs` - Document the resolution

## Output

The skill will:
1. Create the issue in your configured system
2. Return the issue URL and number
3. Add to local tracking (if configured)
4. Optionally notify team members

## Tips

- Use templates for consistent formatting
- Tag issues with relevant labels
- Assign priority based on impact
- Link to related code or documentation
- Include reproduction steps for bugs
- Define acceptance criteria for features
