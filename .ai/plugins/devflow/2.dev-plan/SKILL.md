---
name: dev-plan
description: Analyze task and codebase, produce plan.md with proposed changes, verification steps, and progress checkboxes. Detects refactor vs feature tasks.
triggers:
  - "dev-plan"
  - "devplan"
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
- For refactor tasks: capture original specs (API contracts, business rules, side effects, test counts).

### Step 3: Detect Task Type

- **Feature**: new behavior, new endpoints, new UI.
- **Refactor**: restructuring, cleaning up, improving without new features.

For refactor tasks, tag the plan with `**Type:** refactor` and structure steps with concern tags:
- `[structure]` — boundaries, ownership, layout
- `[simplify]` — readability, naming, complexity
- `[api]` — contract redesign, migration

### Step 4: Propose Changes

Show investigation summary to user. Include:
- What was found
- Proposed approach
- Task type detected
- Confidence level per change

### Step 5: Write Plan

After user approval, write `TASK_DIR/plan.md` using `PLAN_TEMPLATE`:

**For feature tasks:**
- Fill stable sections (Task Context, Requirements, Constraints)
- Append new `## Iteration [N]` with proposed changes
- Write progress checkboxes for each change
- Append first progress table entry

**For refactor tasks:**
- Fill stable sections
- Write `**Type:** refactor`
- Write `## Original specs` — capture APIs, business rules, side effects, test counts
- Write `## Phased plan` with step tags:
  - `[structure]` — boundaries, ownership, layout
  - `[simplify]` — readability, naming, complexity
  - `[api]` — contract redesign, migration
- Write progress checkboxes matching each step
- Append first progress table entry

### Step 6: Verify

Confirm plan.md written. Report summary to user.

## Stop Conditions

Stop and ask if:
- Task context is insufficient to plan
- Multiple valid approaches with no clear winner
- Codebase investigation reveals blocking issues
- Task appears unrelated to current repository
