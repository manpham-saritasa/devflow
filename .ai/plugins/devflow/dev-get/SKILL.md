---
name: dev-get
description: Pull Jira issue into .local/tasks/[KEY]/, write raw.md and task.md using external templates. Use --memory-only to fetch without writing files.
triggers:
  - "dev-get"
  - "devget"
  - "pull task"
  - "pull ticket"
  - "dev-get --memory-only"
---

## Paths

Read shared paths from `config.md`.

## Flags

- `--memory-only` — fetch Jira data, format in-memory, skip Steps 6-7 (no file writes)
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
- Pick entry where `url` matches `https://[JIRA_COMPANY_DOMAIN].atlassian.net` from `.env` or `.env.local`.
- Not found → stop: "[JIRA_COMPANY_DOMAIN] Atlassian instance not found."

### Step 3: Fetch Jira Issue

Call `getJiraIssue`:
- `cloudId`: from step 2
- `issueIdOrKey`: key
- `fields`: `["summary", "priority", "components", "description", "status", "issuetype", "issuelinks", "comment", "timetracking", "assignee", "reporter", "labels", "fixVersions", "created", "updated", "duedate", "resolution", "resolutiondate", "parent", "subtasks", "attachment"]`
- `responseContentFormat`: `"markdown"`

Fail → show real error. Stop.

Extract:
- `summary` = `fields.summary`
- `priority` = `fields.priority.name` or `None`
- `components` = `fields.components[].name` list or empty array
- `status` = `fields.status.name` or `Unknown`
- `issuetype` = `fields.issuetype.name` or `Unknown`
- `description` = `fields.description` (markdown) or `_(no description)_`
- `estimated` = `fields.timetracking.originalEstimate` or `None`
- `spent` = `fields.timetracking.timeSpent` or `None`
- `assignee` = `fields.assignee.displayName` or `Unassigned`
- `reporter` = `fields.reporter.displayName` or `Unknown`
- `labels` = `fields.labels[]` or empty array
- `fixVersions` = `fields.fixVersions[].name` list or empty array
- `created` = `fields.created` or `Unknown`
- `updated` = `fields.updated` or `Unknown`
- `dueDate` = `fields.duedate` or `None`
- `resolution` = `fields.resolution.name` or `Unresolved`
- `resolutionDate` = `fields.resolutiondate` or `None`
- `parent` = `fields.parent.key` plus summary when available, else `None`
- `subtasks` = `fields.subtasks[]` — extract key + summary; empty array if none
- `attachments` = `fields.attachment[]` — extract filename and content URL; empty array if none
- `issuelinks` = `fields.issuelinks[]` — extract related key plus summary, status, and link direction/type when available; empty array if none
- `comments` = `fields.comment.comments[]` — extract `.author.displayName`, `.created` (ISO date), `.body` (markdown); empty array if none
- `epic` = best effort from parent / issue hierarchy if exposed, else `None`
- `sprint` = sprint name if exposed in fields, else `None`


---

### Step 4: Check Existing Files

Check:
- `[TASK_DIR]/task.md`
- `[TASK_DIR]/raw.md`

One/both exist → tell human which. Ask "Overwrite [KEY] task files? (yes/no)". No → stop.

### Step 5: Ensure Folder

**--memory-only:** Skip. No folder or files to create.

Create `[TASK_DIR]/` if not exists. All paths relative to repo root.

### Step 6: Write task.md

**--memory-only:** Format task data in chat. Do not write files.

- Read template from `templates/task-template.md` next to this SKILL.
- Fill the template section by section. Do not leave placeholder text behind.
- Write to `[TASK_DIR]/task.md`.

Template mapping:
- `[Ticket ID]` → Jira key
- `[Ticket Title]` → summary
- `## Overview` → 1-3 plain-language sentences based on summary + description. Focus on user/system outcome, not implementation detail.
- `## Requirements` → 2-4 concrete bullets from description, acceptance criteria, triggers, and business rules visible in Jira.
- `## Triggers` → trigger location, trigger action, trigger data/state if Jira gives them. If no triggers are visible, use a single bullet: `- None identified`.
- `## Acceptance Criteria` → checkbox bullets from explicit Jira acceptance criteria when present. Merge direct acceptance clues from description/comments here first. If Jira has no explicit section, derive 2-3 testable checkbox bullets from the description.
- `## Constraints` → only include real or clearly implied constraints. If none are visible, keep one bullet: `- None identified`.
- `## Affected Modules` → best-effort module or area names from components, feature names, screens, or described workflow. If unclear, use higher-level bullets such as UI area, service area, or domain area.
- `## Related Historical Tasks` → related linked issues with key and short reason/title. If none, keep one bullet: `- None identified`.
- `## Open Questions` → only include meaningful questions that need answers before implementation. If only 1-2 are meaningful, omit the unused Q/A pairs.
- `## Technical Notes` → extra technical context, risk areas, inferred persistence/sync concerns, validation concerns, edge cases, and technical signals from Jira/components/comments/attachments.

Rules:
- Infer carefully, never invent facts.
- Replace instructional placeholder text like `[Requirement 1 ...]` and `[Criterion 1 ...]` with real content.
- Remove optional guidance lines that do not apply.
- If Jira does not provide enough detail for a section, use `None identified` or a short fill-manually note instead of fake specifics.

### Step 7: Write raw.md

**--memory-only:** Skip. No file writes needed.

- Read template from `templates/raw-template.md` next to this SKILL.
- Fill every placeholder the template expects.
- Write to `[TASK_DIR]/raw.md`.

Template mapping:
- `[KEY]` → Jira key
- `[TITLE]` → summary
- `[STATUS]` → status
- `[ISSUETYPE]` → issue type
- `[PRIORITY]` → priority
- `[ESTIMATED]` → original estimate or `None`
- `[SPENT]` → time spent or `None`
- `[ASSIGNEE]` → assignee display name or `Unassigned`
- `[REPORTER]` → reporter display name or `Unknown`
- `[COMPONENTS]` → components joined by `, ` or `None`
- `[LABELS]` → labels joined by `, ` or `None`
- `[FIX_VERSIONS]` → fix versions joined by `, ` or `None`
- `[CREATED]` → created timestamp
- `[UPDATED]` → updated timestamp
- `[DUE_DATE]` → due date or `None`
- `[RESOLUTION]` → resolution or `Unresolved`
- `[RESOLUTION_DATE]` → resolution date or `None`
- `[URL]` → Jira browse URL
- `[EPIC]` → epic summary/key when available, else `None`
- `[SPRINT]` → sprint name when available, else `None`
- `[PARENT]` → parent key + summary when available, else `None`

- `[SUBTASKS]` → bullet list of `KEY — Summary`, or `- None`
- `[RELATED_TASKS]` → bullet list of related linked issues with short context, or `- None`
- `[ATTACHMENTS]` → bullet list of attachment filename + URL, or `- None`
- `[DESCRIPTION]` → full Jira description verbatim markdown, or `_(no description)_`
- `[COMMENTS]` → each comment rendered as:
  ```
  **Author Name** — YYYY-MM-DD
  > comment body (verbatim markdown)
  ```
  Separate comments with blank lines. No comments → `_(no comments)_`.

Rules:
- Keep `raw.md` source-heavy. Do not summarize away useful Jira metadata.
- Do not put inferred technical signals or derived acceptance clues in `raw.md`; keep those in `task.md`.
- Fill every placeholder; do not leave tokens behind.
- Use `None`, `Unresolved`, `Unassigned`, or `- None` instead of blank sections where needed.

### Step 8: Report

Short summary after done:
- Files written: relative paths for `task.md` and `raw.md`
- Also show full absolute paths for both files so the user can copy and open them easily
- Remind: raw.md = full Jira source

---

## Self-Check

- [ ] Jira key parsed from command or user text?
- [ ] Atlassian cloudId found for the target site?
- [ ] Jira issue fetched with all fields needed by both templates?
- [ ] Existing files checked before overwriting?
- [ ] `[TASK_DIR]` folder created?
- [ ] task.md written to match the current task template sections and placeholders?
- [ ] raw.md written to match the current raw template placeholders?
- [ ] No template placeholder tokens or instructional sample text left behind?
- [ ] Relative and absolute file paths shown in the result?
- [ ] User reminded that raw.md is the full Jira source?