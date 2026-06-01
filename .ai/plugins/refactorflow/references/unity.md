# Unity guidance

## Architecture review focus
- Examine scene ownership, MonoBehaviour responsibility, ScriptableObject usage, and separation between gameplay logic and engine wiring.
- Look for god managers, hidden singleton coupling, and logic scattered across many Update loops.
- Check whether reusable systems are trapped in scene-specific components.

## Structure refactor focus
- Prefer separating gameplay rules from MonoBehaviour glue.
- Isolate input, state, UI, save/load, and integration concerns.
- Keep scene-specific code distinct from reusable systems.

## Simplify refactor focus
- Prefer clearer method names, reduced branching in Update and event handlers, and extraction of meaningful gameplay calculations.
- Be careful with Unity lifecycle order, serialized-field expectations, inspector wiring, and play-mode assumptions.