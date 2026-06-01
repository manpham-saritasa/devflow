# PHP guidance

## Architecture review focus
- Examine framework boundaries, controller/service ownership, domain logic placement, and whether legacy procedural areas are mixed with layered code in confusing ways.
- Look for framework lifecycle code leaking too deeply into business logic.
- Identify dynamic array-shape contracts or magic behavior that makes the system hard to reason about.

## Structure refactor focus
- Prefer separating controllers, services, domain rules, persistence, and view concerns.
- Reduce framework leakage into domain code.
- Replace generic helper buckets with domain ownership where possible.

## Simplify refactor focus
- Prefer guard clauses, clearer naming, smaller methods, safer extraction of repeated logic, and removal of dead branches when confidence is high.
- Be careful with dynamic typing assumptions, array-shape contracts, magic methods, and framework lifecycle hooks.