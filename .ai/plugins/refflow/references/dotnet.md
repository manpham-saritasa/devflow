# .NET guidance

## Architecture review focus
- Examine bounded contexts, layering in practice, namespace ownership, and whether application, domain, infrastructure, and API responsibilities are separated cleanly.
- Check whether dependencies point inward consistently; in Clean Architecture, outer layers may depend on inner layers, but not the reverse.
- Look for EF Core, HTTP, file system, or framework details leaking into domain or application logic.
- Identify interfaces that are defined in the wrong layer; interfaces should usually live with the code that consumes them, not the implementation that fulfills them.

## Structure refactor focus
- Prefer separating transport, application, domain, and infrastructure concerns.
- Keep projects or folders aligned with clear ownership, for example Domain, Application, Infrastructure, and API when that matches the codebase shape.
- Reduce controllers, handlers, or services that combine orchestration, business rules, persistence, and mapping.
- Avoid generic shared buckets unless a true cross-cutting abstraction exists.

## Simplify refactor focus
- Prefer guard clauses, intent-revealing names, small extractions, and reduction of repetitive mapping or null-handling noise.
- Be careful with async flow, exception behavior, LINQ semantics, disposal, and cancellation behavior; .NET async code often relies on cooperative cancellation through `CancellationToken`.
- Keep side effects explicit rather than buried inside helper methods or LINQ chains.