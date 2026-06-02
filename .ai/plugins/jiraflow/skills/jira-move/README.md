# Jira Move

Transition Jira issues through your development pipeline using milestone-based routing.

## Setup

### 1. Credentials

Add to `.env.local` in your repo root:

```
JIRA_COMPANY_DOMAIN=saritasa
JIRA_EMAIL=you@company.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PROJ
```

### 2. Discover your project's workflow

Run discover once per project. It walks through the full pipeline, records every transition, and restores the task to its original status.

```bash
jmove PROJ-123 --discover
```

If stuck at a milestone requiring manual input (e.g. estimate field), move the task manually and re-run.

## Usage

| Command | Action |
|---------|--------|
| `jmove KEY` | Auto-advance to next milestone |
| `jmove KEY ready` | Move to `ready` (e.g. Ready for Development) |
| `jmove KEY in-progress` | Move to `in-progress` (e.g. In Progress) |
| `jmove KEY code-review` | Move to code review |
| `jmove KEY verify` | Move to staging/production |
| `jmove KEY complete` | Move to completed |

Accepts milestone names OR raw Jira status names. Falls back to On Production if stuck before complete.

## Pipeline

```
Backlog → Ready → In Progress → Code Review → Ready for QA → In QA → Review → Verify → Complete
```

Milestones are defined in `milestones.config`. Each milestone maps to one or more Jira status names.

## Project config

After `--discover`, a `PROJ.config` file is created with:

- **Milestone mappings** — which Jira statuses belong to which milestone
- **Transition map** — every available transition from every visited status

## Dead ends

Transitions to Cancelled, Blocked, and Completed are not followed during discovery — only the final `complete` milestone is allowed to target them.

## Files

| File | Purpose |
|------|---------|
| `milestones.config` | Shared milestone definitions + pipeline order |
| `PROJ.config` | Per-project transition map (auto-generated) |
| `PROJECT-KEY.config.template` | Template for new project configs |
| `scripts/main.py` | Entry point |
| `scripts/discover.py` | Workflow discovery |
| `scripts/mover.py` | Issue transitions |
| `scripts/milestones.py` | Milestone resolution |
| `scripts/pipeline.py` | Pipeline order navigation |
