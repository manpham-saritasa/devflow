# Devflow Plugin — Shared Configuration

All skills and agents in this plugin reference these paths. Resolve relative to the plugin root.

---

## Paths

| Variable | Value | Description |
|----------|-------|-------------|
| `TASKS_ROOT` | `.local/tasks` | Task evidence folder (repo-relative) |
| `TASK_DIR` | `[TASKS_ROOT]/[KEY]` | Per-task folder |
| `ADR_DIR` | `docs/adrs` | Architecture Decision Records folder |

---

## Path resolution

1. If task key provided explicitly (e.g. `DEV-123`), use it.
2. If not, extract from current branch via regex `([A-Z0-9]+-\d+)`.
3. Resolve `TASK_DIR` with `{KEY}` replaced.

---

## Work Mode

| Variable | Value | Description |
|----------|-------|-------------|
| `WORK_MODE` | `default` | `default` (full file pipeline), `manual` (chat only, no artifact files) |

---

## Templates

Located in `templates/` relative to the plugin root.

| Variable | File |
|----------|------|
| `PLAN_TEMPLATE` | `templates/plan-template.md` |
| `CHANGELOG_TEMPLATE` | `templates/changelog-template.md` |
| `REVIEW_TEMPLATE` | `templates/review-template.md` |

---

## Merge Strategy

| Variable | Value | Description |
|----------|-------|-------------|
| `MERGE_STRATEGY` | `--merge` | Strategy passed to `gh pr merge`. Options: `--merge` (preserve history), `--rebase`, `--squash`. |
