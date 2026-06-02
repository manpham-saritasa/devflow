---
name: plan
version: 0.2.0
description: Diagnose architectural friction, coupling, unclear ownership, and maintainability problems; produce a practical roadmap before refactoring.
triggers:
  - "plan"
  - "refactor"
  - "create a plan"
  - "review this code"
---

# Plan

Use this skill to review a codebase or target slice before implementation.
Invoked by refflow agent when no plan exists or architecture is unclear.

## When to use

Use `plan` when:
- the user asks for a review, audit, assessment, or roadmap,
- the right direction for refactoring is unclear,
- multiple symptoms exist (performance, complexity, slow delivery) and you need to find root causes,
- the team wants an architecture-focused document before changing code.

Do not use `plan` when:
- the user already has a clear architecture direction and only wants local clean-up,
- the request is a small, localized change that doesn't need architecture analysis.

## Goal

- Diagnose the current architecture.
- Identify strengths, friction points, and structural risks.
- Produce a practical roadmap ordered by impact and risk.
- Write the resulting plan to the plan file path.
  Read `config.md` at plugin root for path resolution rules.
  Default fallback: `.local/tasks/refactor/refactor-plan.md`.

## Review focus

Look for:
- unclear ownership and mixed responsibilities,
- shallow modules and overly fragmented concepts,
- excessive file hopping to understand one feature,
- coupling and dependency direction problems,
- framework or infrastructure details leaking into domain logic,
- duplicated orchestration or cross-cutting concerns,
- platform-specific code leaking into shared modules.

## Framework references

See `references/INDEX.md` at plugin root for stack-specific guidance.
Read the matching file for your project's stack.

## Output format

Use `templates/refactor-plan.md` at plugin root as the output template.

### Plan structure

```
## Refactor Plan: [title]

### Current State
[Brief description of how things work now]

### Target State
[Brief description of how things will work after]

### Affected Files
| File | Change | Depends on | Blocks |
|------|--------|------------|--------|
| path/a.ts | modify | — | Step 2 |
| path/b.ts | create | Step 1 | — |

### Execution Plan

#### Phase 1: [name]
- [ ] Step 1.1: [action] in `file.ts`
- [ ] Verify: [how to check it worked]

#### Phase 2: [name]
- [ ] Step 2.1: [action] in `file.ts`
- [ ] Verify: [how to check]

### Rollback Plan
If something fails:
1. `git checkout -- [files]` for reversible steps
2. [Manual undo steps for non-reversible]

### Risks
- [Potential issue and mitigation]

### Invariants
- Behaviors, contracts, and external effects that must not change.
```

## Self-Grill

Before finalizing the plan, pressure-test it against this checklist. Fix any issues inline — don't wait for a separate grill step.

1. **Requirements** — Are the task requirements clear and complete? If vague, ask user for clarification before proceeding.
2. **Invariants** — Are behaviors that must not change explicit and complete?
3. **Risks** — Does each step have a rollback path? If a step fails, what's the recovery?
4. **Validation** — Is every verify step concrete? Specific commands, tests, checks — not "run tests".
5. **Step size** — Is each step reversible? Single concern, < 5 files touched.
6. **Assumptions** — Are unverified assumptions marked as risks?
7. **Test gaps** — Are missing tests acknowledged? Manual-only checks must be explicit.

If any check fails, fix the plan before writing. Mark plan header with `**(GRILLED YYYY-MM-DD)**`.

For deeper design questioning (trade-offs, alternatives, team impact), optionally invoke `grill-me` after the plan is written.

1. Architecture summary.
2. Original specs — capture baseline behavior: APIs, business rules, side effects, test counts.
3. Strengths.
4. Friction points.
5. Recommendations — tagged with concern types: `[structure]`, `[simplify]`, or `[api]`.
6. Priority roadmap — phased execution plan with verify checkboxes.
7. Optional RFC candidates.

## Rules

Follow `PRINCIPLES.md` at plugin root.

- Tie recommendations to observed maintenance cost and change friction.
- If the codebase is very large, narrow the review to the most critical slice rather than attempting total coverage.

## Example

### Scenario
A backend service has:
- controllers that directly use `DbContext`,
- business rules in controllers and repositories,
- shared DTOs used across unrelated bounded contexts,
- repeated transaction logic in multiple places.

### Example output (abridged)

```
## Refactor Plan: Extract domain logic from OrderService

### Current State
- Monolithic ASP.NET backend. Controllers directly use DbContext.
- Business rules live in controllers and repositories.
- Shared DTOs used across bounded contexts.

### Target State
- Thin controllers, application services for orchestration.
- Domain services for business rules.
- Bounded-context-specific DTOs.

### Affected Files
| File | Change | Depends on | Blocks |
|------|--------|------------|--------|
| OrderService.cs | modify | — | Phase 2 |
| OrderDomainService.cs | create | Phase 1 | — |
| CustomerDto.cs | modify | Phase 3 | — |
| OrderDto.cs | modify | Phase 3 | — |

### Execution Plan

#### Phase 1: Extract application services
- [ ] Step 1.1: [structure] Create OrderAppService in `Orders/Application/`
- [ ] Verify: `dotnet test Orders.Tests`, all green
- [ ] Step 1.2: [simplify] Thin out 2 highest-risk controllers
- [ ] Verify: API integration tests pass

#### Phase 2: Move business rules to domain
- [ ] Step 2.1: [structure] Extract OrderDomainService from OrderService
- [ ] Verify: `dotnet test Orders.Domain.Tests`, 42/42 pass

#### Phase 3: Split shared DTOs
- [ ] Step 3.1: [api] Create bounded-context DTOs, keep old delegating
- [ ] Verify: All endpoints return same shape

### Rollback Plan
- Phase 1-2: `git checkout --` files, re-run tests
- Phase 3: Revert DTO changes, old DTOs still exist as fallback

### Risks
- No integration tests for email path — manual verification required
- Phase 3 DTO split may break internal callers — audit first

### Invariants
- POST /api/orders returns same shape
- Discount calculation unchanged
- Email still sent on status change
```