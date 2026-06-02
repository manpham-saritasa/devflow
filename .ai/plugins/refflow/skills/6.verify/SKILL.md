---
name: verify
version: 0.1.0
description: Verify refactor results against the plan's original specs, invariants, and code quality. Produces a verdict.
---

# Verify

Use this skill to verify refactor results against the plan.
See `PRINCIPLES.md` for invocation modes.
Manual trigger: run after all plan steps complete.

## Goal

Verify the refactor against the plan's original specs, invariants, and code quality.
Produce a verdict: Pass / Pass with Changes / Fail.

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

### Specs & invariants
- **API contracts** — Same inputs → same outputs, same status codes?
- **Business rules** — Discounts, calculations, side effects unchanged?
- **Invariants** — Every invariant from the plan still holds?
- **Side effects** — Emails, events, logs — still firing correctly?

### Code quality (from dev-review)
- **Correctness** — Edge cases, null handling, control flow, regression risk.
- **Readability** — Naming, duplication, complexity, maintainability.
- **Design** — Alignment with abstractions, separation of concerns, patterns.
- **Security** — Validation, auth/authz, injection, data exposure.
- **Performance** — Queries, loops, memory, repeated work.
- **Error handling** — Logging, failure behavior.

### Tests
- **Test suite** — All tests pass? Same count as baseline? No new failures?
- **Coverage** — Did the refactor expose untested paths?

## Output

Produce a verify report and write it to the review file.

When a devflow task folder exists (`.local/tasks/{KEY}/task.md`):
write to `.local/tasks/{KEY}/refactor-review.md`.
When standalone: write to `.local/tasks/refactor/refactor-review.md`.
Fallback: report inline in chat.

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

### Quality
| Dimension | Finding | Severity |
|-----------|---------|----------|
| Correctness | No regressions | ✅ |
| Readability | Improved after simplify step | ✅ |
| Security | No new exposure | ✅ |
| Error handling | Unchanged | ✅ |

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
