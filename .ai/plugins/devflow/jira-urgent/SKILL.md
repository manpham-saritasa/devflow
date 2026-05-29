---
name: jira-urgent
description: List Jira tasks where the team is waiting on you. Finds issues with unanswered mentions or questions, drafts replies. Supports --full mode for all open tasks.
triggers:
  - "jira-urgent"
  - "jurgent"
  - "my Jira tasks"
  - "what does my team need from me"
  - "urgent Jira items"
---

## Paths

- `CONFIG` — `./projects.config` (skill-relative, key=value format)
- `OUTPUT_DIR` — `.local/jira/`
- `OUTPUT_FILE` — `urgent-{YYYY-MM-DD}.md`
- `IGNORE_FILE` — `.local/jira/ignored-comments.txt` — one comment ID per line
- `TIMEZONE` — `Asia/Bangkok`
- `DRAFT_MODE` — `student` (student = friendly team-facing; caveman = minimal)

---

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Urgent mode on default project |
| `--full` | Full mode: all open tasks, no drafts |
| `--choose` | Prompt to pick a project |
| `--refresh` | Re-discover projects, update config, then run |
| `<KEY>` | Override project key (e.g., `PROJ`) |

---

## Detection Logic

### Urgent Item Rules

Walk comments newest → oldest. Find first comment matching:

| Rule | Condition |
|------|-----------|
| **A** | Author ≠ you AND mentions you via @-mention |
| **B** | Author ≠ you AND contains `?` |

If matched AND no later comment by you → classify intent. Otherwise drop.

### Intent Classification

**Pass 1 — keyword filter:**
- `verify` if: "is fixed", "was fixed", "resolved", "not reproducible", "please verify", "please check", "ready for review", "ready for qa", "ready for testing"
- `needs_answer` if (overrides verify): "which", "should we", "do we", "can you", "could you", "what about", "any solution", "any update"

**Pass 2 — LLM judgment (if ambiguous):**
- `verify` — teammate reporting completed work, asking for confirmation/review
- `needs_answer` — teammate asking question, requesting decision, blocked waiting on info
- Default: `needs_answer` (safer to surface)

### Tag Mapping

| Rule | Intent | Tag |
|------|--------|-----|
| A (mention) | needs_answer | `at_mention` |
| A (mention) | verify | `at_mention_verify` |
| B (question) | needs_answer | `question` |
| B (question) | verify | `verify` |

### Sort Order (urgent mode)

Group by workflow stage first, then priority within each group:

1. **Blocked** — Blocked, On Hold
2. **Active** — Ready for Development, In Progress, Code Review
3. **Review** — TM Review, In Review

Within each group: `at_mention` first, `question` next, `verify` last.
Within tag: priority Highest → High → Medium → Low → Lowest.
Within priority: comment datetime descending.

### Status Bucketing (full mode)

| Statuses | Bucket |
|----------|--------|
| TM Review, In Review, Code Review | Top priority |
| In Progress | In Progress |
| Ready for Development, Open, To Do | Ready for Development |
| Everything else | Other |

### Drop Conditions (both modes)

Status in: Completed, Done, Closed, Resolved, On Production, On Staging.

---

## Steps

### Step 1: Parse Input

Extract: mode (`urgent` | `full`), project key (optional), flags (`--choose`, `--refresh`).

### Step 2: Load Credentials

Read `.env.local` (preferred) or `.env` from repo root. Extract:
- `JIRA_COMPANY_DOMAIN` — the Atlassian subdomain (e.g., `saritasa`)
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`

Do not use `source` — read the file and parse `KEY=VALUE` lines directly.

### Step 3: Get User Account ID

```bash
curl -s -u "${JIRA_EMAIL}:${JIRA_API_TOKEN}" \
  -H "Accept: application/json" \
  "https://${JIRA_COMPANY_DOMAIN}.atlassian.net/rest/api/3/myself"
```

Parse `accountId` from the JSON response.

### Step 4: Resolve Project Key

| Case | Action |
|------|--------|
| Explicit `<KEY>` in command | Use it |
| `--refresh` | Discover projects → pick new default → update config → use |
| `--choose` | Pick from saved projects → use for this run |
| No flag, no key | Use `default_project_key` from config |

**Discover projects** — call the search API, extract unique project keys and names, save to `CONFIG` in key=value format. Use the POST endpoint:

```bash
curl -s -u "${JIRA_EMAIL}:${JIRA_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jql":"sprint in openSprints() AND (assignee=currentUser() OR reporter=currentUser())","maxResults":100,"fields":["project"]}' \
  "https://${JIRA_COMPANY_DOMAIN}.atlassian.net/rest/api/3/search/jql"
```

### Step 5: Query Jira

Use the JQL search POST endpoint: `POST /rest/api/3/search/jql` with JSON body.

**Urgent mode — two queries:**

Query A (assigned to you):
```bash
curl -s -u "${JIRA_EMAIL}:${JIRA_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jql":"project=<KEY> AND sprint in openSprints() AND assignee=currentUser() AND status not in (Completed,Done,Closed,Resolved,\"On Production\",\"On Staging\") ORDER BY priority DESC, updated DESC","maxResults":50,"fields":["summary","status","priority","issuetype","comment","assignee","updated"]}' \
  "https://${JIRA_COMPANY_DOMAIN}.atlassian.net/rest/api/3/search/jql"
```

Query B (reporter, not assignee): same but `assignee!=currentUser() AND reporter=currentUser()`.

**Full mode:** Query A only. Fields: `summary, status, priority, issuetype, updated`. maxResults: 100.

### Step 6: Filter & Classify (urgent mode only)

For each issue, apply urgent rules from Detection Logic. Record per item:
- `key`, `summary`, `status`, `priority`, `assignee`
- `anchor_comment_id`, `anchor_author`, `anchor_datetime` (in configured timezone)
- `anchor_preview` (first ~200 chars)
- `tag`

**Drop ignored comments:** read `IGNORE_FILE` (one comment ID per line). If `anchor_comment_id` is in the list, drop the item — user has already reviewed and chosen not to reply.

Build deep links using comment IDs: `https://${JIRA_COMPANY_DOMAIN}.atlassian.net/browse/<KEY>?focusedCommentId=<anchor_comment_id>`

### Step 7: Draft Reply (urgent mode only)

| Tag | Template |
|-----|----------|
| `verify`, `at_mention_verify` | "Thanks `<author>`. I'll verify on `<env>` today and confirm here." |
| `at_mention`, `question` | Substantive reply addressing the question. 2-6 sentences. |

Rules:
- Address teammate by `anchor_author`
- Insufficient context → `**I'm not sure yet.**` + how to find out
- Never invent decisions
- Tag confidence: `High`, `Medium`, `Low`

### Step 8: Output

Save to `.local/jira/urgent-{YYYY-MM-DD}.md`. Print full body to chat.

**Urgent mode format:**

Each item links directly to the urgent comment. Use deep link format:
`https://${JIRA_COMPANY_DOMAIN}.atlassian.net/browse/<KEY>?focusedCommentId=<comment_id>`

```markdown
# Jira — Urgent Tasks: <KEY> ({YYYY-MM-DD})

## 🔴 Needs your answer ({count})

### 1. [<KEY-N>](<deep_link_with_comment_id>) — <summary>
- **Status:** <status> | **Priority:** <priority> | **Assignee:** <assignee>
- **<anchor_author> asked on <anchor_datetime>** (<tag>):
  > <anchor_preview>

**Draft reply (confidence: <High|Medium|Low>):**

> <draft text>

---

## 🟡 Verify when convenient ({count})

### N. [<KEY-N>](<deep_link_with_comment_id>) — <summary>
...

**Draft reply (confidence: High):**

> Thanks <author>. I'll verify on dev today and confirm here.
```

No items: "No urgent items in `<KEY>` — your team is not currently blocked on you."

**Full mode format:**

```markdown
# Jira — All My Open Tasks: <KEY> ({YYYY-MM-DD})

### Top priority (review needed)
- [<KEY-N>](<task_link>) (<priority>) — <summary>
  - Last updated: <YYYY-MM-DD HH:MM>

### In Progress
- ...

### Ready for Development
- ...

### Other
- ...
```

### Step 9: Status

```
**Changed:** <N> urgent of <M> total (X ignored)
**Needs review:** <flags>

To ignore items you don't need to reply to, add their comment ID to `.local/jira/ignored-comments.txt`:
```
508167
506832
```
Ignored comments won't appear in future runs.
```

---

## Rules

| Rule | Detail |
|------|--------|
| Anchor IDs from API | Extract `comment.id` directly from JSON. Never retype or summarize IDs before building links. |
| Always re-query | Never reuse cached data. Each run must query Jira fresh. |
| Full output in chat | Print the same markdown that goes into the saved file. |
| Single project | No multi-project aggregation. Use `--choose` to switch. |
| Read-only | Never post comments or transition issues. Ask for confirmation before sending any draft. |
| Match on accountId | Never match on display name — names collide. |
| Skip answered | User comment after the urgent-trigger comment → drop. |
| Cap at 50 | If query hits 50, note in status. |

---

## Examples

```
jurgent                       → query Jira, save file, display
jurgent                       → (second run) show saved list, no API call
jurgent --refresh             → force re-query Jira
jurgent PROJ                  → urgent on specific project
jurgent --full                → all open tasks, no drafts
```

**After first run:** subsequent calls display from saved file without querying Jira. Only re-queries when you run `jurgent` again or use `--refresh`. This lets you loop through the list, reply, and ignore items without hitting the API each time.
