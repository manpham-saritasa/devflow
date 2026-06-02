---
name: simplify
version: 0.2.0
description: Reduce local complexity, improve readability, naming, and control flow, and remove small-scale friction without changing behavior.
triggers:
  - "simplify"
  - "simplify this"
  - "clean up"
---

# Simplify

Use this skill when the plan step is tagged `[simplify]`.
Invoked by refflow agent during execution.

## When to use

See `PRINCIPLES.md` for invocation modes.
Manual trigger: run when a plan step is tagged `[simplify]`.

## Goal

Make code easier to read, explain, review, and maintain without changing runtime behavior, public behavior, or business rules.

## Focus

Apply this skill to:
- deep nesting,
- repeated logic,
- poor names,
- boolean complexity,
- long methods,
- mixed abstraction levels,
- noisy conditionals,
- JSX/template/control-flow clutter,
- repetitive guards or response shaping.

## Code Smells

Use this catalog to identify and fix common smells. Pick the matching operation from the table below.

### 1. Long method
**Smell:** Method > 40 lines, does multiple things.
**Fix:** Extract focused sub-methods. Keep top-level as orchestration.

### 2. Duplicated code
**Smell:** Same logic in 2+ places.
**Fix:** Extract shared function. One source of truth.

### 3. Large class / God object
**Smell:** One class with 10+ unrelated responsibilities.
**Fix:** Split by concern. Each class one reason to change.

### 4. Long parameter list
**Smell:** Function with 5+ parameters.
**Fix:** Introduce parameter object or builder.

### 5. Feature envy
**Smell:** Method uses another object's data more than its own.
**Fix:** Move method to the object that owns the data.

### 6. Primitive obsession
**Smell:** Using strings/ints for domain concepts (email, phone, status).
**Fix:** Wrap in value objects with validation.

### 7. Magic numbers / strings
**Smell:** Unexplained literals (`if status === 2`, `* 0.15`).
**Fix:** Named constants with intent-revealing names.

### 8. Nested conditionals
**Smell:** Arrow code — 4+ levels of nesting.
**Fix:** Guard clauses, early returns, flatten.

### 9. Dead code
**Smell:** Unused functions, imports, commented-out blocks.
**Fix:** Delete. Git history has it if needed.

### 10. Inappropriate intimacy
**Smell:** One class reaches deep into another's internals.
**Fix:** Ask, don't reach. Add proper accessors or move behavior.

## Refactoring Operations

Quick reference — pick the right operation for each smell.

| Operation | When to use |
|-----------|-------------|
| Extract Method | Code fragment can be named and reused |
| Inline Method | Method body is clearer than the call |
| Extract Class | One class doing two things |
| Inline Class | Class adds no value, merge back |
| Rename | Name doesn't reveal intent |
| Introduce Parameter Object | 5+ parameters that travel together |
| Replace Conditional with Polymorphism | Switch/if on type code |
| Replace Magic Number with Constant | Unexplained literal |
| Decompose Conditional | Complex if-condition, extract to method |
| Consolidate Conditional | Same action from different conditions |
| Replace Nested Conditional with Guard Clauses | Arrow code, early returns |
| Introduce Null Object | Repeated null checks on same type |
| Replace Type Code with Class/Enum | Primitive used as type discriminator |
| Replace Inheritance with Delegation | Subclass only uses part of parent |
| Pull Up / Push Down Method | Method in wrong class in hierarchy |
| Remove Dead Code | Unused, unreachable, commented-out |

## Framework-specific notes

See `references/INDEX.md` at plugin root for stack-specific guidance.
Read the matching file for your project's stack.

## Preferred transformations

1. Read the plan file and find the step tagged `[simplify]`.
2. Run relevant tests before touching anything. If any test fails, report and stop.
3. **Scan the entire target file for every smell in the catalog.** Don't fix the first smell you see — count occurrences. Rank by frequency. Fix the most duplicated pattern first.
4. Match the smell to an operation from the catalog above.
5. Apply the transformation:
   - Guard clauses for early exits.
   - Clearer, intent-revealing names.
   - Small meaningful extractions (functions/methods).
   - Safe deduplication of repeated logic.
   - Dead code removal when confidence is high.
   - Flattening nested control flow where reasonable.
6. Run tests after each change. If a test fails and the fix isn't obvious, revert and report.

## Quality checklist

Verify after each simplification step:

**Code quality**
- [ ] Functions < 50 lines
- [ ] Functions do one thing
- [ ] No duplicated code remaining
- [ ] Descriptive names (variables, functions, classes)
- [ ] No magic numbers/strings
- [ ] Dead code removed

**Structure**
- [ ] Related code together
- [ ] Clear module boundaries preserved
- [ ] No circular dependencies introduced

**Safety**
- [ ] External behavior unchanged
- [ ] All existing tests still pass
- [ ] Edge cases considered

## Output format

Use `templates/refactor-plan.md` at plugin root as the output template.

1. Simplification findings.
2. Proposed small improvements.
3. Risks and invariants.
4. Step 1 patch only.
5. Optional next simplifications.

Write output to the plan file — read `config.md` at plugin root for path resolution.
Default fallback: `.local/tasks/refactor/refactor-plan.md`.

## Rules

Follow `PRINCIPLES.md` at plugin root.

- Do not combine multiple large simplifications into one step; keep patches reviewable.
- Avoid micro-optimizations unless they also improve clarity.
- Be explicit about any assumptions when removing or deduplicating code.

## Stop Conditions

Stop and ask if:
- Plan file is missing or the step tagged `[simplify]` cannot be found
- Simplification may change behavior — flag and confirm before acting
- Tests fail and the fix is not obvious — revert and report

## Example

### Scenario (before)

```csharp
public decimal CalculateTotal(Order order)
{
    decimal total = 0;
    if (order != null && order.Items != null)
    {
        foreach (var item in order.Items)
        {
            if (item != null && item.Quantity > 0 && item.Price > 0)
            {
                if (item.DiscountCode != null)
                {
                    total += item.Price * item.Quantity * GetDiscountFactor(item.DiscountCode);
                }
                else
                {
                    total += item.Price * item.Quantity;
                }
            }
        }
    }
    return total;
}
```

### Simplification ideas

- Guard clause for `order` and `Items`.
- Extract line-calculation into a separate method.
- Introduce clearer names for intermediate results.

### Scenario (after, conceptually)

```csharp
public decimal CalculateTotal(Order order)
{
    if (order?.Items == null) return 0;

    return order.Items
        .Where(IsBillableItem)
        .Sum(CalculateLineTotal);
}

private bool IsBillableItem(OrderItem item)
{
    return item != null && item.Quantity > 0 && item.Price > 0;
}

private decimal CalculateLineTotal(OrderItem item)
{
    var baseTotal = item.Price * item.Quantity;
    var discountFactor = item.DiscountCode != null
        ? GetDiscountFactor(item.DiscountCode)
        : 1m;

    return baseTotal * discountFactor;
}
```

- Behavior is unchanged, but:
  - nesting is reduced,
  - responsibilities are clearer,
  - testability is improved.