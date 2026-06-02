# Refflow Plugin — Shared Configuration

All skills and the agent reference these paths. Resolve relative to the plugin root.

---

## Paths

| Variable | Value | Description |
|----------|-------|-------------|
| `TASKS_ROOT` | `.local/tasks` | Task evidence folder (repo-relative) |
| `TASK_DIR` | `[TASKS_ROOT]/[KEY]` | Per-task folder (matches devflow) |
| `PLAN_FILE_NAME` | `refactor-plan.md` | Plan output filename |
| `REVIEW_FILE_NAME` | `refactor-review.md` | Review output filename |
| `DEFAULT_PLAN_PATH` | `.local/tasks/refactor/refactor-plan.md` | Standalone — no task key |
| `DEFAULT_REVIEW_PATH` | `.local/tasks/refactor/refactor-review.md` | Standalone — no task key |

## Path resolution

1. If task key provided explicitly (e.g. `DEV-123`), use it.
2. If not, extract from current branch via regex `([A-Z0-9]+-\d+)`.
3. Check if `.local/tasks/{TASK_KEY}/task.md` exists (inside a devflow task).
4. If yes → write plan to `TASK_DIR/refactor-plan.md`, review to `TASK_DIR/refactor-review.md`.
5. If no → use `DEFAULT_PLAN_PATH`.

---

## Templates

Located in `templates/` relative to the plugin root.

| Variable | File |
|----------|------|
| `PLAN_TEMPLATE` | `templates/refactor-plan.md` |

---

## References

| Variable | Value |
|----------|-------|
| `PRINCIPLES` | `PRINCIPLES.md` |
| `REFERENCES_INDEX` | `references/INDEX.md` |
| `STACK_REFS` | `references/{stack}.md` |

---

## Behavior

| Variable | Value | Description |
|----------|-------|-------------|
| `SAVE_PLAN` | `true` | Auto-save plan to file |
| `UPDATE_DURING_EXECUTION` | `true` | Update plan file after each step |
| `EXECUTION_MODE` | `phase-by-phase` | Execution pacing |
| `REQUIRE_PLAN` | `true` | Require plan before large refactors |
| `SUPPORTED_MODES` | `plan`, `grill`, `execute`, `verify`, `status`, `auto` | Valid workflow modes |
