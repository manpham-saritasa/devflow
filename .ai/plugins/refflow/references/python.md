# Python guidance

## Architecture review focus
- Examine package ownership, import direction, side-effect boundaries, and separation between domain logic and entry points.
- Check whether modules do significant work at import time; import-time side effects make code harder to reason about and test.
- Look for fragmented logic spread across too many tiny modules or catch-all files like `utils.py`.
- Identify whether CLI, service, or worker entry points are explicit and easy to locate.

## Structure refactor focus
- Prefer cohesive packages, isolated side effects, and clear module ownership.
- Keep infrastructure concerns such as I/O, HTTP, persistence, or CLI wiring away from pure business logic.
- Avoid vague buckets like `helpers`, `common`, or `misc` when a domain-specific module name is possible.
- Keep public module exports explicit.

## Simplify refactor focus
- Prefer early returns, clearer local names, small meaningful extractions, and readable control flow.
- Be careful with truthiness, exception behavior, generators, context managers, and mutability.
- Avoid hiding important side effects in boolean expressions, comprehensions, or decorators when that makes behavior harder to follow.