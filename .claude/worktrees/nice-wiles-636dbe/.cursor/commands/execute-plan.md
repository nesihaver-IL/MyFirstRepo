# Execute Plan

You are now implementing code based on the approved implementation plan. Follow the plan step-by-step, track progress, and handle issues as they arise.

## Your Mission

Write clean, tested code that implements the approved plan exactly as documented. Track your progress, validate each step, and adapt only when necessary (documenting deviations).

## Execution Process

### 1. Load and Review Plan

- Read the plan file from `.plans/` directory
- Understand all phases and steps
- Note any special considerations
- Check dependencies and prerequisites

### 2. Set Up Development Environment

```bash
# Create feature branch
git checkout -b feature/[feature-name]

# Ensure dependencies are installed
npm install

# Run tests to establish baseline
npm test

# Verify build works
npm run build
```

### 3. Execute Phase by Phase

For each phase:

1. **Read Phase Requirements**
   - Understand what needs to be done
   - Check dependencies from previous phases
   - Note acceptance criteria

2. **Implement Code**
   - Write clean, typed code
   - Follow project conventions
   - Add appropriate comments
   - Handle errors properly

3. **Test As You Go**
   ```bash
   # After each file/component
   npm test -- YourComponent

   # Check types
   npm run type-check

   # Lint
   npm run lint
   ```

4. **Validate Step**
   - Ensure functionality works
   - Check acceptance criteria
   - Verify no regressions

5. **Update Plan**
   - Mark step as complete ✅
   - Note any deviations
   - Update time estimates

6. **Commit Progress**
   ```bash
   git add .
   git commit -m "feat: [what you implemented]

   - [Detail 1]
   - [Detail 2]

   Part of Phase X: [Phase name]
   Ref: .plans/PLAN-[feature]-[date].md"
   ```

### 4. Track Progress

Update the plan file with progress indicators:

```markdown
### Phase 1: Foundation ✅ COMPLETED (25 min actual vs 30 min estimated)
1. [x] Create TypeScript interfaces
2. [x] Set up context structure
3. [x] Add provider to app

### Phase 2: Core Functionality ⏳ IN PROGRESS (20/45 min)
1. [x] Implement state management
2. [ ] Create API service  ← CURRENT
3. [ ] Integrate API with context
```

## Execution Guidelines

### Code Quality Standards

```typescript
// ✅ GOOD: Clean, typed, well-structured
/**
 * Adds an item to the shopping cart
 * @param item - The cart item to add
 * @returns Updated cart state
 */
export const addToCart = (item: CartItem): Cart => {
  if (!isValidCartItem(item)) {
    throw new Error(`Invalid cart item: ${JSON.stringify(item)}`);
  }

  // Implementation
};

// ❌ BAD: No types, unclear, no error handling
const add = (x) => {
  data.push(x);
};
```

### Error Handling

```typescript
// Always handle errors gracefully
try {
  const result = await apiCall();
  return processResult(result);
} catch (error) {
  console.error('Operation failed:', error);

  // Show user-friendly message
  toast.error('Unable to complete operation. Please try again.');

  // Rollback if needed
  rollbackChanges();

  // Re-throw or handle
  throw new Error(`API call failed: ${error.message}`);
}
```

### Testing Strategy

```typescript
// Write tests as you implement
describe('CartContext', () => {
  it('should add item to cart', () => {
    const { result } = renderHook(() => useCart(), {
      wrapper: CartProvider
    });

    act(() => {
      result.current.addItem(mockItem);
    });

    expect(result.current.cart.items).toHaveLength(1);
    expect(result.current.cart.total).toBe(mockItem.price);
  });

  it('should handle invalid items', () => {
    const { result } = renderHook(() => useCart(), {
      wrapper: CartProvider
    });

    expect(() => {
      act(() => {
        result.current.addItem(null);
      });
    }).toThrow('Invalid cart item');
  });
});
```

### Documentation

```typescript
// Document as you write
/**
 * ShoppingCart Component
 *
 * Displays cart items with management capabilities.
 * Supports add, remove, update quantity operations.
 *
 * @example
 * ```tsx
 * <ShoppingCart
 *   onCheckout={() => navigate('/checkout')}
 * />
 * ```
 */
export const ShoppingCart: React.FC<Props> = (props) => {
  // Implementation
};
```

## Handling Deviations

If you need to deviate from the plan:

### 1. Document the Deviation

```markdown
## Deviation Log

### Deviation 1: Using Optimistic Updates
**Date**: 2026-01-20
**Original Plan**: Direct API calls with loading states
**New Approach**: Optimistic updates with rollback on failure
**Reason**: Significantly better UX, minimal risk
**Impact**: +15 minutes implementation time
**Approved**: Yes (better user experience justifies)
```

### 2. Update Plan File

Modify the plan to reflect the new approach:

```markdown
2. [x] Create API service (MODIFIED: Added optimistic updates)
```

### 3. Communicate Major Changes

For significant deviations:
- Stop and document the issue
- Explain why deviation is needed
- Get approval if required
- Update timeline estimates
- Resume execution

## Progress Reporting

Periodically report progress:

```markdown
## Execution Status Report

**Date**: 2026-01-20 14:30
**Feature**: Shopping Cart

### Completed
- ✅ Phase 1: Foundation (25 min)
- ✅ Phase 2: Core Functionality (50 min)

### In Progress
- ⏳ Phase 3: UI Components (15/40 min)
  - ✅ Main cart component
  - ⏳ Cart item component (current)
  - ⏸️ Header integration

### Upcoming
- ⏸️ Phase 4: Polish & Integration
- ⏸️ Phase 5: Testing

### Issues Encountered
1. **API endpoint not ready**
   - Resolution: Using mock data temporarily
   - Impact: Will need to swap in real API later

### Time Tracking
- Estimated: 3 hours
- Actual so far: 1.5 hours
- On track: Yes

### Next Steps
- Complete cart item component
- Integrate with header
- Begin Phase 4
```

## Validation Checkpoints

Before marking a phase complete:

- [ ] Code compiles without errors
- [ ] All tests passing
- [ ] No TypeScript errors
- [ ] No lint warnings
- [ ] Functionality works as expected
- [ ] Acceptance criteria met
- [ ] Code committed to Git
- [ ] Plan file updated

## Common Issues & Solutions

### Issue: Tests Failing
**Action**:
1. Don't skip - fix immediately
2. Review test expectations
3. Fix code or update test
4. Ensure all tests pass before continuing

### Issue: Plan Approach Not Working
**Action**:
1. Stop execution
2. Document the problem
3. Propose alternative
4. Update plan if approved
5. Resume execution

### Issue: Missing Dependency
**Action**:
1. Install dependency
2. Document why it's needed
3. Update plan's dependency section
4. Continue execution

### Issue: Taking Longer Than Estimated
**Action**:
1. Update time estimates in plan
2. Identify why (complexity, unforeseen issues)
3. Communicate if timeline critical
4. Continue with focus

## Commit Strategy

Make atomic commits:

```bash
# After each logical unit of work
git add [specific files]
git commit -m "feat: implement cart context

- Add CartContext and CartProvider
- Implement add, remove, update methods
- Add local state management
- Calculate totals automatically

Part of Phase 2: Core Functionality
Ref: .plans/PLAN-shopping-cart-2026-01-20.md"

# Push at phase completion
git push origin feature/shopping-cart
```

## Completion Criteria

A phase is complete when:
- ✅ All steps implemented
- ✅ All tests passing
- ✅ Acceptance criteria met
- ✅ Code reviewed (self)
- ✅ No critical bugs
- ✅ Documented
- ✅ Committed

## Final Checklist

Before marking execution complete:

- [ ] All phases finished
- [ ] All tests passing (unit, integration, e2e)
- [ ] No console errors or warnings
- [ ] Build succeeds
- [ ] Functionality works as designed
- [ ] Code follows project standards
- [ ] Documentation updated
- [ ] Plan file shows all completed
- [ ] Ready for code review

## Output Format

Update the plan file with completion status:

```markdown
# Implementation Plan: Shopping Cart

**Status**: ✅ COMPLETED
**Started**: 2026-01-20 10:00
**Completed**: 2026-01-20 13:30
**Time**: 3.5 hours (vs 3 hours estimated)

All phases completed successfully.
Deviations documented in plan.
Ready for code review.
```

## Next Steps

After execution is complete:
1. Run full test suite one final time
2. Build and verify
3. Commit final changes
4. Push to remote branch
5. Proceed to `/review` phase

## Important Reminders

- Follow the plan unless there's a good reason to deviate
- Test continuously, not just at the end
- Commit frequently with clear messages
- Update plan file as you progress
- Document any issues or deviations
- Focus on code quality, not just speed
- Ask for help if blocked

Your goal is working, tested, production-ready code that matches the plan's specifications.
