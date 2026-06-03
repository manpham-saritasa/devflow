---
name: dev-plan
version: 0.1.0
description: Analyze task and codebase, grill requirements until clear, produce plan.md as a handoff document for another coding agent.
triggers:
  - "dev-plan"
  - "devplan"
  - "dplan"
---

## Paths

Read shared paths from `config.md`.
---

## Workflow

### Step 1: Collect Context

Read task context from the best available source:
- `.local/tasks/{KEY}/task.md` first when present
- Jira via MCP when available
- User message as fallback

### Step 2: Investigate

- Explore the repository structure, related tasks, and relevant ADRs.
- Identify affected modules, services, and boundaries.

### Step 3: Detect Task Type

- **Feature**: new behavior, new endpoints, new UI → continue to Step 4.
- **Refactor**: restructuring, cleaning up → delegate to `1.plan`.
  Pass gathered context (affected modules, boundaries, investigation findings).
  Stop and tell user: "Refactor detected. Spawning 1.plan to capture specs and write plan."

### Step 4: Grill Requirements

Before proposing changes, grill the user. The plan will be a handoff document
for another coding agent — it must be self-contained, no tribal knowledge.

Ask questions until:
- Requirements are concrete and unambiguous
- Scope boundaries are explicit (what's in, what's out)
- All acceptance criteria are testable
- Assumptions are stated and verified
- Edge cases and error states are covered

If user is vague, push back: "What exactly should happen when...?"
If user contradicts themselves, call it out.

### Step 5: Propose Changes

Show investigation summary to user. Include:
- What was found
- Proposed approach
- Task type detected
- Confidence level per change:
  - **High** — existing pattern reused, well-understood area
  - **Medium** — new approach, similar to existing patterns
  - **Low** — uncharted territory, high uncertainty

### Step 6: Write Plan

After user approval, write `TASK_DIR/plan.md` using `templates/plan-template.md`:
- Fill stable sections (Task Context, Requirements, Constraints)
- Append new `## Iteration [N]` with proposed changes
- Write progress checkboxes for each change
- Append first progress table entry

### Step 7: Final Check

**Pass 1 — Handoff scan:**
- [ ] Template filled?
- [ ] Another agent could implement without asking questions?
- [ ] No tribal knowledge or implicit assumptions?

Fix gaps before continuing. Re-scan until clean.

**Pass 2 — Plan quality:**
1. **Requirements** — Are the task requirements clear and complete? If vague, ask user before proceeding.
2. **Invariants** — What must not break? Are they explicit?
3. **Risks** — Does each change have a rollback path?
4. **Validation** — Is every verify step concrete? (specific command, not "run tests")
5. **Step size** — Each change reversible? Single concern?
6. **Test gaps** — Are missing tests acknowledged?

Fix any gaps inline.

### Step 8: Verify

Confirm plan.md written. If write failed: report error and stop.
Report summary to user.

## Stop Conditions

Stop and ask if:
- Task context is insufficient to plan
- Multiple valid approaches with no clear winner
- Codebase investigation reveals blocking issues
- Task appears unrelated to current repository
