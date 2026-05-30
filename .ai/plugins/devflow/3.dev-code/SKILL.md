---
name: dev-code
description: Read plan.md, implement the planned changes for the latest iteration, and append results to changelog.md and progress.md.
triggers:
  - "dev-code"
  - "devcode"
---

## Paths

Read shared paths from `config.md`. All `TASKS_ROOT`, `TASK_DIR`, and template variables are defined there.

---

## Workflow

### Step 0: Check Templates

Check `CHANGELOG_TEMPLATE` and `PROGRESS_TEMPLATE` exist. Missing → stop: "Error: template not found."

### Step 1: Read Plan

Read `TASK_DIR/plan.md`. Fallback: check project root. Treat the latest `## Iteration [N]` section as the active implementation source. Missing → stop: "Error: plan.md not found."

Also read: `task.md`, `raw.md`, `review.md`, `progress.md`, `changelog.md` (if present) for constraints, review findings, and prior state.

If `review.md` exists with unresolved findings relevant to the current iteration, treat them as additional execution constraints.

### Step 2: Read Codebase

- Read all files before editing them. Never modify unread files.
- Respect repository conventions, architecture, naming, and test patterns.
- Do not edit prior iteration sections in `plan.md`, `changelog.md`, `review.md`, or `progress.md` except to fix obvious typos with user approval.

### Step 3: Implement

Work through `## Proposed Changes` in order. For each change:
- Follow `Implementation`, `Verify`, and `Test Impact` exactly
- Verify one logical group before moving to the next
- Touch only relevant files; avoid unrelated refactors
- Report progress to user after each major item

### Step 4: Verify

Run tests for the changed code before proceeding:
```bash
# Run the smallest relevant test suite for the diff
```

- If tests fail: fix before continuing. Do not skip failing tests.
- If no tests exist for the changed area: add at least one test for new behavior, or note the gap and why.
- Run linters and builds after tests pass.
- Prefer the smallest verification that proves the requested behavior.
- Never claim verification that didn't happen.
- If verification is incomplete, state what was/wasn't run and why.

### Step 5: Capture Manual Changes

Before writing the changelog, ask the user:

> "I implemented [N] changes from the plan. Did you make any additional manual changes outside this session? If yes, describe them and I'll include them as `[manual]` items in the changelog."

- If user says no → `**Delivery:** Skill`.
- If user describes additional changes → `**Delivery:** Mixed`. Include those changes in the changelog, annotated with `[manual]`. Skill-implemented items get `[skill]`.

### Step 6: Write Changelog

Append a new iteration to `TASK_DIR/changelog.md` using `CHANGELOG_TEMPLATE`:
- `## Iteration [N] — YYYY-MM-DD HH:MM ±TZ`
- `**Trigger:**`, `**Status:**`, `**Delivery:**`, `**Plan reference:**`
- Populate relevant sections: `### Added`, `### Changed`, `### Fixed`
- Number items `[1]`, `[2]`, `[3]`; past tense, outcome-focused
- When `Delivery` is `Mixed`, note in the `### Summary` which items were manual vs. skill
- For `### Fixed`: include `Root cause` and `Resolution` based on evidence
  - If root cause cannot be proven, state best-supported explanation and label as inferred
  - If fixed without reliable reproduction, state that explicitly

### Step 7: Update Progress

Append/update timeline entry in `TASK_DIR/progress.md` using `PROGRESS_TEMPLATE`:
- `Trigger`, `Status`, `Summary`, `Files`, `Next Action`, `ADR Suggested`
- Status after coding: `Implemented`, `In Progress`, `Blocked`, or `Needs Review`
- `ADR Suggested` must be `Yes` or `No`. If `Yes`, include short reason but do not create ADR.

## ADR Triggers

Set `ADR Suggested = Yes` if any of:
- New third-party service or external API integrated
- New library/package introduces new capability or pattern
- Existing technical approach replaced
- Database schema changed
- Auth flow structure changed

## Stop Conditions

Stop and ask user if:
- Requirements conflict, plan assumptions fail, or code conflicts with plan
- Verification fails and correct fix is unclear
- Change violates an invariant, architectural boundary, or business rule
- Implementation becomes significantly broader than planned
