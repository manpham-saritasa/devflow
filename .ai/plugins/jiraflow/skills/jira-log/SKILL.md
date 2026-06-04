---
name: jira-log
description: Log time to a Jira issue via Tempo. Shows daily total after logging.
triggers:
  - "jira-log"
  - "jlog"
---

## Usage

```
jlog                        → show today's hours
jlog list                   → show quick-pick task list
jlog <#|KEY> <DURATION> <DESC>

  jlog PROJ-1 30m Email         → pick task #1 from tasks.txt
  jlog PROJ-1 1h Code           → log directly by key
  jlog 6 1h --job Dev "Setup"   → with job type
  jlog --help                    → show usage
```

Quick-pick tasks in `.local/jiraflow/tasks.txt` — edit to customize.

---

## Workflow

Run the Python script with KEY, duration, and description:

```bash
python .ai/plugins/jiraflow/skills/jira-log/main.py <KEY> <DURATION> <DESCRIPTION>
```

| Arg | Format | Example |
|-----|--------|---------|
| KEY | `PROJ-123` | `RMASUP-1` |
| DURATION | `Xh` or `Xm` | `1h`, `30m` |
| DESCRIPTION | Quoted string | `"Email handle"` |

The script handles Tempo auth, time logging, local file tracking, and daily total. Show its output in chat with clickable issue links.

### Required env vars

Set in `.env.local` (preferred) or `.env`:

```env
JIRA_COMPANY_DOMAIN=saritasa
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=your_api_token_here
JIRA_PROJECT_KEY=PROJ
TEMPO_API_TOKEN=your_tempo_token_here
JLOG_JOB_TYPE=Testingfunctionality
```

- `JLOG_JOB_TYPE` sets the default Tempo job type for your team. Falls back to `Testingfunctionality` if not set.

### Draft before logging when description is vague

If the user's description is vague, placeholder-like, or likely an example — for example:
- very short generic text like `review`, `follow up`, `Email handle`
- placeholder text like `summary of my actions`, `read task, comment task`, `...`
- wording that looks like instruction to the agent rather than final worklog text

Then do **not** log immediately.

Instead:
1. Infer likely worklog text only from task context that directly supports the user's work (summary, relevant issue history, recent actions discussed in chat).
2. Show 1-3 short draft descriptions per task.
3. If logging multiple tasks, draft one description per task unless the user explicitly says to reuse the same sentence for all selected tasks.
4. Ask user to confirm or edit the draft.
5. Only run the script after the user approves the final wording.

When drafting:
- Prefer concrete action verbs: `reviewed`, `investigated`, `commented`, `updated`, `coordinated`, `tested`, `verified`.
- Write the final description as a short, clean sentence in past tense.
- Capitalize the first word and end with a period.
- Keep each description short and billable.
- Do not invent work the user did not mention or strongly imply.
- If confidence is low, say so and ask for correction before logging.

---

## Rules

| Rule | Detail |
|------|--------|
| Always show total | Print daily total table after each log entry. |
| Default Job Type | `JLOG_JOB_TYPE` env var, or `Testingfunctionality` if not set. |
| Draft first if vague | If description is vague/example-like, propose drafts and ask before logging. |
