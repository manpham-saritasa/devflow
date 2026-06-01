# React guidance

## Architecture review focus
- Examine feature boundaries, state ownership, async orchestration, and whether one screen can be understood without excessive file hopping.
- Check whether shared components are truly reusable or whether feature-specific logic has leaked into them.
- Look for state, data loading, and side effects being spread across too many layers.

## Structure refactor focus
- Prefer feature-oriented grouping over broad technical buckets when that improves comprehension.
- Separate presentational UI from orchestration and side effects when the current component mixes too many concerns.
- Keep state as close as practical to where it is used.
- Avoid generic hooks or helper buckets that become hidden dependency hubs.

## Simplify refactor focus
- Prefer early returns for loading, error, empty, and forbidden states.
- Reduce nested ternaries and move heavy derived logic out of JSX into clearly named helpers or hooks.
- Be careful with hook ordering, memoization complexity, and unnecessary abstractions.