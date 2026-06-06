# jira-day

Find Jira tasks you touched today, ranked by your role. Log time with one click.

## 1. Quick start

```bash
jday                    # tasks you touched today (auto-detects favorites)
jday RMASUP             # specific project
jday --window 48h       # last 48 hours
jday --role dev         # dev ranking: PRs first
jday --no-pr            # skip PR checks this run
```

First run asks: your role, PR activity, and favorite projects. Saves to `.local/jiraflow/config.yaml`.

## 2. Setup

### Required env vars (`.env.jira`)

```env
JIRA_COMPANY_DOMAIN=saritasa
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=your_token
JIRA_PROJECT_KEY=PROJ
```

### Favorite projects (shared with jmine/jurgent)

```yaml
# .local/jiraflow/config.yaml
favorite_projects: [RMASUP, COAPS]

# Maps Jira project → GitHub repos for PR detection
project_repos:
  RMASUP:
    - owner/backend
    - owner/frontend
  COAPS: owner/api
```

Without `project_repos`, PR check is skipped. One project can have multiple repos — all are searched.

### Personal config

```yaml
# .local/jday/config.yaml
role: dev          # dev | qa | tm | pm | mixed
check_pr_activity: true
```

## 3. What it checks

Collects evidence from the last 24 hours (or today by default):

| Source | Signal |
|---|---|
| Jira comments | you commented on this issue |
| Jira transitions | you moved this issue to another status |
| Jira updates | you updated description, summary, assignee, etc. |
| Git commits | commit message or branch name includes the task key |
| GitHub PRs | you authored, reviewed, or commented on a PR (needs `project_repos`) |
| Worklogs | you already logged time today (shown as `10m today`) |

## 4. Role ranking

Tasks are sorted differently depending on your role.

### dev

1. PR activity
2. Git activity
3. Jira transition or comment
4. Updated-only
5. Already logged → ranked lower

### qa

1. QA-stage task with transition or comment
2. Any transition or comment
3. Updated-only
4. Already logged → ranked lower

### tm

1. Review-stage transition
2. Coordination or review comment
3. Other transition
4. Updated-only
5. Already logged → ranked lower

### pm

1. Review-stage transition
2. Clarification or planning comment
3. Other transition or update
4. Updated-only
5. Already logged → ranked lower

### mixed

1. 2+ strong signals (pr, git, transition, comment)
2. 1 strong signal
3. Updated-only
4. Already logged → ranked lower

Tie-breaks: not logged wins over logged, then most recent activity, then more evidence.

## 5. Output example

```text
jira-day — last 16h

Suggested: #1

1. PROJ-100
   url: https://<domain>.atlassian.net/browse/PROJ-100
   evidence: [comment, transition, updated]
   logged: 10m today
   summary: Fix login redirect after token expiry
   status: In Progress | priority: High | assignee: Jane Smith
   notes: Replicated on staging, working on fix.

2. PROJ-101
   url: https://<domain>.atlassian.net/browse/PROJ-101
   evidence: [transition, updated]
   logged: not logged
   summary: Add pagination to search results
```

Then:

```text
Log to #1? (yes / choose # / cancel)
```

## 6. Flags

| Flag | Effect |
|---|---|
| `--json` | Output as JSON for scripts |
| `--config` | Show resolved config |
| `--role qa` | Override role for this run |
| `--window 48h` | Custom time window (default: today) |
| `--no-pr` | Skip PR checks this run |
| `--reset-role` | Re-run first-time setup |

## 7. File structure

```text
skills/jira-day/
  SKILL.md
  config.template.yaml
  scripts/
    main.py          ← entry point, arg parsing
    common.py        ← constants, date utils, text extraction
    auth.py          ← env loading, Jira auth, identity
    settings.py      ← config bootstrap, stage groups
    jira_client.py   ← Jira HTTP
    candidate.py     ← task model + bucket logic
    collectors.py    ← evidence gathering (git, PR, Jira)
    output.py        ← ranking + text output
    context.py       ← Runtime/Evidence context objects
    worklogs.py      ← local worklog parsing
    tests/           ← unit tests
```

## 8. How it integrates

- Reads Jira auth from `../../config.md`
- Hands off to `jira-log` for time entry
- Works with `jira-mine` and `jira-urgent` — same favorite projects config
