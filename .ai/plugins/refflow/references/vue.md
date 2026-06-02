# Vue guidance

## Architecture review focus
- Examine whether code is grouped by feature or by generic folders.
- Check whether components, composables, stores, and API adapters have clear ownership.
- Look for giant stores or composables that mix unrelated domains.

## Structure refactor focus
- Prefer feature grouping, focused composables, and clear separation between components, stores, and API adapters.
- Keep reusable UI genuinely reusable; do not force business logic into shared components.
- Avoid vague shared buckets that become dumping grounds.

## Simplify refactor focus
- Move heavy computed or branching logic out of templates into named computed values or composables.
- Reduce watcher complexity and make reactive side effects explicit.
- Be careful with implicit reactivity behavior and overuse of global stores.