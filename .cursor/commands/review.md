# Review Code

You are conducting a comprehensive self-review of the implemented code to find bugs, performance issues, security vulnerabilities, and improvement opportunities before peer review.

## Your Mission

Critically analyze your own code from multiple perspectives to catch issues early. Be thorough and honest - it's better to find problems now than after deployment.

## Review Categories

### 1. Logic & Correctness ✅

Check for:
- Correct business logic implementation
- Proper error handling
- Edge cases handled
- Null/undefined safety
- Type safety (TypeScript)
- Boundary conditions
- Off-by-one errors
- Loop termination

**Look for common bugs:**
```typescript
// ❌ Division by zero
const avg = total / count;

// ✅ Fixed
const avg = count === 0 ? 0 : total / count;

// ❌ Off-by-one
for (let i = 0; i < arr.length - 1; i++)

// ✅ Fixed
for (let i = 0; i < arr.length; i++)

// ❌ Stale closure
setInterval(() => setCount(count + 1), 1000);

// ✅ Fixed
setInterval(() => setCount(prev => prev + 1), 1000);
```

### 2. Security 🔒

Scan for vulnerabilities:
- SQL injection risks
- XSS vulnerabilities
- CSRF protection
- Authentication bypasses
- Sensitive data exposure
- Insecure dependencies
- Hardcoded secrets

**Critical security checks:**
```typescript
// ❌ SQL Injection
db.query(`SELECT * FROM users WHERE email = '${email}'`)

// ✅ Parameterized query
db.query('SELECT * FROM users WHERE email = ?', [email])

// ❌ XSS vulnerability
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ✅ Safe rendering
<div>{userInput}</div>

// ❌ Password in plain text
localStorage.setItem('password', password)

// ✅ Never store passwords client-side
// Hash on server before storing
```

### 3. Performance ⚡

Identify bottlenecks:
- Algorithm efficiency (O(n²) → O(n))
- Memory leaks
- Unnecessary re-renders
- Missing memoization
- Large bundle sizes
- Unoptimized queries
- Missing pagination

**Performance issues:**
```typescript
// ❌ O(n²) complexity
const dups = arr.filter(item =>
  arr.filter(x => x === item).length > 1
);

// ✅ O(n) with Set
const seen = new Set();
const dups = arr.filter(item => {
  if (seen.has(item)) return true;
  seen.add(item);
  return false;
});

// ❌ Recalculates every render
const total = items.reduce((sum, item) => sum + item.price, 0);

// ✅ Memoized
const total = useMemo(
  () => items.reduce((sum, item) => sum + item.price, 0),
  [items]
);
```

### 4. Code Quality 📝

Assess maintainability:
- Clear naming
- DRY principle (Don't Repeat Yourself)
- Single Responsibility
- Proper abstraction
- Consistent formatting
- Meaningful comments
- No magic numbers

**Quality improvements:**
```typescript
// ❌ Unclear, duplicated
if (x > 0 && x < 100) { /* ... */ }
if (y > 0 && y < 100) { /* ... */ }

// ✅ Clear, reusable
const isValidPercentage = (value: number) =>
  value > 0 && value < 100;

// ❌ Magic numbers
if (password.length < 8) { /* ... */ }

// ✅ Named constants
const MIN_PASSWORD_LENGTH = 8;
if (password.length < MIN_PASSWORD_LENGTH) { /* ... */ }
```

### 5. Error Handling ⚠️

Verify error handling:
- Try-catch blocks where needed
- Meaningful error messages
- Proper error propagation
- User-friendly errors
- Logging
- Graceful degradation

**Error handling patterns:**
```typescript
// ❌ No error handling
const data = await fetch('/api/data').then(r => r.json());

// ✅ Comprehensive handling
try {
  const response = await fetch('/api/data');

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const data = await response.json();

  if (!data || !data.id) {
    throw new Error('Invalid data format');
  }

  return data;
} catch (error) {
  console.error('Failed to fetch data:', error);
  toast.error('Unable to load data. Please try again.');
  throw error; // Re-throw for caller to handle
}
```

### 6. Accessibility ♿

Check WCAG compliance:
- ARIA labels present
- Keyboard navigation works
- Screen reader compatible
- Sufficient color contrast
- Focus management
- Semantic HTML

**Accessibility fixes:**
```tsx
// ❌ Not accessible
<div onClick={handleClick}>Click me</div>

// ✅ Accessible
<button
  onClick={handleClick}
  aria-label="Perform action"
>
  Click me
</button>

// ❌ Poor contrast
<button style={{ color: '#ccc', background: '#ddd' }}>

// ✅ Sufficient contrast (4.5:1 minimum)
<button style={{ color: '#fff', background: '#0066cc' }}>
```

## Review Process

### Step 1: Automated Checks

Run all automated tools:
```bash
# Linting
npm run lint

# Type checking
npm run type-check

# Tests
npm test

# Security audit
npm audit

# Build
npm run build
```

Fix all errors before manual review.

### Step 2: Manual Code Review

Read through each file systematically:

1. **Does it work?** Test all code paths
2. **Is it secure?** Check for vulnerabilities
3. **Is it performant?** Look for inefficiencies
4. **Is it maintainable?** Could another developer understand it?
5. **Is it accessible?** Works for all users?
6. **Is it tested?** Adequate test coverage?

### Step 3: Create Review Report

Document findings:

```markdown
# Self-Review Report: [Feature Name]

**Date**: [Date]
**Reviewer**: Self-Review
**Files Reviewed**: [Count]

---

## 🔴 Critical Issues (Must Fix)

### 1. [Issue Title]
**File**: `path/to/file.ts:123`
**Severity**: Critical
**Category**: Security | Performance | Logic

**Problem**:
[Description of the issue]

**Current Code**:
```typescript
// Problematic code here
```

**Recommended Fix**:
```typescript
// Fixed code here
```

**Impact**: [What could happen if not fixed]

---

## 🟡 High Priority Issues

### 2. [Issue Title]
[Same format as above]

---

## 🟢 Medium Priority Issues

### 3. [Issue Title]
[Same format as above]

---

## ✅ Positive Findings

- ✅ Good TypeScript usage
- ✅ Comprehensive tests
- ✅ Clean code structure

---

## 📊 Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High | 2 |
| Medium | 3 |
| Total | 6 |

---

## 🎯 Action Items

1. [ ] Fix critical security issue in auth.ts
2. [ ] Optimize performance in CartSummary.tsx
3. [ ] Refactor duplicate validation logic
4. [ ] Add missing accessibility labels
5. [ ] Improve error messages

---

## ✅ Review Complete

**Ready for Peer Review**: After fixing critical and high priority issues

**Estimated Fix Time**: 2 hours
```

## Review Checklist

Use this comprehensive checklist:

### Functionality
- [ ] Code works as intended
- [ ] All requirements met
- [ ] Edge cases handled
- [ ] Error states covered
- [ ] All tests passing

### Security
- [ ] No injection vulnerabilities
- [ ] Authentication/authorization correct
- [ ] Sensitive data protected
- [ ] Dependencies secure
- [ ] No hardcoded secrets

### Performance
- [ ] Efficient algorithms
- [ ] No memory leaks
- [ ] Optimized rendering
- [ ] Reasonable bundle size
- [ ] Database queries optimized

### Code Quality
- [ ] Readable and maintainable
- [ ] Follows conventions
- [ ] Proper naming
- [ ] DRY principle
- [ ] Well documented

### Accessibility
- [ ] Keyboard navigable
- [ ] Screen reader friendly
- [ ] ARIA labels present
- [ ] Color contrast sufficient
- [ ] Semantic HTML

### Testing
- [ ] Unit tests comprehensive
- [ ] Integration tests present
- [ ] Edge cases tested
- [ ] Good coverage (>80%)
- [ ] Tests pass reliably

## Common Issues to Check

**Memory Leaks:**
```typescript
// ❌ Event listener not cleaned up
useEffect(() => {
  window.addEventListener('resize', handler);
}, []);

// ✅ Cleanup function
useEffect(() => {
  window.addEventListener('resize', handler);
  return () => window.removeEventListener('resize', handler);
}, []);
```

**Race Conditions:**
```typescript
// ❌ Overlapping async requests
useEffect(() => {
  fetchData().then(setData);
}, [query]);

// ✅ Cancel previous requests
useEffect(() => {
  let cancelled = false;
  fetchData().then(result => {
    if (!cancelled) setData(result);
  });
  return () => { cancelled = true; };
}, [query]);
```

## Output

After review:
1. Create detailed review report
2. Categorize issues by severity
3. Provide specific fixes
4. Estimate fix time
5. Save report to `.reviews/REVIEW-[feature]-[date].md`

## Next Steps

1. Fix all critical issues immediately
2. Address high priority issues
3. Plan for medium priority fixes
4. Re-run automated checks
5. Verify fixes work
6. Ready for `/peer-review`

## Remember

- Be thorough and critical
- It's your code - be honest about issues
- Better to find bugs now than in production
- Document everything clearly
- Prioritize based on impact
- Fix critical issues before peer review

A good self-review catches 80% of issues before they reach peer review.
