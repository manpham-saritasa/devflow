# Refactorflow Plugin — Shared Configuration

All skills and the agent reference these paths. Resolve relative to the plugin root.

---

## Paths

| Variable | Value | Description |
|----------|-------|-------------|
| `PLAN_FILE_NAME` | `refactor-plan.md` | Always this filename |
| `DEFAULT_PLAN_PATH` | `.local/tasks/refactor/refactor-plan.md` | When no task key |
| `TASK_PLAN_PATTERN` | `.local/tasks/{TASK_KEY}/refactor-plan.md` | Inside a devflow task |

## Path resolution

1. Check if `.local/tasks/{TASK_KEY}/task.md` exists (inside a devflow task).
2. If yes → resolve `TASK_PLAN_PATTERN` with `{TASK_KEY}` replaced.
3. If no → use `DEFAULT_PLAN_PATH`.

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
