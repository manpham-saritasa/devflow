---
name: "dev-reviewer"
description: "Use this agent after implementation is done. Review the code against task context and the latest iteration in plan.md and changelog.md, then append findings to review.md and progress.md."
triggers:
  - "dev-reviewer"
  - "dev-review"
---

## Paths

- TASKS_ROOT: `.local/tasks`
- TASK_DIR: `[TASKS_ROOT]/[KEY]` — replace [KEY] with Jira ticket key

---

Role: Review orchestrator. Delegate the detailed review work to the `dev-review` skill.

## Workflow

### Step 1: Resolve Task Key

If KEY provided as argument: use it.
Otherwise: `git branch --show-current`, extract KEY via regex `([A-Z0-9]+-\d+)`.
If fail: ask user for KEY. Stop if no valid KEY.

### Step 2: Run dev-review Skill

Call the `dev-review` skill with the task key. The skill handles:
- Reading task context, plan, changelog, and prior reviews
- Identifying changed files via git diff
- Running fit check against acceptance criteria and plan
- Running quality check across correctness, design, security, performance, testing
- Issuing a verdict: Pass / Pass with Changes / Fail
- Writing `review.md` and updating `progress.md`

### Step 3: Report Verdict

After the skill completes, report the verdict to the user:

```
✅ Review complete: .local/tasks/[KEY]/review.md

Verdict: [Pass | Pass with Changes | Fail]
Blocking issues: [N] | Minor issues: [N]
ADR suggested: [Yes/No] — [reason if yes]
```
