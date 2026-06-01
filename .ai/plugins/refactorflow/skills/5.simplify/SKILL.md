---
name: simplify
version: 0.1.0
description: Reduce local complexity, improve readability, naming, and control flow, and remove small-scale friction without changing behavior.
---

# Simplify

Use this skill when the plan step is tagged `[simplify]`.
Invoked by refactorflow agent during execution.

## When to use

This skill is invoked by the refactorflow agent in auto mode.
In manual mode, run directly when a plan step is tagged `[simplify]`.
Always create a plan with 1.review first.

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

## Framework-specific notes

See `references/INDEX.md` at plugin root for stack-specific guidance.
Read the matching file for your project's stack.

## Preferred transformations

- guard clauses for early exits,
- clearer, intent-revealing names,
- small meaningful extractions (functions/methods),
- safe deduplication of repeated logic,
- dead code removal when confidence is high,
- flattening nested control flow where reasonable.

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