---
name: jira-urgent
description: List Jira tasks where the team is waiting on you. Finds issues with unanswered mentions or questions, drafts replies.
triggers:
  - "jira-urgent"
  - "jurgent"
  - "my Jira tasks"
  - "what does my team need from me"
  - "urgent Jira items"
---

## Config

Read shared auth from `../../config.md`.

## Paths

- `IGNORE_FILE` — `./ignored-comments.txt` (skill-relative) — one comment ID per line

---

## Workflow

Run the Python script and present its output cleanly in chat:

```bash
python .ai/plugins/jiraflow/skills/jira-urgent/scripts/main.py
```

Then for each item found, fetch the full comment body from Jira and draft a reply per the classification rules below. Present as formatted markdown — not raw terminal output.

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

---

## Output Format (Strict — follow exactly)

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

> Thanks <author>. I'll verify today and confirm here.
```

No items: "No urgent items in `<KEY>` — your team is not currently blocked on you."

---

## Draft Reply Templates

| Tag | Template |
|-----|----------|
| `verify`, `at_mention_verify` | "Thanks `<author>`. I'll verify today and confirm here." |
| `at_mention`, `question` | Substantive reply addressing the question. 2-6 sentences. |

Rules:
- Address teammate by `anchor_author`
- Insufficient context → `**I'm not sure yet.**` + how to find out
- Never invent decisions
- Tag confidence: `High`, `Medium`, `Low`

---

## Rules

| Rule | Detail |
|------|--------|
| Always re-query | Never reuse cached data. Each run must query Jira fresh. |
| Print to chat | Present clean formatted markdown in chat. Do not save to file. |
| Single project | Use `[PROJECT_KEY]` to switch. |
| Read-only | Never post comments or transition issues. Ask for confirmation before sending any draft. |
- Match on accountId | Never match on display name — names collide.
- Skip answered | User comment after the urgent-trigger comment → drop.

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Default project from `JIRA_PROJECT_KEY` in `.env.jira` |
| `[PROJECT_KEY]` | Override project key (e.g., `PROJ`) |
