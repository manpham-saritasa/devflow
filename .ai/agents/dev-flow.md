---
name: "devflow"
description: "Full development flow agent. Run plan → code → review in sequence for a task, with user checkpoints between each phase."
triggers:
  - "devflow"
  - "/devflow"
---

## Paths

- TASKS_ROOT: `.local/tasks`
- TASK_DIR: `[TASKS_ROOT]/[KEY]` — replace [KEY] with Jira ticket key

---

Role: Development flow orchestrator. Run the complete plan → code → review pipeline by delegating to `dev-plan`, `dev-code`, and `dev-review` skills in sequence. Stop at each phase for user confirmation before continuing.

## Workflow

### Step 1: Resolve Task Key

If KEY provided as argument: use it.
Otherwise: `git branch --show-current`, extract KEY via regex `([A-Z0-9]+-\d+)`.
If fail: ask user for KEY. Stop if no valid KEY.

### Phase 1 — Plan

Run the `dev-plan` skill. It will:
- Gather task context and investigate the codebase
- Output an investigation summary
- Wait for user confirmation before writing `plan.md`

**Checkpoint:** After the plan is created, ask: "Proceed to implementation? (yes/no/adjust)"

- `yes` → continue to Phase 2.
- `no` → stop.
- `adjust` → re-run planning with feedback.

### Phase 2 — Code

Run the `dev-code` skill. It will:
- Read `plan.md` and implement `## Proposed Changes` in order
- Verify each change
- Write `changelog.md` and `progress.md`
- Report progress after each major item

**Stop conditions:** If the skill hits a conflict, failure, or scope creep, stop and relay to the user immediately.

**Checkpoint:** After implementation, ask: "Proceed to review? (yes/no)"

- `yes` → continue to Phase 3.
- `no` → stop (can review later with `/dev-reviewer [KEY]`).

### Phase 3 — Review

Run the `dev-review` skill. It will:
- Run fit check against acceptance criteria and plan
- Run quality check across correctness, design, security, performance, testing
- Issue a verdict and write `review.md`

### Final Summary

After all phases complete:

```
✅ Devflow complete for [KEY]

Plan: .local/tasks/[KEY]/plan.md (Iteration [N])
Code: .local/tasks/[KEY]/changelog.md
Review: .local/tasks/[KEY]/review.md

Verdict: [Pass | Pass with Changes | Fail]
Next: [ship with /dev-ship | re-plan | address review findings]
```

## Phase Independence

Each phase can be run independently if desired:

- `/devflow [KEY] --plan-only` — stop after planning
- `/devflow [KEY] --code-only` — skip planning, start from code
- `/devflow [KEY] --review-only` — only run review

If no flag, run all three phases in sequence with checkpoints.
