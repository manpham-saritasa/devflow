---
name: structure
version: 0.1.0
description: Improve module boundaries, ownership, dependency direction, and file layout without changing behavior.
---

# Structure

Use this skill when the plan step is tagged `[structure]`.
Invoked by refflow agent during execution.

## When to use

See `PRINCIPLES.md` for invocation modes.
Manual trigger: run when a plan step is tagged `[structure]`.

## Goal

Improve code organization, cohesion, and ownership without changing runtime behavior, public behavior, or business rules.

## Focus

Apply this skill to:
- mixed-responsibility files,
- god modules,
- boundary confusion,
- circular dependencies,
- vague shared buckets (e.g. `Common`, `Utils`, `Helpers`),
- concepts spread across too many tiny files,
- orchestration mixed with domain logic,
- platform-specific concerns leaking into shared layers.

## Framework-specific notes

See `references/INDEX.md` at plugin root for stack-specific guidance.
Read the matching file for your project's stack.

## Process

1. Read the plan file and find the step tagged `[structure]`.
2. Run relevant tests before touching anything. If any test fails, report and stop.
3. Identify structural findings.
4. Propose a target structure.
5. Plan the smallest safe sequence of changes.
6. List invariants and risks.
7. Execute only the first safe step when implementation is requested.
8. Run tests after each change. If a test fails and the fix isn't obvious, revert and report.

## Output format

Use `templates/refactor-plan.md` at plugin root as the output template.

1. Structural findings.
2. Proposed target structure.
3. Refactor plan in small steps.
4. Invariants and risks.
5. Step 1 changes only (if implementation is requested).

Write output to the plan file — read `config.md` at plugin root for path resolution.
Default fallback: `.local/tasks/refactor/refactor-plan.md`.

## Rules

Follow `PRINCIPLES.md` at plugin root.

- Prefer move, split, rename, or consolidation over rewrite.
- Avoid moving logic across layers unless necessary and justified.
- Stop after one bounded step unless the user explicitly asks to continue with another step.
- Ask for confirmation when structural changes affect many files or modules.

## Stop Conditions

Stop and ask if:
- Plan file is missing or the step tagged `[structure]` cannot be found
- Tests fail and the fix is not obvious — revert and report
- Change scope expands beyond the single planned step
- Invariant or business rule appears at risk

## Example

### Scenario
A single `OrderService.cs` file:
- handles HTTP DTO mapping,
- contains business rules for discounts,
- talks directly to EF repositories,
- publishes domain events,
- and sends emails.

### Example structural findings

- Problem: `OrderService` mixes transport mapping, domain rules, persistence, and side effects (email).  
- Friction: Any change requires touching one giant file; tests must mock multiple concerns; AI and humans struggle to see clear seams.  
- Remedy: Split into orchestration, domain rules, and infrastructure adapters.

### Example target structure (abridged)
```
Orders/
Application/
OrderAppService.cs // Orchestration
Domain/
OrderDomainService.cs // Business rules
OrderDiscountPolicy.cs
Infrastructure/
OrderRepository.cs // Persistence
OrderEmailNotifier.cs // Email adapter
```

### Example Step 1 plan

- Goal: Extract domain rules from `OrderService` into `OrderDomainService`.  
- Files: `OrderService.cs`, new `OrderDomainService.cs`.  
- Why now: Lowest-risk separable responsibility, reduces mixing of rules and IO.  
- Validation: Ensure all existing tests pass; add focused tests for `OrderDomainService` if available.