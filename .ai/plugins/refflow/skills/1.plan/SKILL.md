---
name: plan
version: 0.1.0
description: Diagnose architectural friction, coupling, unclear ownership, and maintainability problems; produce a practical roadmap before refactoring.
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

1. Architecture summary.
2. Original specs — capture baseline behavior: APIs, business rules, side effects, test counts.
3. Strengths.
4. Friction points.
5. Recommendations.
6. Priority roadmap.
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

1. Architecture summary  
   - Monolithic backend with ASP.NET controllers, EF Core, and shared DTOs across domains. Controllers mix HTTP handling, transaction orchestration, and business rules.

2. Strengths  
   - Consistent technology stack (.NET, EF Core).  
   - Reasonable separation between read and write paths in some areas.

3. Friction points  
   - Controllers directly depend on `DbContext`, making business rules hard to reuse.  
   - Shared `CustomerDto` and `OrderDto` used across bounded contexts, leaking internal concerns.  
   - Transaction logic duplicated in multiple controllers and services.

4. Recommendations  
   - Introduce application services to orchestrate use cases; keep controllers thin.  
   - Move business rules into domain services or aggregates.  
   - Split shared DTOs by bounded context; define mapping at the edges.  
   - Centralize transaction and unit-of-work behavior in one cross-cutting component.

5. Priority roadmap  
   - Phase 1: Extract application services for the 2 highest-risk controllers.  
   - Phase 2: Move business rules from controllers into domain services.  
   - Phase 3: Split shared DTOs and update mapping layers.  
   - Phase 4: Introduce centralized transaction orchestration and remove duplicates.