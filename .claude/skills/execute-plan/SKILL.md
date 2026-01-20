---
name: execute-plan
description: AI writes the code using the approved plan. Use different AI models for different tasks (Claude for backend logic, specialized models for specific domains). Triggers on keywords like execute plan, implement plan, build feature, write code.
---

# Execute Plan

This skill implements the code based on an approved plan, following the documented steps precisely.

## Purpose

Transform the approved plan into working code by:
- Following the plan step-by-step
- Writing clean, tested code
- Documenting as you go
- Tracking progress
- Handling issues that arise

## When to Use

- After `/create-plan` is approved
- When ready to write actual code
- Following a documented implementation strategy
- Need systematic, tracked execution

## How It Works

1. **Load Plan**: Read the approved plan file
2. **Execute in Order**: Follow steps sequentially
3. **Track Progress**: Check off completed items
4. **Handle Issues**: Adapt when needed, document changes
5. **Validate**: Ensure each step works before moving on

## Usage

```
/execute-plan
```

Or specify which plan:
```
"Execute the shopping cart implementation plan"
```

## Execution Process

### Step 1: Pre-Execution Setup

```bash
# Create feature branch
git checkout -b feature/[feature-name]

# Verify dependencies
npm install

# Run existing tests to ensure baseline
npm test
```

### Step 2: Phase-by-Phase Execution

For each phase in the plan:

1. **Read Phase Requirements**
   - Understand what needs to be done
   - Check for dependencies
   - Note any special considerations

2. **Implement Code**
   - Write clean, tested code
   - Follow project conventions
   - Add appropriate comments

3. **Validate Step**
   - Run relevant tests
   - Check for errors
   - Verify functionality

4. **Update Plan**
   - Check off completed items
   - Note any deviations
   - Document issues encountered

### Step 3: Continuous Testing

After each significant change:
```bash
# Run tests
npm test

# Check types (TypeScript)
npm run type-check

# Lint code
npm run lint

# Run build
npm run build
```

### Step 4: Progress Tracking

Update the plan file with progress:
```markdown
### Phase 1: Foundation ✅ COMPLETED
1. [x] Create base component structure
2. [x] Set up state management
3. [x] Define TypeScript interfaces

### Phase 2: Core Functionality ⏳ IN PROGRESS
1. [x] Implement main feature logic
2. [ ] Add API integration  ← CURRENT
3. [ ] Handle loading and error states
```

## Execution Example

```markdown
## Executing Plan: Shopping Cart Feature

**Plan Location**: `.plans/PLAN-shopping-cart-2026-01-20.md`
**Status**: In Progress
**Started**: 2026-01-20 10:00 AM

---

### Phase 1: Foundation ✅ COMPLETED (15 mins)

#### 1.1 Create TypeScript Interfaces ✅
```typescript
// Created: src/types/cart.ts
export interface CartItem {
  id: string;
  productId: string;
  name: string;
  price: number;
  quantity: number;
  imageUrl: string;
}

export interface Cart {
  items: CartItem[];
  total: number;
  itemCount: number;
}
```

**Testing**: ✅ Type definitions compile correctly

#### 1.2 Create Cart Context ✅
```typescript
// Created: src/contexts/CartContext.tsx
import React, { createContext, useContext, useState } from 'react';
import { Cart, CartItem } from '../types/cart';

interface CartContextType {
  cart: Cart;
  addItem: (item: CartItem) => void;
  removeItem: (itemId: string) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  clearCart: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
};

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [cart, setCart] = useState<Cart>({
    items: [],
    total: 0,
    itemCount: 0
  });

  const addItem = (item: CartItem) => {
    setCart(prev => {
      const existingItem = prev.items.find(i => i.id === item.id);
      if (existingItem) {
        return {
          ...prev,
          items: prev.items.map(i =>
            i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
          ),
          total: prev.total + item.price,
          itemCount: prev.itemCount + 1
        };
      }
      return {
        items: [...prev.items, { ...item, quantity: 1 }],
        total: prev.total + item.price,
        itemCount: prev.itemCount + 1
      };
    });
  };

  // ... other methods

  return (
    <CartContext.Provider value={{ cart, addItem, removeItem, updateQuantity, clearCart }}>
      {children}
    </CartContext.Provider>
  );
};
```

**Testing**: ✅ Context provides correctly, no type errors

---

### Phase 2: Core Functionality ⏳ IN PROGRESS (20/45 mins)

#### 2.1 Implement Cart Logic ✅
Completed cart state management with add, remove, update, and clear operations.

**Testing**: ✅ All cart operations work correctly

#### 2.2 Add API Integration ⏳ CURRENT
```typescript
// Creating: src/api/cart.ts
import axios from 'axios';
import { Cart, CartItem } from '../types/cart';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:3001';

export const cartAPI = {
  async getCart(): Promise<Cart> {
    const response = await axios.get(`${API_BASE}/cart`);
    return response.data;
  },

  async addToCart(item: CartItem): Promise<Cart> {
    const response = await axios.post(`${API_BASE}/cart/items`, item);
    return response.data;
  },

  // ... more methods
};
```

**Issue Encountered**: API endpoint not yet available
**Resolution**: Using mock data for now, will integrate real API later
**Updated Plan**: Added note to integrate real API in Phase 4

---

### Deviations from Plan

1. **Mock API Data**
   - Original: Use real API immediately
   - Updated: Use mock data, integrate API in Phase 4
   - Reason: Backend not ready yet

2. **Added Loading States**
   - Not in original plan
   - Added because: Better UX during API calls
   - Impact: +10 mins to timeline

---

### Current Status

- ✅ Phase 1: Complete (15 mins)
- ⏳ Phase 2: 50% complete (20/45 mins)
- ⏸️ Phase 3: Not started
- ⏸️ Phase 4: Not started
- ⏸️ Phase 5: Not started

**Next Step**: Complete API integration (Phase 2.2)
**Estimated Time Remaining**: 2 hours
```

## Best Practices During Execution

### 1. Code Quality

```typescript
// ❌ Bad: No types, unclear logic
const handleClick = (x) => {
  if (x) {
    setData([...data, x]);
  }
};

// ✅ Good: Typed, clear, documented
/**
 * Adds an item to the cart if it's valid
 * @param item - The cart item to add
 */
const handleAddToCart = (item: CartItem): void => {
  if (!item || item.quantity <= 0) {
    console.warn('Invalid cart item:', item);
    return;
  }

  setCartItems(prevItems => [...prevItems, item]);
};
```

### 2. Incremental Testing

```bash
# After each file/component
npm test -- CartContext.test.tsx

# After each phase
npm test

# Before moving to next phase
npm run build && npm test
```

### 3. Commit Strategy

```bash
# Commit after each completed step
git add src/contexts/CartContext.tsx
git commit -m "feat: add cart context with state management

- Create CartContext and CartProvider
- Implement add, remove, update, clear methods
- Add TypeScript types
- Calculate totals automatically

Part of Phase 1: Foundation
Ref: .plans/PLAN-shopping-cart-2026-01-20.md"

# Push at end of each phase
git push origin feature/shopping-cart
```

### 4. Error Handling

```typescript
// Always handle errors gracefully
try {
  const cart = await cartAPI.addToCart(item);
  setCart(cart);
} catch (error) {
  console.error('Failed to add item to cart:', error);
  // Show user-friendly error
  toast.error('Could not add item. Please try again.');
  // Rollback optimistic update if needed
  rollbackCartUpdate();
}
```

### 5. Documentation

```typescript
/**
 * Shopping Cart Component
 *
 * Displays cart items with quantities and prices.
 * Allows users to update quantities or remove items.
 *
 * @example
 * ```tsx
 * <ShoppingCart
 *   onCheckout={() => navigate('/checkout')}
 *   onContinueShopping={() => navigate('/products')}
 * />
 * ```
 */
export const ShoppingCart: React.FC<ShoppingCartProps> = ({ ... }) => {
  // Implementation
};
```

## Handling Deviations

When you need to deviate from the plan:

1. **Document Why**
   ```markdown
   ### Deviation: Added Optimistic Updates

   **Original Plan**: Direct API calls with loading states
   **Updated Approach**: Optimistic updates with rollback
   **Reason**: Better UX, feels more responsive
   **Impact**: +15 mins, but worth it
   **Approved By**: [Name] on [Date]
   ```

2. **Update Plan File**
   - Add notes about changes
   - Update time estimates
   - Check off as modified, not original

3. **Communicate**
   - If major deviation, get approval
   - Update stakeholders
   - Document in commit messages

## Multi-Model Strategy

Use different AI models for different tasks:

### Claude Sonnet/Opus
Best for:
- Complex business logic
- Backend implementation
- State management
- Architecture decisions

### Specialized Models
- **UI Generation**: Models good at CSS/design
- **Data Processing**: Models optimized for algorithms
- **Testing**: Models focused on edge cases

### Model Selection Example

```markdown
## Execution Plan with Model Assignments

### Phase 1: Backend Logic (Claude Opus)
- Implement authentication
- Create API endpoints
- Handle database operations

### Phase 2: Frontend UI (Specialized UI Model)
- Create responsive layouts
- Implement design system
- Add animations

### Phase 3: Testing (Claude Sonnet)
- Write unit tests
- Create integration tests
- Add E2E tests
```

## Progress Tracking

### Status Indicators
- ⏸️ **Not Started**: Hasn't been attempted
- ⏳ **In Progress**: Currently working on
- ⚠️ **Blocked**: Can't proceed, needs resolution
- ✅ **Completed**: Done and tested
- ❌ **Failed**: Attempted but didn't work

### Time Tracking
```markdown
| Phase | Estimated | Actual | Status |
|-------|-----------|--------|--------|
| Phase 1 | 30 mins | 35 mins | ✅ |
| Phase 2 | 45 mins | 20 mins (in progress) | ⏳ |
| Phase 3 | 30 mins | - | ⏸️ |
```

## Validation Checkpoints

Before marking a phase complete:

- [ ] Code compiles without errors
- [ ] All tests pass
- [ ] No type errors (TypeScript)
- [ ] No lint errors
- [ ] Functionality works as expected
- [ ] Meets acceptance criteria
- [ ] Code reviewed (if required)
- [ ] Committed to version control

## Common Issues & Solutions

### Issue: Tests Failing
**Solution**:
1. Fix tests before continuing
2. Don't skip phases
3. Update plan if tests reveal problems

### Issue: Missing Dependency
**Solution**:
1. Add to package.json
2. Document why it's needed
3. Update plan with new dependency

### Issue: Approach Not Working
**Solution**:
1. Stop execution
2. Document the issue
3. Return to `/exploration-phase`
4. Update `/create-plan`
5. Resume execution

### Issue: Time Running Over
**Solution**:
1. Update time estimates
2. Identify bottlenecks
3. Consider simplifying scope
4. Communicate delays

## Output

Execution produces:
1. **Working Code**: Fully implemented feature
2. **Tests**: Passing test suite
3. **Documentation**: Updated docs
4. **Updated Plan**: Progress tracked
5. **Git History**: Clean commits

## Integration with Workflow

```
/exploration-phase
    ↓
/create-plan
    ↓
/execute-plan  ← YOU ARE HERE
    ↓
/review
    ↓
/peer-review
    ↓
/update-docs
```

## Completion Criteria

Execution is complete when:
- ✅ All plan phases finished
- ✅ All tests passing
- ✅ No critical bugs
- ✅ Code meets standards
- ✅ Ready for review

**Next Step**: `/review` to check for bugs and improvements
