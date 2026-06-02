# Refactor Plan

> Fill this template after `plan` runs. Grill before executing.
> Review after all steps complete.

## Goal and scope
- What problem are we solving? What is explicitly out of scope?
- Example: "Extract domain logic from OrderService without changing Order API."

## Current State
- Brief description of how things work now.

## Target State
- Brief description of how things will work after.

## Original specs
- Baseline behavior captured before any changes. Used by `verify` at the end.
- APIs: endpoints, inputs, outputs, status codes, error responses.
- Behavior: key business rules, side effects, edge cases.
- Tests: what test suites cover this code, how many pass today.
- Example:
  - "POST /api/orders with {customerId, items} → 201 {orderId, status, total}"
  - "Discount: 10% off orders > $100"
  - "Email sent to customer on status change to 'shipped'"
  - "42 tests in Orders.Domain.Tests, all green"

## Findings
- Key architecture / structure / simplification issues found during review.
- Example: "OrderService mixes HTTP mapping, discount rules, persistence, and email."

## Affected Files
| File | Change | Depends on | Blocks |
|------|--------|------------|--------|
| path/a.ts | modify | — | Step 2 |
| path/b.ts | create | Step 1 | — |

## Invariants
- Behaviors, contracts, and external effects that must not change.
- Example: "POST /api/orders returns same shape. Discount calculation unchanged. Email still sent."

## Risks and unknowns
- Migration risks, test gaps, assumptions, open questions.
- Example: "No integration tests for email path. Unknown: does discount apply to digital goods?"

## Execution Plan

### Phase 1: [name]
- [ ] Step 1.1: [concern tag] [action] in `file.ts`
- [ ] Verify: [how to check it worked]

### Phase 2: [name]
- [ ] Step 2.1: [concern tag] [action] in `file.ts`
- [ ] Verify: [how to check]

## Rollback Plan
If something fails:
1. `git checkout -- [files]` for reversible steps
2. [Manual undo steps for non-reversible steps]

## Validation
- Per step: exact tests to run, commands, manual checks.
- Example: "Step 1: run `dotnet test Orders.Domain.Tests`, verify all green."

## Progress
- [ ] Phase 1 — not started
- [ ] Phase 2 — not started
- Track surprises and follow-ups here.

---

*Last updated: YYYY-MM-DD*
