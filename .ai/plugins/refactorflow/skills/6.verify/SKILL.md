---
name: verify
version: 0.1.0
description: Verify a completed or in-progress refactor against the original specs and invariants from the plan.
---

# Verify
## When to use

This skill is invoked by the refactorflow agent in auto mode.
In manual mode, run directly after all plan steps are complete.
Always create a plan with 1.review first.

## Goal

Confirm the refactor did not break anything by comparing current state against
the plan's original specs and invariants.

## Process

1. Read the plan file (see `config.md` at plugin root for path resolution).
2. Extract `## Original specs` and `## Invariants`.
3. For each original spec:
   - Re-run the same check (API call, test suite, manual verification).
   - Report: pass / fail / changed.
4. For each invariant:
   - Verify it still holds.
   - Report: intact / broken.
5. Run the full test suite.
6. Produce a verification report.

## Verification checklist

- **API contracts** — Same inputs → same outputs, same status codes?
- **Business rules** — Discounts, calculations, side effects unchanged?
- **Test suite** — All tests pass? Same count as baseline? No new failures?
- **Invariants** — Every invariant from the plan still holds?
- **Side effects** — Emails, events, logs — still firing correctly?
- **Performance** — Any obvious regression? (optional, if spec captured timing)

## Output

```
## Verify Report

📋 Plan: [plan path]
📊 Steps verified: N of N

### Specs
| # | Spec | Result |
|---|------|--------|
| 1 | POST /api/orders → 201 | ✅ Pass |
| 2 | Discount 10% > $100 | ✅ Pass |
| 3 | Email on shipped | ✅ Pass |

### Invariants
| # | Invariant | Result |
|---|-----------|--------|
| 1 | Order response shape unchanged | ✅ Intact |
| 2 | Discount calculation unchanged | ✅ Intact |

### Tests
- Orders.Domain.Tests: 42/42 pass ✅
- Orders.Api.Tests: 18/18 pass ✅

### Verdict
✅ All specs match. All invariants intact. All tests pass.
Ready to merge.
```

If any spec fails or invariant breaks:
```
### Verdict
❌ Verification failed.
- Spec #3: Email not sent on shipped status — regression.
- Recommend: revert Step 3 or fix before merging.
```

## Rules

Follow `PRINCIPLES.md` at plugin root.

- Do not implement fixes — only report findings.
- Compare against the plan's original specs, not assumptions.
- If original specs are missing or incomplete, flag it and do best-effort verification.
- If tests don't exist for critical paths, note it as a risk.
