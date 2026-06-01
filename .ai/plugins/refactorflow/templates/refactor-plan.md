# Refactor Plan

> Fill this template after `review` runs. Grill before executing.
> Verify after all steps complete.

## Goal and scope
- What problem are we solving? What is explicitly out of scope?
- Example: "Extract domain logic from OrderService without changing Order API."

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

## Invariants
- Behaviors, contracts, and external effects that must not change.
- Example: "POST /api/orders returns same shape. Discount calculation unchanged. Email still sent."

## Risks and unknowns
- Migration risks, test gaps, assumptions, open questions.
- Example: "No integration tests for email path. Unknown: does discount apply to digital goods?"

## Phased plan
- Number each step. Order by risk (lowest first).
- Each step = one reversible change with concrete validation.
- Tag each step with its concern type: `[structure]`, `[simplify]`, or `[api]`.

1. Phase 1 / Step 1 — `[structure]` description, files touched, why first.
2. Phase 1 / Step 2 — `[simplify]` ...
3. Phase 2 / Step 1 — `[api]` ...

## Validation
- Per step: exact tests to run, commands, manual checks.
- Example: "Step 1: run `dotnet test Orders.Domain.Tests`, verify all green."

## Progress
- [ ] Step 1 — not started
- [ ] Step 2 — not started
- Track surprises and follow-ups here.

---

*Last updated: YYYY-MM-DD*
