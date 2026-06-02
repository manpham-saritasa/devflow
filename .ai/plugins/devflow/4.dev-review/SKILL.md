---
name: dev-review
description: Review implemented code against task context and the latest plan/changelog iteration. Append findings to review.md and update plan.md progress.
triggers:
  - "dev-review"
  - "devreview"
---

## Paths

Read shared paths from `config.md`.
---

## Workflow

Check required templates from `config.md` exist. Missing → stop.

### Step 1: Read Context

Read all available files from `TASK_DIR/`. Missing files are not errors.

### Step 1.5: Detect Task Type

Check the plan's `**Type:**` field:
- `**Type:** refactor` → refactor already verified by 6.verify.
  No further review needed. Skip entire workflow.
  Report: "Refactor verified by 6.verify. See `refactor-review.md`."
  Update plan.md progress with verdict from refactor-review.md.
- `**Type:** feature` or missing → continue to Step 2.


### Step 2: Identify Changes

```bash
git diff [BASE_BRANCH]...HEAD  # main if no develop
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

### Step 4: Run Tests

Run the relevant test suite before proceeding:
```bash
# Run tests for the changed area. Prefer the smallest command that covers the diff.
```

If tests fail: list failures, flag as `[blocking]`, stop. Do not produce a verdict.
If no tests exist: note it as a finding under Test & Verification Review.
If tests pass: continue to quality check.

### Step 4b: Quality Check

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

### Step 5.5: Changelog Gap Check

Before writing the review, compare `git diff` against the latest changelog iteration:

- Identify changes present in the diff but not in `changelog.md`.
- If small unlogged manual fixes found:
  - Prompt user: "Found [N] unlogged changes. Describe them and I'll add them to the changelog."
  - Update the latest changelog iteration: set `**Delivery:** Mixed`, note manual items in `### Summary`.
  - Continue with the review.
- If large unlogged changes found (new files, significant logic):
  - Flag as a review finding: "Significant unlogged changes detected. Consider running `dev-code` to create a proper iteration before review."
  - Do not auto-append to changelog — the user should plan these properly.

### Step 6: Write Review

**Manual mode:** Skip file writes. Present findings and verdict in chat.

Determine the next review pass number from prior `review.md` (default: 1).
Append to `TASK_DIR/review.md` using `templates/review-template.md`:
- New review pass for the active iteration
- Every acceptance criterion in `Acceptance Criteria Review`
- Every planned change in `Plan Coverage Review`
- Every issue with severity, category, location, explanation, suggested fix
- Empty sections: write `None`

### Step 7: Update Progress in Plan

Update the `## Progress` section in `TASK_DIR/plan.md`:
- Tick relevant checkboxes if review passes.
- Append a row to the progress table:
  `| [date] | — | Review: [Pass / Pass with Changes / Fail] |`
- Update the `Current status` field: `Approved`, `Approved with Changes`, `Rejected`, or `Blocked`.
- `ADR Suggested`: `Yes`/`No` with reason if yes

## ADR Triggers

See decision triggers in `8.dev-adr/SKILL.md`. Set `ADR Suggested = Yes` when any trigger matches. Do not create ADR files — only recommend.
## Self-Check

- [ ] Tests run and passing? If no tests exist, gap noted?
- [ ] Review compared actual code against task context, plan, and changelog?
- [ ] Repository conventions and architecture respected?
- [ ] Full files reviewed when context needed, not just diff hunks?
- [ ] Fit and quality reviewed separately?
- [ ] Unexpected files flagged?
- [ ] Blocking vs minor issues distinguished?
- [ ] Review pass number determined from prior reviews?
- [ ] Plan.md progress updated?
- [ ] Verdict matches findings?
- [ ] ADR recommended only when appropriate?
