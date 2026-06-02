# Android guidance

## Architecture review focus
- Examine boundaries between activities/fragments or composables, view models, repositories, use cases, and data sources.
- Look for platform concerns leaking into domain logic and for excessive ceremonial layering that increases file hopping.
- Identify god view models or duplicated use-case wrappers.

## Structure refactor focus
- Prefer feature-oriented packages and clear ownership of UI, domain, and data concerns.
- Keep side effects and state transitions explicit.
- Avoid unnecessary layers that do not provide real isolation.

## Simplify refactor focus
- Prefer clearer state handling, flatter branching, smaller view-model methods, and more explicit naming of UI states and actions.
- Be careful with lifecycle interactions, coroutine scope behavior, nullability, and recomposition-sensitive logic.