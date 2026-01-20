---
name: create-plan
description: AI creates a detailed text file that explains how it will do the work, including the steps and technical choices. Triggers on keywords like create plan, implementation plan, architecture plan, design plan.
---

# Create Plan

This skill creates a comprehensive implementation plan before writing any code.

## Purpose

Transform exploration findings into a concrete, step-by-step execution plan that:
- Outlines all implementation steps
- Documents technical decisions
- Identifies files to modify/create
- Establishes clear success criteria
- Provides a roadmap for execution

## When to Use

- After completing `/exploration-phase`
- Before starting implementation
- When you need stakeholder approval
- For complex features requiring coordination
- To ensure all team members understand the approach

## How It Works

1. **Synthesize Exploration**: Convert findings into actionable steps
2. **Define Architecture**: Document technical decisions
3. **Create Timeline**: Order tasks logically
4. **Identify Dependencies**: Note what depends on what
5. **Document Plan**: Save as a readable markdown file

## Usage

```
/create-plan
```

Or specify what to plan:
```
"Create a plan for implementing the shopping cart feature"
```

## Plan Structure

### Standard Plan Template

```markdown
# Implementation Plan: [Feature Name]

## Overview
[Brief description of what we're building]

## Goals
- Primary goal
- Secondary goals
- Success criteria

## Technical Decisions

### Architecture
- [Key architectural choices]
- [Design patterns to use]
- [Technology selections]

### File Structure
```
src/
├── components/
│   └── NewComponent.tsx (CREATE)
├── services/
│   └── ExistingService.ts (MODIFY)
└── utils/
    └── helpers.ts (MODIFY)
```

### State Management
- [How state will be managed]
- [Which context/store to use]

### API Integration
- [Endpoints needed]
- [Request/response formats]

## Implementation Steps

### Phase 1: Foundation (Estimated: X mins)
1. [ ] Create base component structure
2. [ ] Set up state management
3. [ ] Define TypeScript interfaces

### Phase 2: Core Functionality (Estimated: X mins)
1. [ ] Implement main feature logic
2. [ ] Add API integration
3. [ ] Handle loading and error states

### Phase 3: User Interface (Estimated: X mins)
1. [ ] Build UI components
2. [ ] Add styling
3. [ ] Implement interactions

### Phase 4: Polish (Estimated: X mins)
1. [ ] Add error handling
2. [ ] Implement validation
3. [ ] Add accessibility features

### Phase 5: Testing (Estimated: X mins)
1. [ ] Write unit tests
2. [ ] Add integration tests
3. [ ] Manual testing

## Files to Modify

### Create New Files
- `src/components/ShoppingCart.tsx` - Main cart component
- `src/contexts/CartContext.tsx` - Cart state management
- `src/types/cart.ts` - TypeScript definitions
- `tests/cart.test.tsx` - Unit tests

### Modify Existing Files
- `src/App.tsx` - Add cart provider
- `src/components/Header.tsx` - Add cart icon
- `src/api/index.ts` - Add cart endpoints

## Dependencies

### Required
- None (using existing dependencies)

### Optional
- `react-toastify` - For cart notifications
- `lodash` - For cart calculations

## Risk Mitigation

### Identified Risks
1. **Cart state sync issues**
   - Mitigation: Use optimistic updates with rollback

2. **Performance with large carts**
   - Mitigation: Implement pagination/virtualization

3. **Race conditions on concurrent updates**
   - Mitigation: Add request debouncing

## Testing Strategy

### Unit Tests
- Cart state updates
- Cart calculations
- Item quantity validation

### Integration Tests
- Add to cart flow
- Remove from cart
- Update quantities
- Checkout process

### Manual Tests
- [ ] Cross-browser testing
- [ ] Mobile responsiveness
- [ ] Accessibility check
- [ ] Performance testing

## Rollback Plan

If issues arise:
1. Revert commit: `git revert [commit-hash]`
2. Feature flag off (if implemented)
3. Restore previous version

## Success Criteria

- [ ] Users can add items to cart
- [ ] Cart persists across sessions
- [ ] Cart updates in real-time
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Accessibility standards met

## Timeline

- Phase 1: 30 minutes
- Phase 2: 45 minutes
- Phase 3: 30 minutes
- Phase 4: 20 minutes
- Phase 5: 25 minutes
- **Total: ~2.5 hours**

## Approval

- [ ] Technical approach approved
- [ ] Timeline acceptable
- [ ] Dependencies confirmed
- [ ] Ready to execute

---
**Status**: Draft | Ready | Approved | In Progress | Completed
**Created**: [Date]
**Last Updated**: [Date]
```

## Example Plan

```markdown
# Implementation Plan: User Authentication

## Overview
Implement secure user authentication with email/password and social login options.

## Goals
- Enable user registration and login
- Secure password storage
- Support Google OAuth
- Session management

## Technical Decisions

### Architecture
- JWT-based authentication
- HttpOnly cookies for token storage
- Refresh token rotation
- bcrypt for password hashing

### File Structure
```
src/
├── auth/
│   ├── AuthContext.tsx (CREATE)
│   ├── AuthProvider.tsx (CREATE)
│   ├── LoginForm.tsx (CREATE)
│   └── RegisterForm.tsx (CREATE)
├── api/
│   └── auth.ts (CREATE)
├── hooks/
│   └── useAuth.ts (CREATE)
└── middleware/
    └── authMiddleware.ts (CREATE)
```

## Implementation Steps

### Phase 1: Backend Setup
1. [ ] Create auth endpoints (/login, /register, /logout)
2. [ ] Implement JWT generation and validation
3. [ ] Set up password hashing
4. [ ] Create user database schema

### Phase 2: Frontend Auth Context
1. [ ] Create AuthContext and AuthProvider
2. [ ] Implement useAuth hook
3. [ ] Add token management logic
4. [ ] Handle auth state persistence

### Phase 3: UI Components
1. [ ] Build LoginForm component
2. [ ] Build RegisterForm component
3. [ ] Add form validation
4. [ ] Implement error handling

### Phase 4: Protected Routes
1. [ ] Create ProtectedRoute component
2. [ ] Add auth middleware
3. [ ] Implement redirect logic
4. [ ] Handle unauthorized access

### Phase 5: OAuth Integration
1. [ ] Set up Google OAuth
2. [ ] Create OAuth callback handler
3. [ ] Link OAuth to existing accounts
4. [ ] Test OAuth flow

## Files to Modify

### Backend
- CREATE `server/routes/auth.js`
- CREATE `server/middleware/auth.js`
- CREATE `server/models/User.js`
- MODIFY `server/app.js` - Add auth routes

### Frontend
- CREATE `src/auth/*` - All auth components
- CREATE `src/api/auth.ts` - Auth API calls
- MODIFY `src/App.tsx` - Add AuthProvider
- MODIFY `src/router.tsx` - Add protected routes

## Dependencies
```json
{
  "jsonwebtoken": "^9.0.0",
  "bcryptjs": "^2.4.3",
  "express-validator": "^7.0.0",
  "@react-oauth/google": "^0.12.0"
}
```

## Security Considerations
- Password strength requirements
- Rate limiting on auth endpoints
- CSRF protection
- XSS prevention
- SQL injection prevention

## Testing Strategy
- Unit tests for auth logic
- Integration tests for auth flow
- Security testing for vulnerabilities
- Load testing for auth endpoints

## Success Criteria
- [ ] Users can register with email/password
- [ ] Users can login securely
- [ ] Sessions persist correctly
- [ ] Google OAuth works
- [ ] All security tests pass
- [ ] No authentication bypasses

## Timeline
Total: ~4-5 hours

**Status**: Ready for Approval
```

## Plan File Location

Plans are saved to:
```
.plans/
├── PLAN-[feature-name]-[date].md
└── CURRENT_PLAN.md (symlink to active plan)
```

## Best Practices

1. **Be Specific**: Don't say "add functionality" - detail exactly what
2. **Order Logically**: Dependencies first, then features
3. **Estimate Realistically**: Add buffer time for unknowns
4. **Consider Rollback**: Always have a way to undo
5. **Include Testing**: Tests are part of the plan, not an afterthought
6. **Document Decisions**: Explain why you chose this approach
7. **Get Approval**: Review plan before executing

## Plan Review Checklist

Before approving a plan:

### Completeness
- [ ] All steps clearly defined
- [ ] All files identified
- [ ] Dependencies listed
- [ ] Testing strategy included

### Feasibility
- [ ] Technical approach is sound
- [ ] Timeline is realistic
- [ ] Resources available
- [ ] No blocking issues

### Quality
- [ ] Follows project standards
- [ ] Security considered
- [ ] Performance optimized
- [ ] Accessible by default

### Communication
- [ ] Plan is readable
- [ ] Decisions explained
- [ ] Risks identified
- [ ] Success criteria clear

## Integration with Workflow

```
/exploration-phase
    ↓
    [Understand the task]
    ↓
/create-plan  ← YOU ARE HERE
    ↓
    [Review and approve plan]
    ↓
/execute-plan
    ↓
/review
```

## Tips

1. **Start with Why**: Explain the reasoning behind decisions
2. **Think in Phases**: Break complex tasks into manageable chunks
3. **Consider Alternatives**: Note why you chose this approach over others
4. **Plan for Failure**: What if something goes wrong?
5. **Include Examples**: Show expected inputs/outputs
6. **Reference Standards**: Link to style guides, patterns, docs
7. **Keep Updated**: Update plan as you learn new information

## Common Mistakes to Avoid

❌ **Too Vague**: "Build the feature"
✅ **Specific**: "Create CartItem component with quantity controls"

❌ **No Order**: Random list of tasks
✅ **Logical Flow**: Dependencies first, then features

❌ **Missing Tests**: Only implementation, no testing
✅ **Test Included**: Each phase has corresponding tests

❌ **Unrealistic**: "Complete in 1 hour"
✅ **Realistic**: "Complete in 4-5 hours with testing"

## Output

The plan skill produces:
1. Detailed markdown file in `.plans/` directory
2. Checklist format for easy tracking
3. Clear approval status
4. Ready for `/execute-plan`

**Next Step**: Review the plan, get approval, then proceed to `/execute-plan`
