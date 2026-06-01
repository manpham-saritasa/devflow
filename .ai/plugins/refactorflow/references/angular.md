# Angular guidance

## Architecture review focus
- Examine whether the app is organized by feature or broad technical buckets.
- Check whether services, standalone components, modules, and state boundaries reflect business features rather than convenience groupings.
- Look for god services, duplicated RxJS orchestration, and cross-feature imports that weaken boundaries.

## Structure refactor focus
- Prefer feature-oriented folders and clear separation between components, services, state, and API adapters.
- Keep orchestration out of presentational components where possible.
- Avoid giant shared modules or shared services that hide real ownership.

## Simplify refactor focus
- Prefer clearer observable pipelines, smaller template logic, named derived streams, and reduced branching in components.
- Be careful with subscription lifecycles, side effects inside RxJS chains, and over-abstracting simple template logic.