# Create Plan

You are creating a detailed implementation plan based on the exploration findings. This plan will guide the execution phase.

## Your Mission

Transform exploration findings into a concrete, step-by-step implementation plan that documents all technical decisions, identifies files to modify/create, and establishes clear success criteria.

## Plan Creation Process

### 1. Synthesize Exploration Findings

Review and consolidate:
- Requirements and goals
- Technical constraints
- Identified patterns
- Potential challenges
- Answered questions

### 2. Define Technical Approach

Document decisions on:
- Architecture patterns to use
- State management strategy
- API integration approach
- File structure and organization
- Testing strategy
- Performance considerations
- Security measures

### 3. Break Down Into Phases

Organize work into logical phases:
- Phase 1: Foundation (types, base structure)
- Phase 2: Core functionality
- Phase 3: UI/UX implementation
- Phase 4: Integration and polish
- Phase 5: Testing and validation

### 4. Identify All Files

List every file to:
- **CREATE**: New files needed
- **MODIFY**: Existing files to update
- **DELETE**: Files to remove (if any)

### 5. Estimate Effort

Provide realistic time estimates for each phase.

## Plan Template

Create a plan using this structure:

```markdown
# Implementation Plan: [Feature Name]

**Created**: [Date]
**Status**: Draft | Ready | Approved | In Progress | Completed

---

## 📋 Overview

[1-2 paragraph summary of what we're building and why]

## 🎯 Goals

**Primary Goal:**
- [Main objective]

**Secondary Goals:**
- [Additional objective 1]
- [Additional objective 2]

**Success Criteria:**
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Measurable criterion 3]

---

## 🏗️ Technical Decisions

### Architecture
- **Pattern**: [e.g., Context API for state management]
- **Reasoning**: [Why this approach]

### State Management
- **Approach**: [e.g., React Context with useReducer]
- **Persistence**: [e.g., localStorage + backend sync]

### API Integration
- **Endpoints**: [List endpoints needed]
- **Authentication**: [How auth is handled]
- **Error Handling**: [Strategy for errors]

### File Structure
```
src/
├── components/
│   ├── NewComponent.tsx       (CREATE)
│   └── ExistingComponent.tsx  (MODIFY)
├── contexts/
│   └── NewContext.tsx         (CREATE)
├── api/
│   └── newService.ts          (CREATE)
├── types/
│   └── newTypes.ts            (CREATE)
└── utils/
    └── helpers.ts             (MODIFY)
```

---

## 📝 Implementation Phases

### Phase 1: Foundation (Est: 30 min)

**Goal**: Set up basic structure and types

1. [ ] Create TypeScript interfaces
   - File: `src/types/cart.ts` (CREATE)
   - Define all type definitions
   - Export interfaces

2. [ ] Set up context structure
   - File: `src/contexts/CartContext.tsx` (CREATE)
   - Create context and provider skeleton
   - Define context interface

3. [ ] Add provider to app
   - File: `src/App.tsx` (MODIFY)
   - Wrap app with provider

**Acceptance Criteria:**
- [ ] All types compile without errors
- [ ] Provider renders without crashing
- [ ] Context accessible in components

---

### Phase 2: Core Functionality (Est: 45 min)

**Goal**: Implement main business logic

1. [ ] Implement state management
   - Add state variables
   - Implement add/update/remove logic
   - Handle calculations (totals, counts)

2. [ ] Create API service
   - File: `src/api/cart.ts` (CREATE)
   - Implement all API calls
   - Add error handling
   - Add retry logic

3. [ ] Integrate API with context
   - Connect context to API
   - Handle loading states
   - Implement optimistic updates

**Acceptance Criteria:**
- [ ] State updates correctly
- [ ] API calls succeed
- [ ] Errors handled gracefully

---

### Phase 3: UI Components (Est: 40 min)

**Goal**: Build user interface

1. [ ] Create main component
   - File: `src/components/ShoppingCart.tsx` (CREATE)
   - Build layout structure
   - Add item list rendering

2. [ ] Create item component
   - File: `src/components/CartItem.tsx` (CREATE)
   - Display item details
   - Add quantity controls
   - Add remove button

3. [ ] Add to existing components
   - File: `src/components/Header.tsx` (MODIFY)
   - Add cart icon
   - Show item count badge

**Acceptance Criteria:**
- [ ] Components render correctly
- [ ] Responsive on mobile
- [ ] Accessible (WCAG AA)

---

### Phase 4: Polish & Integration (Est: 25 min)

**Goal**: Add refinements and integrate fully

1. [ ] Add error handling
   - User-friendly error messages
   - Toast notifications
   - Retry mechanisms

2. [ ] Implement validation
   - Quantity limits
   - Stock availability
   - Input sanitization

3. [ ] Add loading states
   - Skeleton loaders
   - Spinners where appropriate
   - Disable buttons during operations

**Acceptance Criteria:**
- [ ] All errors handled
- [ ] Validation works
- [ ] Loading states clear

---

### Phase 5: Testing (Est: 30 min)

**Goal**: Ensure quality and reliability

1. [ ] Write unit tests
   - Test context logic
   - Test calculations
   - Test API service

2. [ ] Write integration tests
   - Test full user flows
   - Test error scenarios
   - Test edge cases

3. [ ] Manual testing
   - Test on different browsers
   - Test on mobile devices
   - Test with screen reader
   - Performance testing

**Acceptance Criteria:**
- [ ] All tests passing
- [ ] Coverage > 80%
- [ ] No console errors

---

## 📂 File Manifest

### Files to Create
- `src/types/cart.ts` - Type definitions
- `src/contexts/CartContext.tsx` - State management
- `src/api/cart.ts` - API service
- `src/components/ShoppingCart.tsx` - Main UI
- `src/components/CartItem.tsx` - Item UI
- `src/components/CartSummary.tsx` - Summary UI
- `tests/cart.test.tsx` - Unit tests
- `tests/integration/cart-flow.test.tsx` - Integration tests

### Files to Modify
- `src/App.tsx` - Add provider
- `src/components/Header.tsx` - Add cart icon
- `src/components/ProductCard.tsx` - Add to cart button
- `src/api/index.ts` - Export cart API

### Files to Delete
- None

---

## 🔒 Security Considerations

- [ ] Input sanitization for cart items
- [ ] Authentication on all cart endpoints
- [ ] CSRF protection for state changes
- [ ] Rate limiting on API calls
- [ ] No sensitive data in localStorage

---

## ⚡ Performance Considerations

- [ ] Memoize expensive calculations
- [ ] Debounce quantity updates
- [ ] Lazy load cart component
- [ ] Optimize re-renders with React.memo
- [ ] Keep bundle size minimal

---

## ♿ Accessibility

- [ ] WCAG AA compliance
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] ARIA labels on interactive elements
- [ ] Focus management
- [ ] Sufficient color contrast

---

## 📦 Dependencies

### Required
- None (using existing dependencies)

### Optional
- `react-hot-toast` - For notifications
- `lodash.debounce` - For debouncing

---

## ⚠️ Risk Mitigation

**Risk 1: State Synchronization Issues**
- Mitigation: Optimistic updates with rollback
- Testing: Comprehensive state tests

**Risk 2: API Failures**
- Mitigation: Retry logic with exponential backoff
- Testing: Test failure scenarios

**Risk 3: Performance with Large Carts**
- Mitigation: Virtualization if needed
- Testing: Test with 100+ items

---

## 📊 Timeline

| Phase | Estimated | Status |
|-------|-----------|--------|
| Phase 1 | 30 min | ⏸️ |
| Phase 2 | 45 min | ⏸️ |
| Phase 3 | 40 min | ⏸️ |
| Phase 4 | 25 min | ⏸️ |
| Phase 5 | 30 min | ⏸️ |
| **Total** | **~3 hours** | |

---

## ✅ Approval Checklist

Before proceeding to execution:

- [ ] Technical approach approved
- [ ] Timeline acceptable
- [ ] Dependencies confirmed
- [ ] Security reviewed
- [ ] Accessibility considered
- [ ] All questions answered
- [ ] Ready to execute

---

## 🚀 Next Steps

Once approved:
1. Save this plan to `.plans/PLAN-[feature]-[date].md`
2. Proceed to execution phase
3. Track progress against this plan
4. Update plan if deviations occur

---

**Plan Status**: [Draft | Ready for Review | Approved | In Execution | Completed]
```

## Guidelines

1. **Be Specific**: Don't say "add feature" - detail exactly what
2. **Order Logically**: Build foundation first, then features
3. **Include Everything**: Types, tests, docs - all in the plan
4. **Estimate Realistically**: Add buffer time for unknowns
5. **Consider All Aspects**: Security, performance, accessibility
6. **Make Checkable**: Use checkboxes for tracking
7. **Document Decisions**: Explain why you chose this approach

## Plan Storage

Save the plan to:
```
.plans/PLAN-[feature-name]-[YYYY-MM-DD].md
```

## Output

After creating the plan:
1. Display the complete plan
2. Save to `.plans/` directory
3. Ask for approval before proceeding
4. Ready for execution phase once approved

The plan serves as a contract and roadmap for implementation. Take time to make it comprehensive and accurate.
