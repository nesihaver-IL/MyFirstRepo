# Exploration Phase

You are entering the exploration phase before implementation. Your goal is to thoroughly understand the task, analyze existing code, and clarify all requirements.

## Your Mission

Conduct a comprehensive exploration of the task and codebase before writing any code. This phase is about understanding, not implementing.

## Exploration Process

### 1. Clarify Requirements

Ask questions to understand:
- What exactly needs to be accomplished?
- Who are the users/stakeholders?
- What defines success for this task?
- What are the constraints or limitations?
- What should NOT change?
- Are there any deadlines or priorities?

### 2. Analyze Existing Codebase

Investigate:
- **Find Related Code**: Search for similar functionality
- **Understand Patterns**: Identify coding patterns and conventions used
- **Map Dependencies**: Understand how components relate
- **Review Architecture**: Study the overall structure
- **Check Tests**: Look at existing tests for similar features
- **Read Documentation**: Review any relevant docs

Use these commands to explore:
```bash
# Find related files
grep -r "keyword" --include="*.ts" --include="*.tsx"

# Understand structure
tree src/ -L 3

# Check dependencies
npm list | grep package-name
```

### 3. Assess Technical Landscape

Evaluate:
- Current technology stack
- Architecture patterns in use
- Performance considerations
- Security requirements
- Accessibility standards
- Browser/platform compatibility
- Testing strategy

### 4. Identify Challenges

Look for:
- Breaking changes required
- Integration complexities
- Performance impacts
- Security concerns
- Edge cases and corner cases
- Potential conflicts with existing code

### 5. Ask Clarifying Questions

Present questions in organized format:

**Functional Questions:**
- How should X work in scenario Y?
- What should happen when Z occurs?
- Should we handle edge case A?

**Technical Questions:**
- Which pattern should we follow: X or Y?
- Where should this code live?
- How should we manage state?
- What's the testing approach?

**Business Questions:**
- What's the priority level?
- Are there deadline constraints?
- Who needs to approve this?

## Output Format

Present your findings as:

```markdown
# Exploration Report: [Feature Name]

## 🎯 Understanding

[Summary of what you understand the task to be]

## 📁 Codebase Analysis

**Relevant Files Found:**
- path/to/file1.ts - [what it does]
- path/to/file2.tsx - [what it does]

**Patterns Identified:**
- [Pattern 1]: Used in X, Y, Z
- [Pattern 2]: State management approach

**Dependencies:**
- Existing: package-name@version
- May need: potential-package

## 🤔 Questions & Clarifications

### Critical Questions
1. [Question requiring immediate answer]
2. [Another critical question]

### Technical Decisions Needed
1. [Decision point A or B?]
2. [Approach X or Y?]

### Nice to Know
1. [Lower priority question]

## ⚠️ Potential Challenges

1. **Challenge 1**: [Description]
   - Impact: [What could go wrong]
   - Mitigation: [Possible solution]

2. **Challenge 2**: [Description]
   - Impact: [What could go wrong]
   - Mitigation: [Possible solution]

## 💡 Initial Recommendations

Based on exploration, I recommend:
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

**Reasoning**: [Why these recommendations]

## ✅ Ready for Next Steps

Once questions are answered, we can proceed to:
- Create a detailed implementation plan
- Define exact scope and approach
- Begin implementation
```

## Guidelines

- **Don't Assume**: Ask questions rather than guessing
- **Be Thorough**: Check all related areas
- **Document Findings**: Keep track of what you learn
- **Identify Risks**: Surface potential issues early
- **Validate Understanding**: Confirm your interpretation
- **Think Ahead**: Consider future implications
- **Stay Focused**: Don't go down unnecessary rabbit holes

## Important Reminders

- ❌ DO NOT write code during exploration
- ❌ DO NOT make changes to files
- ✅ DO read and analyze existing code
- ✅ DO ask clarifying questions
- ✅ DO document your findings
- ✅ DO identify potential approaches

The exploration phase sets the foundation for successful implementation. Take your time to understand fully before moving to planning.
