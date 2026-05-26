---
name: dev-plan
description: Create a structured execution plan from task evidence and codebase investigation. Saves to plan.md and progress.md.
triggers:
  - "dev-plan"
  - "devplan"
---

## Paths

Read shared paths from `config.md`. All `TASKS_ROOT`, `TASK_DIR`, `ADR_DIR`, and template variables are defined there.

---

## Workflow

### Step 0: Check Templates

Check `PLAN_TEMPLATE` and `PROGRESS_TEMPLATE` exist. Missing → stop: "Error: template not found."

### Step 1: Gather Context

Read from `TASK_DIR` when present:
- `task.md` — requirements, constraints, open questions
- `raw.md` — Jira description, comments, implementation notes
- `plan.md` — prior iterations, unresolved work, decisions
- `review.md` — prior review outcomes, unresolved findings
- `progress.md` — task timeline, next iteration number
- PR review feedback captured in `review.md` or user message — comments to address

If local files are missing, fall back to Jira MCP (requires `.env` in repo root with `JIRA_COMPANY_DOMAIN`, `JIRA_PROJECT_KEY`, `JIRA_EMAIL`, `JIRA_API_TOKEN`) or user message. Do not fail on missing files.

### Step 2: Investigate Codebase

- Read `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/`, lint/formatter configs
- Explore project structure with task context in mind
- Identify relevant files, modules, functions, integration points
- **Repo-match check:** Determine if the current repository is related to the task using concrete evidence: matching services, modules, domains, feature names, or task-specific components.
- If the repo appears unrelated, stop and ask: "This repository does not appear to contain the code for this task. Wrong repo? Continue anyway or switch? (continue/switch)"
  - `continue` → proceed but note mismatch risk in investigation summary.
  - `switch` → stop and wait for correct repo.
- Check `ADR_DIR` for matching ADRs — note constraints and decisions

### Step 3: Research Related Tasks

- Collect related task keys from `task.md` (Related Issues), Jira links, ADRs, code comments, prior plans, prior reviews
- For each related key, read `TASKS_ROOT/[RELATED_KEY]/` task files when present
- Extract patterns used, decisions made, file paths touched, constraints, review findings, and delivered behavior
- From `pr.md` when present: shipped scope, tradeoffs, regressions avoided, follow-up work

### Step 4: Summarize & Confirm

Output an investigation summary:

```
## Investigation Summary

**Key files:** [relevant files found]
**Patterns observed:** [conventions/patterns from codebase + related tasks]
**ADR constraints:** [must-respect constraints, or "none found"]
**Related task insights:** [notable decisions/approaches from related tasks]
**Prior iteration context:** [relevant prior iteration outcomes, or "none"]
**Repo match:** [yes / no (mismatch risk noted)]
**Open questions:** [unanswered questions — proposed assumptions or ask user]
**Approach:** [1-2 sentence proposed solution]
**Impact related tasks:** [current codebase + most relevant related tasks with 0-10 scores and reasons]

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

## Progress Writing Rules

- Use `PROGRESS_TEMPLATE` exactly
- Keep `progress.md` append-only
- Append one timeline block per iteration: `## Iteration [N] — YYYY-MM-DD HH:MM ±TZ`
- Record: `Trigger`, `Status`, `Summary`, `Files`, `Next Action`, `ADR Suggested`
- `ADR Suggested` must be `Yes` or `No`. If `Yes`, include short reason but do not create ADR.

## Pre-Save Checklist

- [ ] Task context gathered from available sources?
- [ ] Repo-match verified or mismatch risk noted?
- [ ] Codebase explored and key files identified?
- [ ] ADR constraints checked?
- [ ] Related tasks researched?
- [ ] Investigation summary confirmed by user?
- [ ] Template structure followed exactly?
- [ ] Changes ordered by sequence with dependencies called out?
- [ ] Plan and progress appended with correct datetime?
