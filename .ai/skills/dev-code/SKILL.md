---
name: dev-code
description: Read plan.md, implement the planned changes for the latest iteration, and append results to changelog.md and progress.md.
---

## Paths

- TASKS_ROOT: `.local/tasks`
- TASK_DIR: `[TASKS_ROOT]/[KEY]`
- CHANGELOG_TEMPLATE: `.ai/agents/templates/changelog-template.md`
- PROGRESS_TEMPLATE: `.ai/agents/templates/progress-template.md`

---

## Workflow

### Step 0: Check Templates

Check `CHANGELOG_TEMPLATE` and `PROGRESS_TEMPLATE` exist. Missing → stop: "Error: template not found."

### Step 1: Read Plan

Read `TASK_DIR/plan.md`. Fallback: check project root. Treat the latest `## Iteration [N]` section as the active implementation source. Missing → stop: "Error: plan.md not found."

Also read: `task.md`, `raw.md`, `review.md`, `progress.md`, `changelog.md` (if present) for constraints, review findings, and prior state.

### Step 2: Read Codebase

- Read all files before editing them. Never modify unread files.
- Respect repository conventions, architecture, naming, and test patterns.

### Step 3: Implement

Work through `## Proposed Changes` in order. For each change:
- Follow `Implementation`, `Verify`, and `Test Impact` exactly
- Verify one logical group before moving to the next
- Touch only relevant files; avoid unrelated refactors
- Report progress to user after each major item

### Step 4: Verify

- Run relevant tests, builds, linters
- Prefer the smallest verification that proves the requested behavior
- Never claim verification that didn't happen
- If verification is incomplete, state what was/wasn't run and why

### Step 5: Write Changelog

Append a new iteration to `TASK_DIR/changelog.md` using `CHANGELOG_TEMPLATE`:
- `## Iteration [N] — YYYY-MM-DD HH:MM ±TZ`
- `**Trigger:**`, `**Status:**`, `**Plan reference:**`
- Populate relevant sections: `### Added`, `### Changed`, `### Fixed`
- Number items `[1]`, `[2]`, `[3]`; past tense, outcome-focused
- For `### Fixed`: include `Root cause` and `Resolution` based on evidence
  - If root cause cannot be proven, state best-supported explanation and label as inferred
  - If fixed without reliable reproduction, state that explicitly

### Step 6: Update Progress

Append/update timeline entry in `TASK_DIR/progress.md` using `PROGRESS_TEMPLATE`:
- `Trigger`, `Status`, `Summary`, `Files`, `Next Action`, `ADR Suggested`
- Status after coding: `Implemented`, `In Progress`, `Blocked`, or `Needs Review`

## Stop Conditions

Stop and ask user if:
- Requirements conflict, plan assumptions fail, or code conflicts with plan
- Verification fails and correct fix is unclear
- Change violates an invariant, architectural boundary, or business rule
- Implementation becomes significantly broader than planned
