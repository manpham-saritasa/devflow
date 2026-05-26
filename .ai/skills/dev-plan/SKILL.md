---
name: dev-plan
description: Create a structured execution plan from task evidence and codebase investigation. Saves to plan.md and progress.md.
---

## Paths

- TASKS_ROOT: `.local/tasks`
- TASK_DIR: `[TASKS_ROOT]/[KEY]`
- ADR_DIR: `.local/adr`
- PLAN_TEMPLATE: `.ai/agents/templates/plan-template.md`
- PROGRESS_TEMPLATE: `.ai/agents/templates/progress-template.md`

---

## Workflow

### Step 1: Gather Context

Read from `TASK_DIR` when present:
- `task.md` — requirements, constraints, open questions
- `raw.md` — Jira description, comments, implementation notes
- `plan.md` — prior iterations, unresolved work, decisions
- `review.md` — prior review outcomes, unresolved findings
- `progress.md` — task timeline, next iteration number
- `pr-feedback-[N].md` — PR review feedback to address

If local files are missing, fall back to Jira MCP or user message. Do not fail on missing files.

### Step 2: Investigate Codebase

- Read `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/`, lint/formatter configs
- Explore project structure with task context in mind
- Identify relevant files, modules, functions, integration points
- Check `ADR_DIR` for matching ADRs — note constraints and decisions

### Step 3: Research Related Tasks

- Collect related task keys from local files, Jira links, ADRs, code comments
- Read related task folders for patterns, approaches, review findings
- Extract reusable structure, rejected alternatives, lessons learned

### Step 4: Summarize & Confirm

Output an investigation summary:

```
## Investigation Summary

**Key files:** ...
**Patterns observed:** ...
**ADR constraints:** ...
**Approach:** [1-2 sentence proposal]

Proceed? (yes/no/adjust)
```

Do not write plan.md until user confirms.

### Step 5: Create Plan

- Determine next iteration number from progress.md or plan.md (default: 1)
- Capture datetime: `YYYY-MM-DD HH:MM ±TZ`
- Break solution into ordered `## Proposed Changes`
- Use `PLAN_TEMPLATE` structure exactly
- For each change: `User outcome`, `Why`, `Affected area`, `Confidence`, `Implementation`, `Test Impact`
- End each `Implementation` with a concrete `Verify` step
- Populate `Constraints`, `Risks`, `Open Questions`, `Done Criteria`

### Step 6: Write Files

- Append new iteration to `TASK_DIR/plan.md`
- Append timeline entry to `TASK_DIR/progress.md`
- Create files if they don't exist

## Plan Writing Rules

- Start with: `## Iteration [N] — YYYY-MM-DD HH:MM ±TZ`
- Include `**Trigger:** [new request | review follow-up | bug fix | scope update]`
- Order changes by implementation sequence; call out dependencies and parallelism
- Use exact file paths from codebase investigation — never invent
- Keep concise and executable by another coding agent
