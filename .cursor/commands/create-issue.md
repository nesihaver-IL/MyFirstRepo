# Create Issue

You are tasked with creating a well-structured issue report for the project management system.

## Your Task

Gather information about the bug, feature, or idea and create a properly formatted issue that can be submitted to GitHub Issues, Linear, Jira, or other project management tools.

## Process

1. **Understand the Issue Type**
   - Ask if this is a Bug, Feature Request, or Idea/Enhancement
   - Gather relevant details based on type

2. **Collect Information**

   For **Bugs**:
   - Description of the problem
   - Steps to reproduce
   - Expected behavior vs actual behavior
   - Environment details (OS, browser, version)
   - Priority level
   - Possible solution (if any)

   For **Features**:
   - Feature description
   - Problem it solves
   - Proposed solution
   - User story format: "As a [user], I want [feature] so that [benefit]"
   - Acceptance criteria
   - Priority level

   For **Ideas/Enhancements**:
   - Idea description
   - Context and value
   - Implementation notes
   - Impact assessment
   - Priority level

3. **Format the Issue**

   Use this template:

   ```markdown
   # [Title]

   ## Type
   [Bug | Feature | Enhancement]

   ## Description
   [Clear description]

   ## [Context-Specific Sections]
   [Steps to Reproduce for bugs]
   [User Story for features]
   [Implementation Notes for enhancements]

   ## Priority
   [Low | Medium | High | Critical]

   ## Labels
   [Suggested labels]
   ```

4. **Submit or Save**
   - If GitHub CLI is available, offer to create the issue directly
   - Otherwise, format for manual submission
   - Save to `.issues/` directory for tracking

## Example Output

```markdown
# Login button not working on mobile

## Type
Bug

## Description
The login button is unresponsive when tapped on mobile devices (iOS and Android).

## Steps to Reproduce
1. Open the app on a mobile device
2. Navigate to the login page
3. Tap the login button
4. Nothing happens

## Expected Behavior
Login form should submit and user should be authenticated.

## Actual Behavior
Button press has no effect. No error messages shown.

## Environment
- iOS 17.2 (Safari)
- Android 13 (Chrome)
- App version: 1.2.0

## Priority
High

## Possible Solution
May be related to touch event handling. Check if click events need to be replaced with touch events.

## Labels
- bug
- mobile
- high-priority
- authentication
```

## Guidelines

- Be specific and detailed
- Include all relevant context
- Set appropriate priority
- Suggest labels for categorization
- Offer to create the issue via CLI if available
- Save locally if CLI not available

After gathering the information, create a well-formatted issue ready for submission.
