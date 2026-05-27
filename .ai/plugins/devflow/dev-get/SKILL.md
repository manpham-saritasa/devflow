---
name: dev-get
description: Pull Jira issue into .local/tasks/[KEY]/, write raw.md and task.md using external templates.
triggers:
  - "dev-get"
  - "devget"
  - "pull task"
  - "pull ticket"  
---

## Paths

Read shared paths from `config.md`. All `TASKS_ROOT` and `TASK_DIR` variables are defined there.

---

## When to Use

Trigger on:
- `dev-get ABC-123` ← primary command
- Jira URL from `https://saritasa.atlassian.net/...` + request to import

## Workflow

### Step 1: Parse Jira Key

- Word after `dev-get` or `devget` = key.
- Else find first match of `[A-Z][A-Z0-9_]+-\d+` in user text.
- Not found → ask "Give Jira key like ABC-123." Stop.

### Step 2: Get Cloud ID

- Call Atlassian resource list.
- Pick entry where `url == "https://saritasa.atlassian.net"`. Use its `id`.
- Not found → tell human "Saritasa Atlassian not connected." Stop.

### Step 3: Fetch Jira Issue

Call `getJiraIssue`:
- `cloudId`: from step 2
- `issueIdOrKey`: key
- `fields`: `["summary", "priority", "components", "description", "status", "issuetype", "issuelinks", "comment"]`
- `responseContentFormat`: `"markdown"`

Fail → show real error. Stop.

Extract:
- `summary` = `fields.summary`
- `priority` = `fields.priority.name` or null
- `components` = `fields.components[].name` list
- `status` = `fields.status.name` or null
- `issuetype` = `fields.issuetype.name` or null
- `description` = `fields.description` (markdown) or null
- `issuelinks` = `fields.issuelinks[]` — extract `.outwardIssue.key` and `.inwardIssue.key` from each entry (skip nulls)
- `comments` = `fields.comment.comments[]` — extract `.author.displayName`, `.created` (ISO date), `.body` (markdown) from each entry; empty array if none

---

### Step 4: Check Existing Files

Check:
- `[TASK_DIR]/task.md`
- `[TASK_DIR]/raw.md`

One/both exist → tell human which. Ask "Overwrite [KEY] task files? (yes/no)". No → stop.

### Step 5: Ensure Folder

Create `[TASK_DIR]/` if not exists. All paths relative to repo root.

### Step 6: Write task.md

- Read template from `templates/task-template.md` next to this SKILL.
- Replace placeholders. Write to `[TASK_DIR]/task.md`.

Placeholders:
- `[TASK_KEY]` — Jira key
- `[TASK_TITLE]` — summary
- `[PRIORITY]` — priority or `None`
- `[COMPONENT]` — components joined by `, ` or `None`
- `[RELATED_ISSUES]` — render as:
  ```
  ## Related Issues

  - KEY — summary _(link type, status)_
  - KEY — summary _(link type, status)_
  ```
  Omit entire section (including heading) if no related tasks.

Free-text sections — infer from Jira description:

**Objective** — one sentence. Outcome for user/system, not implementation detail.

**Constraints** — 2-3 bullets. Pull from: related tickets, tech stack signals, business/deployment rules. Gap → `[Constraint - not clear from ticket, fill manually]`.

**Acceptance Criteria** — use "Acceptance criteria" section in description if exists. Else derive 2-3 testable outcomes from problem. Each needs ≥1 happy-path + ≥1 edge/error test case.

**Open Questions** — 2-3 questions on scope, edge cases, related tickets, unknowns. Leave answers blank.

Rule: infer, never invent. Truly no info → `[Not enough info in ticket - fill manually]`.

### Step 7: Write raw.md

- Read template from `templates/raw-template.md` next to this SKILL.
- Replace placeholders. Write to `[TASK_DIR]/raw.md`.

Placeholders:
- `[KEY]` — Jira key
- `[TITLE]` — summary
- `[STATUS]` — status or `Unknown`
- `[ISSUETYPE]` — issuetype or `Unknown`
- `[PRIORITY]` — priority or `None`
- `[COMPONENTS]` — components joined by `, ` or `None`
- `[RELATED_ISSUES]` — same format as task.md: render as `## Related Issues` section with one bullet per linked issue. Omit entire section if no related tasks.
- `[DESCRIPTION]` — full Jira description verbatim markdown, or `_(no description)_`
- `[COMMENTS]` — each comment rendered as:
  ```
  **Author Name** — YYYY-MM-DD
  > comment body (verbatim markdown)
  ```
  Multiple comments separated by blank line. No comments → `_(no comments)_`.

Never summarize description or comments. Dump verbatim.

### Step 8: Report

Short summary after done:
- Files written: task.md + raw.md paths
- Remind: raw.md = full Jira source

---

## Self-Check

- [ ] Jira key parsed from command or user text?
- [ ] Atlassian cloudId found for the target site?
- [ ] Jira issue fetched with all required fields?
- [ ] Existing files checked before overwriting?
- [ ] `[TASK_DIR]` folder created?
- [ ] task.md written with all placeholders replaced?
- [ ] raw.md written with verbatim description and comments?
- [ ] User reminded that raw.md is the full Jira source?