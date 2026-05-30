# Standard Operating Procedure — Development Workflow

This SOP defines how our team takes a Jira task from backlog to production. It covers branching, coding, review, shipping, and the tools that automate each step.

---

## 1. Task Lifecycle Overview

Every task follows this pipeline:

```
Backlog → Ready → In Progress → Code Review → Ready for QA → In QA → Review → Verify → Complete
```

| Stage | What happens | Owner |
|-------|-------------|-------|
| Backlog | Task created, not yet prioritized | PM |
| Ready | Task assigned, ready to start | Developer |
| In Progress | Branch created, coding started | Developer |
| Code Review | PR opened, reviewer assigned | Reviewer |
| Ready for QA | PR merged, ready for testing | Developer |
| In QA | Tester is verifying | Tester |
| Review | Stakeholder or tech lead review | Lead |
| Verify | Deployed to staging or production | Developer |
| Complete | Task closed | PM |

---

## 2. Starting a Task

### 2.1 Pull the task from Jira

Run `dev-get PROJ-123` to fetch the Jira issue into your local task folder. This creates:

- `.local/tasks/PROJ-123/task.md` — structured task summary
- `.local/tasks/PROJ-123/raw.md` — full Jira source (description, comments, metadata)

### 2.2 Create a branch

Run `dev-start PROJ-123` to create a gitflow branch:

| Command | What it does |
|---------|-------------|
| `dev-start PROJ-123` | Feature branch from `develop` |
| `dev-start PROJ-123 --hotfix` | Hotfix branch from `main` |
| `dev-start PROJ-123 --release` | Release branch from `develop` |
| `dev-start PROJ-123 --worktree` | Isolated worktree (recommended for parallel tasks) |

The branch name follows this format:

```
feature/proj-123-short-summary
hotfix/proj-456-fix-crash
release/proj-789-version-1-2-0
```

The task's Jira status is automatically moved to **In Progress**.

---

## 3. Planning and Implementation

### 3.1 Plan before you code

Run `/devflow PROJ-123` to enter the full pipeline. The orchestrator will:

1. Detect your current progress
2. Suggest the next step
3. Run each phase with checkpoints

Individual phases:

| Phase | Command | Output |
|-------|---------|--------|
| Plan | `/dev-plan PROJ-123` | `plan.md` — structured execution plan |
| Code | `/dev-code` | `changelog.md` — what was implemented |
| Review | `/dev-review` | `review.md` — self-review findings |

The orchestrator runs plan → code → review in sequence, stopping at each checkpoint for your approval.

### 3.2 Commit in logical groups

Run `/dev-commit` to stage and commit changes. The skill:

- Groups related files together
- Orders commits chronologically
- Appends the task key to every commit message
- Keeps commits small and reviewable

Commit message format: `{action} {description} PROJ-123`

Examples:
- `Add login form validation PROJ-123`
- `Fix null reference in PDF export PROJ-123`
- `Update API error handling PROJ-123`

### 3.3 Self-review before shipping

Run `/dev-review` before opening a PR. The review checks:

- **Fit** — does the code match the plan and acceptance criteria?
- **Quality** — correctness, readability, test coverage, error handling
- **Changelog gaps** — are there unlogged manual changes?

Findings are categorized as `[blocking]` or `[minor]`. Blocking issues must be fixed before shipping.

---

## 4. Shipping the PR

Run `/dev-ship` to create a PR and notify Jira:

| Flag | Behavior |
|------|----------|
| (none) | Create PR + comment Jira |
| `--pr-only` | Create PR only, skip Jira |
| `--jira-only` | Comment Jira only, skip PR |
| `--no-jira` | Create PR only, no Jira integration |
| `--dry-run` | Preview reports without creating anything |

The skill generates two reports:

1. **Technical PR body** — architecture, decisions, file paths, code patterns. For future engineers.
2. **Non-technical Jira comment** — behavior changes, user impact only. For testers and PMs.

After shipping, the task moves to **Code Review**.

---

## 5. Fixing PR Comments

Run `/dev-fix-pr` when a reviewer requests changes. The skill:

1. Lists all unresolved review threads
2. Plans fixes for each comment
3. Applies approved changes in logical commits
4. Pushes and resolves threads via GraphQL

The skill supports multiple rounds — it loops until all comments are resolved or you choose to stop.

Commit format: `Fix PR comments PROJ-123`

---

## 6. Finishing a Task

Run `/dev-finish` when the PR is approved. The skill:

1. Verifies the PR is approved (stops if changes are still requested)
2. Merges the PR using the configured merge strategy (default: `--merge`, preserves history)
3. Deletes the local branch or worktree
4. Cleans up remote branch

The task folder (`.local/tasks/PROJ-123/`) is preserved — it contains your plan, changelog, and review history as a snapshot of completed work.

The task moves to **Ready for QA**.

---

## 7. Architecture Decisions

Run `/dev-adr PROJ-123` when the task introduced:

- A new third-party service or external API
- A new library or package that introduces a new capability
- A replacement of an existing technical approach
- A database schema change
- An auth or permission boundary change

The skill reads your task evidence and generates an ADR in `docs/adrs/`. It skips non-architectural tasks automatically.

---

## 8. Daily Workflow

### 8.1 See what's assigned to you

Run `jtask` to list your Jira tasks grouped by status:

| Flag | What it shows |
|------|--------------|
| (none) | All assigned tasks |
| `--pending` | Currently in progress |
| `--ready` | Ready to start |
| `--review` | Under review |

### 8.2 Check what the team needs from you

Run `jurgent` to find tasks where someone is waiting on your response. The skill:

- Scans Jira comments for unanswered mentions and questions
- Skips comments you already replied to
- Orders results by priority and urgency

### 8.3 Move tasks through the pipeline

Run `jmove PROJ-123` to transition a task to its next milestone. The skill uses per-project transition maps and shared milestone definitions.

### 8.4 Log your time

Run `jlog` to log work hours to Jira via Tempo. Supports flexible duration formats (`1h`, `30m`, `1h30m`), past dates (`--date`), and job types (`--job`). Shows a daily summary after logging.

---

## 9. Branch and Worktree Conventions

| Mode | How it works | When to use |
|------|-------------|------------|
| Gitflow | Branch in the main clone | Single task, simple workflow |
| Worktree | Isolated sibling folder | Multiple parallel tasks, clean separation |

Worktree structure:

```
project-api/                          ← main clone
project-api-worktrees/                ← all worktrees here
├── proj-111-short-name/              ← worktree 1
├── proj-222-short-name/              ← worktree 2
```

Worktrees are fully independent — each has its own `.env` file and working directory. The main clone stays clean on `main` or `develop`.

---

## 10. Quick Reference

| Action | Command |
|--------|---------|
| Start task | `dev-start PROJ-123` |
| Fetch task | `dev-get PROJ-123` |
| Full pipeline | `/devflow PROJ-123` |
| Plan only | `/dev-plan PROJ-123` |
| Commit changes | `/dev-commit` |
| Self-review | `/dev-review` |
| Ship PR | `/dev-ship` |
| Fix PR comments | `/dev-fix-pr` |
| Finish task | `/dev-finish` |
| Create ADR | `/dev-adr PROJ-123` |
| List my tasks | `jtask` |
| Check urgent items | `jurgent` |
| Move Jira status | `jmove PROJ-123` |
| Log time | `jlog` |

---

## 11. Do Not

- Push directly to `main` or `develop`
- Merge your own PR without review
- Skip the plan before coding complex tasks
- Commit unrelated changes together
- Leave a worktree without finishing or deleting it
- Skip the changelog — it is the single source of truth for what was delivered
