---
name: "devflow"
description: "Full development flow agent. Run plan → code → review in sequence for a task, with user checkpoints between each phase."
triggers:
  - "devflow"
  - "/devflow"
  - "/dev-flow"
---

## Paths

- TASKS_ROOT: `.local/tasks`
- TASK_DIR: `[TASKS_ROOT]/[KEY]` — replace [KEY] with Jira ticket key

---

Role: Development flow orchestrator. Run the complete plan → code → review pipeline by delegating directly to `dev-plan`, `dev-code`, and `dev-review` skills in sequence. Stop at each phase for user confirmation before continuing.

## Workflow

### Step 0: Setup Task Folder

If `TASK_DIR` does not exist, create it.
If `TASK_DIR/task.md` does not exist and Jira MCP is available, fetch the Jira issue and save key details to `task.md`.

### Step 1: Resolve Task Key

If KEY provided as argument: use it.
Otherwise: `git branch --show-current`, extract KEY via regex `([A-Z0-9]+-\d+)`.
If fail: ask user for KEY. Stop if no valid KEY.

### Phase 1 — Plan (`dev-plan` skill)

Read and execute `.ai/skills/dev-plan/SKILL.md`. The skill handles:
- Gathering task context and investigating the codebase
- Repo-match check: is this the right repo for the task?
- Outputting an investigation summary for user confirmation
- Writing `plan.md` + `progress.md`

**Checkpoint:** "Proceed to implementation? (yes/no/adjust)"

- `yes` → Phase 2.
- `no` → stop.
- `adjust` → re-run planning with feedback.

### Phase 2 — Code (`dev-code` skill)

Read and execute `.ai/skills/dev-code/SKILL.md`. The skill handles:
- Reading `plan.md` and implementing `## Proposed Changes` in order
- Verifying each change
- Writing `changelog.md` + updating `progress.md`
- Reporting progress after each major item

**Stop conditions:** If the skill hits a conflict, failure, scope creep, or violated invariant — stop and relay to user.

**Checkpoint:** "Proceed to review? (yes/no)"

- `yes` → Phase 3.
- `no` → stop (review later with `/devflow [KEY] --review-only`).

### Phase 3 — Review (`dev-review` skill)

Read and execute `.ai/skills/dev-review/SKILL.md`. The skill handles:
- Identifying changes via git diff
- Fit check against acceptance criteria and plan
- Quality check across correctness, design, security, performance, testing
- Issuing a verdict and writing `review.md` + updating `progress.md`

### Final Summary

```
✅ Devflow complete for [KEY]

Plan: .local/tasks/[KEY]/plan.md (Iteration [N])
Code: .local/tasks/[KEY]/changelog.md
Review: .local/tasks/[KEY]/review.md

Verdict: [Pass | Pass with Changes | Fail]
Next: [ship with /dev-ship | address findings | re-plan]
```

## Phase Independence

Skip phases with flags:

- `/devflow [KEY] --plan-only` — stop after planning
- `/devflow [KEY] --code-only` — skip planning, start from code (requires existing `plan.md`)
- `/devflow [KEY] --review-only` — only run review

No flags → run all three phases with checkpoints.
