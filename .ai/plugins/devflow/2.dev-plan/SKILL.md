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

### Step 3: Detect Task Type

- **Feature**: new behavior, new endpoints, new UI → continue to Step 4.
- **Refactor**: restructuring, cleaning up → delegate to `1.plan`.
  Stop and tell user: "Refactor detected. Spawning 1.plan to capture specs and write plan."

### Step 4: Propose Changes

Show investigation summary to user. Include:
- What was found
- Proposed approach
- Task type detected
- Confidence level per change

### Step 5: Write Plan

After user approval, write `TASK_DIR/plan.md` using `templates/plan-template.md`:
- Fill stable sections (Task Context, Requirements, Constraints)
- Append new `## Iteration [N]` with proposed changes
- Write progress checkboxes for each change
- Append first progress table entry

### Step 6: Verify

Confirm plan.md written. Report summary to user.

## Stop Conditions

Stop and ask if:
- Task context is insufficient to plan
- Multiple valid approaches with no clear winner
- Codebase investigation reveals blocking issues
- Task appears unrelated to current repository
