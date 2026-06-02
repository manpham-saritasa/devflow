# iOS guidance

## Architecture review focus
- Examine boundaries between views, view controllers or SwiftUI composition, navigation/coordinators, networking, persistence, and domain logic.
- Look for UI state and business rules being mixed too tightly.
- Identify view models or coordinators that are becoming god objects.

## Structure refactor focus
- Prefer clear separation between UI composition, state management, navigation, service clients, and domain rules.
- Keep networking and persistence out of UI layers.
- Avoid making one view model the owner of unrelated concerns.

## Simplify refactor focus
- Prefer clearer names, smaller view-model methods, flatter control flow, and isolation of side effects.
- Be careful with async state updates, main-thread assumptions, retain cycles, and lifecycle-driven behavior.