---
name: dev-code
description: Read plan.md, implement the planned changes for the latest iteration, append results to changelog.md, and update plan.md progress checkboxes.
triggers:
  - "dev-code"
  - "devcode"
---

## Paths

Read shared paths from `config.md`.
---

## Workflow

Check required templates from `config.md` exist. Missing → stop.

### Step 1: Read Plan

**Manual mode:** Skip file reads. No plan.md exists — user handled implementation manually. Jump to Step 7.

Read `TASK_DIR/plan.md`. Fallback: check project root. Treat the latest `## Iteration [N]` section as the active implementation source. Missing → stop: "Error: plan.md not found."

Read all available files from `TASK_DIR/` for constraints, review findings, and prior state.

If `review.md` exists with unresolved findings relevant to the current iteration, treat them as additional execution constraints.

### Step 1.5: Detect Task Type

Check the plan's `**Type:**` field:
- `**Type:** refactor` → spawn the refflow agent.
  Tell user: "Refactor task detected. Handing off to refflow."
  Stop — refflow handles the rest.
- `**Type:** feature` or missing → continue to Step 2.

### Step 2: Read Codebase

- Read all files before editing them. Never modify unread files.
- Respect repository conventions, architecture, naming, and test patterns.
- Do not edit prior iteration sections in `plan.md`, `changelog.md`, or `review.md` except to fix obvious typos with user approval.

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

Append a new iteration to `TASK_DIR/changelog.md` using `templates/changelog-template.md`:
- `## Iteration [N] — YYYY-MM-DD HH:MM ±TZ`
- `**Trigger:**`, `**Status:**`, `**Delivery:**`, `**Plan reference:**`
- Populate relevant sections: `### Added`, `### Changed`, `### Fixed`
- Number items `[1]`, `[2]`, `[3]`; past tense, outcome-focused
- When `Delivery` is `Mixed`, note in the `### Summary` which items were manual vs. skill
- For `### Fixed`: include `Root cause` and `Resolution` based on evidence
  - If root cause cannot be proven, state best-supported explanation and label as inferred
  - If fixed without reliable reproduction, state that explicitly

### Step 7: Update Progress in Plan

Update the `## Progress` section in `TASK_DIR/plan.md`:
- Tick the checkbox for each completed change: `- [x] 1. [Change title]`
- Append a row to the progress table:
  `| [date] | [step] | Implemented — [N]/[N] tests pass |`
- Update the `Current status` field in the header to `Implemented` or `In Progress`.

## ADR Triggers

See decision triggers in `8.dev-adr/SKILL.md`. Set `ADR Suggested = Yes` when any trigger matches. Do not create ADR files — only recommend.
## Stop Conditions

Stop and ask user if:
- Requirements conflict, plan assumptions fail, or code conflicts with plan
- Verification fails and correct fix is unclear
- Change violates an invariant, architectural boundary, or business rule
- Implementation becomes significantly broader than planned
