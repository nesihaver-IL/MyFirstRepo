---
name: peer-review
description: Different AI models review the code, finding problems the first model missed. Triggers on keywords like peer review, second opinion, cross review, multi-model review.
---

# Peer Review

This skill uses different AI models to review code from multiple perspectives, catching issues the original model might have missed.

## Purpose

Get a "second opinion" on code quality by:
- Using different AI models with different strengths
- Finding blind spots from the original implementation
- Validating architectural decisions
- Catching subtle bugs
- Providing alternative perspectives

## When to Use

- After completing `/review` (self-review)
- Before merging to main branch
- For critical/complex features
- When you want maximum confidence
- Before production deployment

## How It Works

1. **Multi-Model Analysis**: Different models review the same code
2. **Diverse Perspectives**: Each model has different strengths
3. **Cross-Validation**: Compare findings across models
4. **Consensus Building**: Identify consistent issues
5. **Comprehensive Report**: Aggregate all findings

## Usage

```
/peer-review
```

Or specify the focus:
```
"Peer review the authentication system for security issues"
```

## Multi-Model Strategy

### Model Specializations

Different AI models excel at different tasks:

#### Model 1: Claude Opus (Original Implementation)
**Strengths:**
- Complex logic
- Architecture design
- Best practices
- Documentation

**Review Focus:**
- Already reviewed in `/review`
- Baseline understanding

#### Model 2: Security-Focused Model
**Strengths:**
- Vulnerability detection
- Attack vector analysis
- Security best practices
- Compliance checking

**Review Focus:**
- Authentication/authorization flaws
- Injection vulnerabilities
- Data exposure risks
- Cryptographic weaknesses

#### Model 3: Performance-Focused Model
**Strengths:**
- Algorithm efficiency
- Memory optimization
- Rendering performance
- Database query optimization

**Review Focus:**
- Time complexity
- Space complexity
- Caching opportunities
- Bottleneck identification

#### Model 4: UX/Accessibility-Focused Model
**Strengths:**
- User experience
- Accessibility standards
- Mobile responsiveness
- Design patterns

**Review Focus:**
- WCAG compliance
- Keyboard navigation
- Screen reader support
- Mobile UX

## Peer Review Process

### Round 1: Security Review

```markdown
# Security Peer Review
**Reviewer**: Security-Focused AI
**Date**: 2026-01-20
**Focus**: Security vulnerabilities

## Critical Findings

### 1. JWT Token Exposure in LocalStorage
**Severity**: 🔴 Critical
**File**: `src/auth/AuthProvider.tsx:56`

```typescript
// CRITICAL SECURITY FLAW
localStorage.setItem('authToken', token);
```

**Issue**: Tokens in localStorage are vulnerable to XSS attacks

**Recommendation**:
```typescript
// Store in HttpOnly cookie instead
// Backend should set cookie:
res.cookie('authToken', token, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: 3600000
});
```

**Attack Scenario**:
1. Attacker injects XSS payload
2. Script reads localStorage.getItem('authToken')
3. Token exfiltrated to attacker's server
4. Account compromised

**CVSS Score**: 8.5 (High)

### 2. Missing Rate Limiting
**Severity**: 🔴 Critical
**File**: `src/api/auth.ts:12`

```typescript
// No rate limiting on login endpoint
export const login = async (email: string, password: string) => {
  return axios.post('/api/auth/login', { email, password });
};
```

**Issue**: Brute force attacks possible

**Recommendation**:
```typescript
// Backend: Implement rate limiting
app.use('/api/auth', rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  message: 'Too many login attempts'
}));

// Frontend: Show rate limit message
if (error.response?.status === 429) {
  toast.error('Too many attempts. Please try again later.');
}
```

## Additional Security Issues

### 3. Weak Password Requirements
**Severity**: 🟡 High
**File**: `src/components/RegisterForm.tsx:34`

Current: Minimum 6 characters
Recommended: 12+ chars, mixed case, numbers, symbols

### 4. No CSRF Protection
**Severity**: 🟡 High
**File**: API endpoints

Recommendation: Implement CSRF tokens for state-changing operations

---

**Security Score**: 3/10 (Needs Significant Work)
**Critical Issues**: 2
**High Issues**: 2
```

### Round 2: Performance Review

```markdown
# Performance Peer Review
**Reviewer**: Performance-Focused AI
**Date**: 2026-01-20
**Focus**: Performance optimization

## Critical Findings

### 1. Inefficient Cart Total Calculation
**Severity**: 🟡 High
**File**: `src/components/CartSummary.tsx:23`

```typescript
// O(n) operation runs on EVERY render
const total = cart.items.reduce((sum, item) =>
  sum + (item.price * item.quantity), 0
);
```

**Issue**: Recalculated unnecessarily

**Benchmark**:
- 10 items: 0.1ms (acceptable)
- 100 items: 1.2ms (noticeable)
- 1000 items: 15ms (janky)

**Recommendation**:
```typescript
const total = useMemo(() =>
  cart.items.reduce((sum, item) =>
    sum + (item.price * item.quantity), 0
  ),
  [cart.items]
);
```

**Expected Improvement**: 95% reduction in calculations

### 2. Large Bundle Size
**Severity**: 🟡 High
**File**: Multiple

**Current Bundle**: 1.2 MB (uncompressed)
**Target**: < 500 KB

**Issues**:
- Entire `lodash` imported (540 KB)
- Moment.js included (232 KB)
- Unused dependencies

**Recommendation**:
```typescript
// ❌ Importing entire library
import _ from 'lodash';
import moment from 'moment';

// ✅ Import only what you need
import debounce from 'lodash/debounce';
import { format } from 'date-fns';  // Smaller alternative

// ✅ Use tree-shaking
import { debounce } from 'lodash-es';
```

**Expected Improvement**: 60% reduction in bundle size

### 3. Missing Code Splitting
**Severity**: 🟢 Medium
**File**: `src/App.tsx`

```typescript
// All routes loaded upfront
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Settings from './pages/Settings';

// Recommended: Lazy load routes
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Profile = lazy(() => import('./pages/Profile'));
const Settings = lazy(() => import('./pages/Settings'));
```

**Expected Improvement**: 40% faster initial load

## Performance Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| First Contentful Paint | 2.1s | < 1.5s | 🔴 |
| Largest Contentful Paint | 3.8s | < 2.5s | 🔴 |
| Time to Interactive | 4.2s | < 3.0s | 🔴 |
| Bundle Size | 1.2 MB | < 500 KB | 🔴 |

**Performance Score**: 4/10 (Needs Improvement)
```

### Round 3: Accessibility Review

```markdown
# Accessibility Peer Review
**Reviewer**: UX/A11y-Focused AI
**Date**: 2026-01-20
**Focus**: WCAG 2.1 AA compliance

## Critical Findings

### 1. Form Inputs Missing Labels
**Severity**: 🔴 Critical
**File**: `src/components/LoginForm.tsx:45`
**WCAG**: 3.3.2 Labels or Instructions (Level A)

```tsx
// WCAG VIOLATION: No label
<input
  type="email"
  placeholder="Email"
  value={email}
  onChange={e => setEmail(e.target.value)}
/>

// ✅ Fixed
<label htmlFor="email">
  Email Address
  <input
    id="email"
    type="email"
    placeholder="email@example.com"
    value={email}
    onChange={e => setEmail(e.target.value)}
    aria-required="true"
    aria-invalid={emailError ? 'true' : 'false'}
    aria-describedby={emailError ? 'email-error' : undefined}
  />
</label>
{emailError && (
  <span id="email-error" role="alert">
    {emailError}
  </span>
)}
```

### 2. Poor Color Contrast
**Severity**: 🟡 High
**File**: `src/styles/theme.ts`
**WCAG**: 1.4.3 Contrast (Level AA)

**Failing Colors**:
```css
/* Contrast Ratio: 2.8:1 (FAIL - needs 4.5:1) */
.btn-secondary {
  color: #767676;
  background: #f0f0f0;
}

/* ✅ Fixed: 5.2:1 */
.btn-secondary {
  color: #595959;
  background: #f0f0f0;
}
```

**Testing Tool**: WebAIM Contrast Checker

### 3. Missing Keyboard Navigation
**Severity**: 🟡 High
**File**: `src/components/Dropdown.tsx`
**WCAG**: 2.1.1 Keyboard (Level A)

```tsx
// Not keyboard accessible
<div onClick={handleOpen}>Open Menu</div>

// ✅ Fixed
<button
  onClick={handleOpen}
  onKeyDown={e => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleOpen();
    }
  }}
  aria-expanded={isOpen}
  aria-haspopup="true"
>
  Open Menu
</button>
```

## Accessibility Audit Results

### WCAG 2.1 Level AA Compliance

| Category | Issues | Status |
|----------|--------|--------|
| Perceivable | 5 | 🔴 |
| Operable | 3 | 🟡 |
| Understandable | 1 | 🟢 |
| Robust | 2 | 🟡 |

**A11y Score**: 5/10 (Needs Work)
**Screen Reader Tested**: ❌ No
**Keyboard Navigation**: ⚠️ Partial
```

### Round 4: Code Quality Review

```markdown
# Code Quality Peer Review
**Reviewer**: Best Practices AI
**Date**: 2026-01-20
**Focus**: Maintainability & clean code

## Findings

### 1. Code Duplication (DRY Violation)
**Severity**: 🟢 Medium
**File**: Multiple files

```typescript
// Repeated in 5 different files
if (!user || !user.isAuthenticated) {
  throw new Error('Unauthorized');
}

// ✅ Refactor to utility
// src/utils/auth.ts
export const requireAuth = (user: User | null): void => {
  if (!user || !user.isAuthenticated) {
    throw new Error('Unauthorized');
  }
};

// Usage
requireAuth(user);
```

### 2. Magic Numbers
**Severity**: 🟢 Medium
**File**: `src/utils/validation.ts`

```typescript
// What do these numbers mean?
if (password.length < 8 || password.length > 128) {
  return false;
}

// ✅ Use named constants
const PASSWORD_MIN_LENGTH = 8;
const PASSWORD_MAX_LENGTH = 128;

if (password.length < PASSWORD_MIN_LENGTH ||
    password.length > PASSWORD_MAX_LENGTH) {
  return false;
}
```

### 3. Poor Error Messages
**Severity**: 🟢 Medium

```typescript
// Not helpful
throw new Error('Invalid input');

// ✅ Descriptive
throw new Error(
  `Email validation failed: "${email}" is not a valid email format. ` +
  `Expected format: user@domain.com`
);
```

**Code Quality Score**: 7/10 (Good with room for improvement)
```

## Consensus Report

After all peer reviews, create a consolidated report:

```markdown
# Consolidated Peer Review Report
**Project**: Shopping Cart Feature
**Date**: 2026-01-20
**Reviewers**: 4 AI Models

---

## Executive Summary

**Overall Score**: 5.75/10

| Aspect | Score | Priority |
|--------|-------|----------|
| Security | 3/10 | 🔴 Critical |
| Performance | 4/10 | 🟡 High |
| Accessibility | 5/10 | 🟡 High |
| Code Quality | 7/10 | 🟢 Medium |

---

## Must Fix Before Merge (Blocking)

### 1. JWT in LocalStorage (Security)
- **Risk**: Account takeover via XSS
- **Fix**: Move to HttpOnly cookie
- **Time**: 30 minutes

### 2. No Rate Limiting (Security)
- **Risk**: Brute force attacks
- **Fix**: Add rate limiting middleware
- **Time**: 45 minutes

### 3. Missing Form Labels (Accessibility)
- **Risk**: Unusable for screen readers
- **Fix**: Add proper labels and ARIA
- **Time**: 20 minutes

**Total Time to Fix Blockers**: ~1.5 hours

---

## Should Fix Soon (High Priority)

1. Bundle size optimization (Performance)
2. Color contrast issues (Accessibility)
3. Keyboard navigation (Accessibility)
4. Missing memoization (Performance)

**Estimated Time**: 2-3 hours

---

## Can Fix Later (Medium Priority)

1. Code duplication
2. Magic numbers
3. Code splitting
4. Error message improvements

**Estimated Time**: 1-2 hours

---

## Positive Highlights

✅ Well-structured components
✅ Good TypeScript usage
✅ Comprehensive tests
✅ Clear naming conventions
✅ Proper error handling (non-security)

---

## Model Agreement Analysis

**Issues Found by All Models**:
- JWT storage issue (unanimous)
- Form label problems (unanimous)

**Issues Found by 2+ Models**:
- Performance concerns (2 models)
- Bundle size (2 models)

**Unique Findings**:
- Rate limiting (Security model only)
- Color contrast (A11y model only)

---

## Recommendations

### Immediate Actions
1. ❌ **DO NOT MERGE** until blocking issues fixed
2. Fix security issues immediately
3. Address accessibility blockers
4. Re-review after fixes

### Next Steps
1. Fix blocking issues
2. Run `/review` again
3. Verify fixes with tests
4. Update documentation
5. Ready for merge

---

## Final Verdict

**Status**: ⛔ Not Ready for Production

**After Fixes**: Re-evaluate for approval
```

## Disagreement Resolution

When models disagree:

```markdown
## Model Disagreement: Validation Strategy

### Model 1 (Claude): Client-side only
**Reasoning**: Better UX, immediate feedback

### Model 2 (Security): Server-side required
**Reasoning**: Client-side can be bypassed

### Resolution: Both!
- Client-side for UX
- Server-side for security
- Best of both worlds

**Decision**: Implement both layers
```

## Best Practices

1. **Use Diverse Models**: Different perspectives catch more issues
2. **Focus Each Review**: Give each model a specific lens
3. **Compare Findings**: Look for consensus and unique insights
4. **Prioritize Issues**: Not everything needs immediate fixing
5. **Document Disagreements**: Resolve conflicting recommendations
6. **Re-Review After Fixes**: Verify issues are resolved

## Integration with Workflow

```
/exploration-phase
    ↓
/create-plan
    ↓
/execute-plan
    ↓
/review (self-review)
    ↓
[Fix critical issues]
    ↓
/peer-review  ← YOU ARE HERE
    ↓
[Fix blocking issues]
    ↓
/update-docs
    ↓
[Ready for merge]
```

## Output

Peer review produces:
1. **Individual Reviews**: One per model/focus area
2. **Consensus Report**: Aggregated findings
3. **Priority Matrix**: What to fix when
4. **Approval Status**: Ready or blocked

## Tips

- Schedule peer review for complex features
- Use models with complementary strengths
- Don't skip even if self-review looks good
- Fresh perspective always finds something
- Learn from peer review findings
- Build a checklist from common issues

**Next Step**: Fix all blocking issues, then proceed to `/update-docs`
