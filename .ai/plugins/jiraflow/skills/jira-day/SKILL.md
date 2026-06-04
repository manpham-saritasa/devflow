---
name: jira-day
description: Find Jira tasks you touched in the last 24 hours, suggest the best candidate, and optionally log time through jlog.
triggers:
  - "jday"
  - "jira-day"
  - "what did i work on today"
  - "find tasks i touched today"
---

## Goal

Find Jira tasks you touched in the last 24 hours, rank them by role-aware rules, suggest the best candidate, and optionally log time.

## Shared config

Read Jira auth from `../../config.md`.

Read optional local override from the repo root:

- `.local/jday/config.yaml`

If missing on first run:
1. Ask for role: `dev`, `qa`, `tm`, `pm`, `mixed`
2. Ask: "Do you do PR activity as part of your work?"
3. Ask: "List your favorite projects (comma-separated keys, e.g. PROJ, COAPS)?"
4. Auto-detect identity
5. Create `.local/jday/config.yaml`

If `favorite_projects` is set and no project key is given, `jday` loops through all favorites and merges results.

Use `config.template.yaml` in this skill as the file template.

## Run

```bash
python .ai/plugins/jiraflow/skills/jira-day/scripts/main.py [PROJECT_KEY]
```

Useful flags:

```bash
python .ai/plugins/jiraflow/skills/jira-day/scripts/main.py PROJ --json
python .ai/plugins/jiraflow/skills/jira-day/scripts/main.py PROJ --role qa
python .ai/plugins/jiraflow/skills/jira-day/scripts/main.py PROJ --window 48h
python .ai/plugins/jiraflow/skills/jira-day/scripts/main.py PROJ --no-pr
python .ai/plugins/jiraflow/skills/jira-day/scripts/main.py --config
python .ai/plugins/jiraflow/skills/jira-day/scripts/main.py --reset-role
```

## Evidence sources

Collect candidate Jira tasks from the last 24 hours using:

1. Jira comments by current user
2. Jira transitions by current user
3. Jira updated-by activity (non-status changelog by current user)
4. Git commits / branches / commit messages with task key
5. GitHub PR activity by current user (only if `check_pr_activity: true`)
6. Existing worklogs in last 24 hours

## Role-aware ranking

### dev
1. PR activity
2. Git activity
3. Jira transition/comment
4. Updated-only
5. Already-logged lower

### qa
1. QA-stage transition/comment
2. Verification/test activity
3. Updated-only
4. PR low or skipped
5. Already-logged lower

### tm
1. Review-stage transition
2. Coordination/review comments
3. Other transitions
4. Updated-only
5. PR low or skipped

### pm
1. Review-stage transition
2. Clarification/planning comments
3. Other transitions/updates
4. Updated-only
5. PR very low or skipped

### mixed
1. 2+ evidence sources
2. 1 strong source (`pr`, `git`, `transition`, `comment`)
3. Updated-only
4. Already-logged lower

Tie-breaks:
1. not logged before logged
2. most recent activity first
3. more evidence badges first

## Output format

If `--json` is used, the script returns structured data. Format it in chat like this:

```text
jira-day — last 24h

Suggested: #1

1. PROJ-100
   url: https://<domain>.atlassian.net/browse/PROJ-100
   evidence: [comment, transition, updated]
   logged: not logged
   summary: Fix login redirect after token expiry
   status: In Progress | priority: High | assignee: Jane Smith
   notes: Replicated on staging, working on fix.

2. PROJ-101
   url: https://<domain>.atlassian.net/browse/PROJ-101
   evidence: [comment, updated]
   logged: not logged
   summary: Add pagination to search results
   status: Ready for Development | priority: High | assignee: Jane Smith
   notes: Created API task for this.
```

Then ask:

- `Log to #1? (yes / choose # / cancel)`

If yes or alternate chosen:
1. Ask duration
2. Ask description
3. Run:
   ```bash
   python .ai/plugins/jiraflow/skills/jira-log/main.py <KEY> <DURATION> "<DESCRIPTION>"
   ```
4. Show final total from `jlog`

## Rules

- Always use rolling last 24h by default
- Always dedupe by Jira key
- Keep already-logged tasks visible, but rank lower
- Skip PR checks if user config disables them
- Use shared stage groups from `../../config.md`
- Never log time without confirmation
- If no candidates found, say so clearly and stop
