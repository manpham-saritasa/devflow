---
name: dev-review
description: Review implemented code against task context and the latest plan/changelog iteration. Append findings to review.md and progress.md.
---

## Paths

- TASKS_ROOT: `.local/tasks`
- TASK_DIR: `[TASKS_ROOT]/[KEY]`
- REVIEW_TEMPLATE: `.ai/agents/templates/review-template.md`
- PROGRESS_TEMPLATE: `.ai/agents/templates/progress-template.md`

---

## Workflow

### Step 0: Check Templates

Check `REVIEW_TEMPLATE` and `PROGRESS_TEMPLATE` exist. Missing → stop: "Error: template not found."

### Step 1: Read Context

Read from `TASK_DIR`:
- `task.md`, `raw.md` — requirements, constraints, acceptance criteria
- `plan.md` — latest iteration as planned baseline
- `changelog.md` — latest iteration as claimed summary (not source of truth)
- `review.md` — prior passes, determine next review pass number, track unresolved findings
- `progress.md` — current state, active iteration

### Step 2: Identify Changes

```bash
git diff develop...HEAD
```
Fallback: `git diff main...HEAD`

Collect `diff_files[]` from the branch diff.
Collect `plan_files[]` from the latest plan iteration when explicit file paths are listed.
Compute `unexpected_files[]` = files in diff but not in plan. Flag them — do not auto-fail if the change is justified and low-risk.
Review full changed files when context is needed to judge correctness, not just diff hunks.

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
- `[blocking]` = broken requirement, crash, security flaw, data loss risk, regression risk, invariant violation.
- `[minor]` = readability, consistency, maintainability, non-critical verification gap.

### Step 5: Verdict

- **Pass** — fit clean, no blocking issues
- **Pass with Changes** — fit acceptable, minor issues remain
- **Fail** — acceptance criterion fails, plan violation, or blocking issue exists

### Step 6: Write Review

Determine the next review pass number from prior `review.md` (default: 1).
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

## Self-Check

- [ ] Review compared actual code against task context, plan, and changelog?
- [ ] Repository conventions and architecture respected?
- [ ] Full files reviewed when context needed, not just diff hunks?
- [ ] Fit and quality reviewed separately?
- [ ] Unexpected files flagged?
- [ ] Blocking vs minor issues distinguished?
- [ ] Review pass number determined from prior reviews?
- [ ] Progress.md updated?
- [ ] Verdict matches findings?
- [ ] ADR recommended only when appropriate?
