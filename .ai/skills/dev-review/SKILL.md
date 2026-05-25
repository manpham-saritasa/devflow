---
name: dev-review
description: Review implemented code against task context and the latest plan/changelog iteration. Append findings to review.md and progress.md.
---

## Paths

- DEV_ROOT: `.local`
- TASK_DIR: `[DEV_ROOT]/tasks/[KEY]`
- REVIEW_TEMPLATE: `templates/review-template.md`
- PROGRESS_TEMPLATE: `templates/progress-template.md`

---

## Workflow

### Step 1: Read Context

Read from `TASK_DIR`:
- `task.md`, `raw.md` — requirements, constraints, acceptance criteria
- `plan.md` — latest iteration as planned baseline
- `changelog.md` — latest iteration as claimed summary (not source of truth)
- `review.md` — prior passes, unresolved findings
- `progress.md` — current state, active iteration

### Step 2: Identify Changes

```bash
git diff develop...HEAD
```
Fallback: `git diff main...HEAD`

Collect `diff_files[]`, `plan_files[]`, compute `unexpected_files[]`.

### Step 3: Fit Check

- Evaluate every acceptance criterion and planned item
- Accept deviations only when result is equivalent or better
- Check `Out of scope`, `Do not modify`, and other plan constraints
- Verify the latest changelog iteration accurately reflects implementation

### Step 4: Quality Check

Review across these dimensions:
- **Correctness:** edge cases, null handling, control flow, regression risk
- **Quality:** readability, naming, duplication, complexity, maintainability
- **Design:** alignment with abstractions, separation of concerns, patterns
- **Security:** validation, auth/authz, injection, data exposure
- **Performance:** queries, loops, memory, repeated work
- **Error handling:** logging, failure behavior
- **Testing:** coverage, adequacy of verification

Label every issue: `[blocking]` or `[minor]`.

### Step 5: Verdict

- **Pass** — fit clean, no blocking issues
- **Pass with Changes** — fit acceptable, minor issues remain
- **Fail** — acceptance criterion fails, plan violation, or blocking issue exists

### Step 6: Write Review

Append to `TASK_DIR/review.md` using `REVIEW_TEMPLATE`:
- New review pass for the active iteration
- Every acceptance criterion in `Acceptance Criteria Review`
- Every planned change in `Plan Coverage Review`
- Every issue with severity, category, location, explanation, suggested fix
- Empty sections: write `None`

### Step 7: Update Progress

Update `TASK_DIR/progress.md`:
- Status: `Approved`, `Approved with Changes`, `Rejected`, `Blocked`, or `Needs Review`
- `ADR Suggested`: `Yes`/`No` with reason if yes

## ADR Triggers

Set `ADR Suggested = Yes` if:
- New third-party service or external API integrated
- New library/package introduces new capability or pattern
- Existing technical approach replaced
- Database schema changed
- Auth flow structure changed

Do not create ADR files — only recommend.
