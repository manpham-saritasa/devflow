# Design Patterns Reference

Common design patterns useful during refactoring. Use when a plan step calls for restructuring conditional logic or validation chains.

## Strategy Pattern

### When to use
- Switch/if-else on a type code or enum that keeps growing
- Same operation implemented differently based on context
- Want to add new behaviors without modifying existing code

### Before (conditional logic)

```typescript
function calculateShipping(order: Order, method: string): number {
  if (method === 'standard') {
    return order.total > 50 ? 0 : 5.99;
  } else if (method === 'express') {
    return order.total > 100 ? 9.99 : 14.99;
  } else if (method === 'overnight') {
    return 29.99;
  }
  throw new Error(`Unknown method: ${method}`);
}
```

### After (Strategy pattern)

```typescript
interface ShippingStrategy {
  calculate(order: Order): number;
}

class StandardShipping implements ShippingStrategy {
  calculate(order: Order): number {
    return order.total > 50 ? 0 : 5.99;
  }
}

class ExpressShipping implements ShippingStrategy {
  calculate(order: Order): number {
    return order.total > 100 ? 9.99 : 14.99;
  }
}

class OvernightShipping implements ShippingStrategy {
  calculate(order: Order): number {
    return 29.99;
  }
}

// Registry — add new strategies without touching existing code
const strategies: Record<string, ShippingStrategy> = {
  standard: new StandardShipping(),
  express: new ExpressShipping(),
  overnight: new OvernightShipping(),
};

function calculateShipping(order: Order, method: string): number {
  const strategy = strategies[method];
  if (!strategy) throw new Error(`Unknown method: ${method}`);
  return strategy.calculate(order);
}
```

## Chain of Responsibility

### When to use
- Multiple validation or processing steps applied in sequence
- Each step can short-circuit (stop processing)
- Order of steps matters but may need to change

### Before (nested validations)

```typescript
function validate(user: User): string[] {
  const errors: string[] = [];
  if (!user.email) errors.push('Email required');
  else if (!isValidEmail(user.email)) errors.push('Invalid email');
  if (!user.name) errors.push('Name required');
  if (user.age < 18) errors.push('Must be 18+');
  if (user.country === 'blocked') errors.push('Country not supported');
  return errors;
}
```

### After (Chain of Responsibility)

```typescript
interface ValidationResult {
  error: string | null;
}

interface Validator {
  validate(user: User): ValidationResult;
}

class EmailRequiredValidator implements Validator {
  validate(user: User): ValidationResult {
    if (!user.email) return { error: 'Email required' };
    return { error: null };
  }
}

class EmailFormatValidator implements Validator {
  validate(user: User): ValidationResult {
    if (user.email && !isValidEmail(user.email)) return { error: 'Invalid email' };
    return { error: null };
  }
}

class AgeValidator implements Validator {
  validate(user: User): ValidationResult {
    if (user.age < 18) return { error: 'Must be 18+' };
    return { error: null };
  }
}

// Chain runner
function validateUser(user: User, validators: Validator[]): string[] {
  const errors: string[] = [];
  for (const validator of validators) {
    const result = validator.validate(user);
    if (result.error) errors.push(result.error);
  }
  return errors;
}

// Usage — order is explicit, easy to change
const validators = [
  new EmailRequiredValidator(),
  new EmailFormatValidator(),
  new AgeValidator(),
];
const errors = validateUser(user, validators);
```

## When NOT to use these patterns

- **Strategy**: When there are only 2-3 variants and they rarely change — a simple switch is fine.
- **Chain of Responsibility**: When validation logic is simple (< 5 checks) and order doesn't matter — a plain function is clearer.
- Always ask: "Does this reduce complexity, or just move it around?"
