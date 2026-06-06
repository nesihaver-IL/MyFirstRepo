---
name: exploration-phase
description: AI studies the task, reads existing code, and asks questions to understand the goal and its limits. Triggers on keywords like explore codebase, understand task, analyze requirements, clarify scope.
---

# Exploration Phase

This skill conducts a thorough exploration and analysis of your task before implementation begins.

## Purpose

Before writing any code, the AI needs to understand:
- What you're trying to accomplish
- The existing codebase structure
- Technical constraints and requirements
- Potential challenges and edge cases
- Best approach for implementation

## When to Use

- Starting a new feature
- Fixing a complex bug
- Refactoring existing code
- Working with unfamiliar codebases
- Need to understand scope before planning

## How It Works

The exploration phase follows a systematic approach:

### 1. Requirement Clarification
- Ask questions about the task
- Understand user goals
- Identify success criteria
- Define scope and boundaries

### 2. Codebase Analysis
- Read relevant existing code
- Understand current architecture
- Identify dependencies
- Find related files and modules

### 3. Technical Discovery
- Assess technical constraints
- Identify potential challenges
- Research best practices
- Consider edge cases

### 4. Question Generation
- Ask clarifying questions
- Validate assumptions
- Confirm approach
- Get feedback on direction

## Usage

Invoke the exploration phase:

```
/exploration-phase
```

Or describe what you need to explore:
```
"I need to add user authentication, but first let me understand the current setup"
```

## Exploration Process

### Phase 1: Initial Understanding

**Questions to Ask:**
- What is the main goal of this task?
- Who are the users/stakeholders?
- What does success look like?
- Are there any deadlines or constraints?
- What should NOT change?

### Phase 2: Codebase Investigation

**Areas to Explore:**
```bash
# Find relevant files
- Search for related functionality
- Identify entry points
- Map dependencies
- Review existing patterns
```

**Key Files to Read:**
- Main application files
- Configuration files
- Related feature implementations
- Tests for similar features
- Documentation

### Phase 3: Technical Analysis

**Considerations:**
- Current tech stack
- Architecture patterns used
- Performance requirements
- Security considerations
- Scalability needs
- Browser/platform compatibility

### Phase 4: Risk Assessment

**Identify:**
- Breaking changes
- Integration challenges
- Performance impacts
- Security vulnerabilities
- Testing complexity

## Example Exploration Session

```
User: "Add a shopping cart to the e-commerce site"

AI: Let me explore this task before we create a plan.

🔍 EXPLORATION PHASE - Shopping Cart Feature

**Understanding the Goal:**
1. What kind of shopping cart do you need?
   - Session-based or persistent?
   - Guest checkout support?
   - Multi-item management?

2. User experience expectations?
   - Inline updates or page refresh?
   - Quantity adjustments?
   - Save for later functionality?

**Analyzing Existing Code:**
- Found: `/src/products/ProductList.tsx` - Product display
- Found: `/src/api/products.ts` - Product API calls
- Found: `/src/contexts/UserContext.tsx` - User state management
- Missing: Cart state management
- Missing: Cart persistence logic

**Technical Questions:**
1. Should cart persist across sessions?
2. Where should we store cart state? (localStorage, database, Redux?)
3. Do we need cart synchronization across devices?
4. What happens to cart on logout?

**Identified Patterns:**
- Using React Context for state
- API calls through centralized service
- TypeScript for type safety
- Component-based architecture

**Potential Challenges:**
- Cart synchronization with inventory
- Handling price changes
- Managing cart expiration
- Concurrent cart modifications

**Recommendations:**
Based on exploration, I suggest:
1. Use React Context for cart state
2. Persist to localStorage + backend
3. Implement optimistic updates
4. Add cart validation on checkout

Ready to proceed to /create-plan?
```

## Exploration Checklist

Use this checklist to ensure thorough exploration:

### Requirements
- [ ] Core functionality clearly defined
- [ ] Success criteria established
- [ ] User stories documented
- [ ] Edge cases identified
- [ ] Constraints understood

### Codebase
- [ ] Relevant files located
- [ ] Current patterns understood
- [ ] Dependencies mapped
- [ ] Existing tests reviewed
- [ ] Documentation read

### Technical
- [ ] Architecture decisions made
- [ ] Tech stack compatibility verified
- [ ] Performance implications considered
- [ ] Security risks assessed
- [ ] Testing strategy outlined

### Communication
- [ ] Clarifying questions asked
- [ ] Assumptions validated
- [ ] Approach confirmed
- [ ] Concerns raised
- [ ] Next steps agreed

## Output Format

The exploration phase produces:

1. **Findings Summary**
   - What was discovered
   - Key insights
   - Important constraints

2. **Questions List**
   - Clarifications needed
   - Decisions to make
   - Approvals required

3. **Risk Assessment**
   - Potential issues
   - Mitigation strategies
   - Dependencies

4. **Recommendations**
   - Suggested approach
   - Alternative options
   - Next steps

## Integration with Other Skills

**Typical Workflow:**
```
/exploration-phase
    ↓
[Answer questions, review findings]
    ↓
/create-plan
    ↓
/execute-plan
    ↓
/review
```

## Best Practices

1. **Ask Before Assuming**: Don't make assumptions about requirements
2. **Read Before Writing**: Understand existing code first
3. **Document Findings**: Keep track of discoveries
4. **Validate Understanding**: Confirm your interpretation
5. **Consider Alternatives**: Explore multiple approaches
6. **Think About Edge Cases**: Don't just focus on happy path
7. **Assess Impact**: Consider wider system effects

## Advanced Exploration Techniques

### Codebase Mapping
```bash
# Find all files related to feature
grep -r "authentication" --include="*.ts" --include="*.tsx"

# Understand file structure
tree src/ -L 3

# Check dependencies
npm list | grep auth
```

### Pattern Recognition
- Identify coding conventions
- Note naming patterns
- Understand folder structure
- Review component patterns
- Check state management approach

### Dependency Analysis
- Map component relationships
- Identify shared utilities
- Find external dependencies
- Check version compatibility

## Tips for Effective Exploration

1. **Start Broad, Then Narrow**: Begin with high-level understanding, then drill down
2. **Use Search Effectively**: Grep/search for keywords to find relevant code
3. **Read Tests**: Tests often reveal expected behavior
4. **Check Documentation**: README, comments, and docs provide context
5. **Trace Data Flow**: Follow how data moves through the system
6. **Identify Patterns**: Look for established patterns to follow
7. **Ask "Why"**: Understand the reasoning behind current implementations

## Common Questions to Ask

### Functional
- What should happen in this scenario?
- How should errors be handled?
- What's the expected user experience?
- Are there any special cases?

### Technical
- What's the current architecture?
- Which patterns should I follow?
- Are there performance requirements?
- What's the testing strategy?

### Business
- What's the priority?
- Are there deadlines?
- Who needs to approve?
- What's the impact if delayed?

## Exploration Complete

Once exploration is done, you should have:
- ✅ Clear understanding of the goal
- ✅ Knowledge of existing code
- ✅ Identified challenges
- ✅ Validated assumptions
- ✅ Recommended approach

**Next Step**: `/create-plan` to document the implementation strategy
