---
name: gmail-jira
description: Create a Jira task from a Gmail message and draft a reply with the task ID.
triggers:
  - "gmail-jira"
  - "create task from email"
  - "email to jira"
  - "jira from email"
---

## Goal

Turn a Gmail message into a Jira task: analyze content, propose task details, create in Jira, attach screenshots, and draft a reply email with the task ID.

## Shared config

Read Gmail auth from `../../config.md`. Read Jira auth from `../../../jiraflow/config.md`.

Credentials:
- Gmail: `.env.gmail` (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN, GMAIL_ACCOUNT)
- Jira: `.env.jira` (JIRA_COMPANY_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN)
- Scopes needed: `gmail.readonly` + `gmail.compose`

## Flow

### Step 1 — User selects an email

User runs `gmail-new` first to see emails, then says "create task for email #N."

If the email already has full body loaded from a previous step, use it. Otherwise fetch the full message via Gmail API:

```
GET /gmail/v1/users/me/messages/{id}?format=full
```

Extract: subject, from, to, date, body (text/plain or stripped HTML), threadId, Message-ID header, attachment IDs.

### Step 2 — Analyze and propose

Read the project's available components and issue types from Jira API:

```
GET /rest/api/3/project/{PROJECT_KEY}/components
GET /rest/api/3/project/{PROJECT_KEY}
```

Read `.local/gmailflow/project-labels.txt` if filtering by project label.

**Suggest these fields from email content:**

| Field | How to determine |
|-------|-----------------|
| **Component** | Match keywords in subject/body to project component names (e.g., "Forney Vault" → Forney, "LIMS" → LIMS, "Field App" → Field App). Show the matched component name. |
| **Issue Type** | Bug if email describes a defect/error. Task if it's a request. Story if it's a feature ask. |
| **Summary** | Format: `[Component name] - [Short description from email]`. Keep under 80 chars. |
| **Environment** | Infer from email context: "Production", "Staging", or specific server/URL mentioned. |
| **Sprint** | Always assign to the *current active sprint* for the project. |

**Build the description using `templates/task-template.md`** — fill in Overview, Source, Environment, Steps to Reproduce, Notes from the email content.

### Step 3 — Ask open questions

If any field is ambiguous, ask the user 1-2 numbered questions before showing the proposal:

```
❓ 1. Component: email mentions both "LIMS" and "Forney Vault" — which component?
❓ 2. Type: is this a Bug or a Task?
```

- Only ask when genuinely ambiguous. Don't ask question for fields that are clear.
- Number every question so the user can answer by number.
- Wait for answers before proceeding to Step 4.

### Step 4 — Show before creating

Show the proposed task to the user in a table:

```
## Proposed Task

| Field | Value |
|-------|-------|
| Project | {KEY} |
| Type | {Bug/Task/Story} |
| Component | {name} |
| Summary | {summary} |
| Sprint | {current sprint name} |
| Environment | {inferred} |

**Description preview:**
> [first few lines of description]

Attachments: {N} screenshot(s) from email
Reply draft: [yes/no]
```

Wait for user to confirm ("yes" or adjust).

### Step 5 — Create the Jira task

Use Jira REST API v3:

```
POST /rest/api/3/issue
```

**Payload:**

```json
{
  "fields": {
    "project": {"key": "RMASUP"},
    "summary": "...",
    "description": { ADF doc },
    "issuetype": {"id": "1"},
    "components": [{"id": "..."}],
    "customfield_10006": {sprint_id},
    "customfield_XXXXX": {"value": "Production"}
  }
}
```

**Key notes:**
- Description MUST be Atlassian Document Format (ADF), not plain text.
- Sprint field (`customfield_10006`) takes the sprint ID as a number.
- Environment field — discover its custom field ID by querying the project's create metadata or using known IDs. Common IDs: `customfield_10006` for sprint. Environment varies by project.

**Set the current sprint:**
```
GET /rest/agile/1.0/board?projectKeyOrId={KEY}
```
Pick the first `scrum` board, then:
```
GET /rest/agile/1.0/board/{boardId}/sprint?state=active
```
Use the first active sprint's `id` as `customfield_10006` in the issue payload (integer).

**To discover the Environment field ID:**
```
GET /rest/api/3/issue/createmeta?projectKeys={KEY}&issuetypeIds={TYPE_ID}&expand=projects.issuetypes.fields
```
Search for "Environment" in the returned fields and note its `fieldId`.

### Step 6 — Attach email screenshots

Fetch each attachment from the Gmail message:
```
GET /gmail/v1/users/me/messages/{msgId}/attachments/{attachmentId}
```

Upload to Jira:
```
POST /rest/api/3/issue/{issueKey}/attachments
Header: X-Atlassian-Token: no-check
Body: multipart/form-data with the file
```

> **Attachment filtering rules:**
- Files with `Content-Disposition: attachment` → always upload (PDF, XLSX, etc.). These are the real evidence.
> - Inline images from `multipart/related` are email body content, not real attachments:
>   - `image001.png` → auto-skip (Outlook signature, consistently ~4KB).
>   - Small images (<10KB) + no issue reference in body → signatures/icons → skip.
>   - Only include an inline image if it is explicitly a screenshot of the issue described in the email.
> - When unsure, ask user: "[N] file attachments + [M] inline images found. Upload which?"

### Step 7 — Draft reply email

Create a Gmail draft replying to the thread using the original Message-ID:

```python
msg = MIMEText(body)
msg['To'] = original_from
msg['Subject'] = f'Re: {original_subject}'
msg['In-Reply-To'] = original_message_id
msg['References'] = original_message_id
```

Draft body template (from `templates/reply-template.md`):

```
Got it.

We will take a look at it soon.
Item {TASK-KEY}

Regards,
```

Create via:
```
POST /gmail/v1/users/me/drafts
```

### Step 8 — Report back

Show:
- Task key with clickable URL: [RMASUP-2195](https://saritasa.atlassian.net/browse/RMASUP-2195)
- Number of attachments uploaded
- Draft status (created, check Drafts)

## Output format

```
Task created: [RMASUP-XXXX](url)
Type: Bug | Component: Forney | Sprint: Sprint 123
3 screenshots attached
Draft reply ready in Gmail Drafts
```

## Rules

- Always show the proposed task before creating. Do not create without confirmation.
- Never hardcode field IDs — discover them from Jira API when needed.
- If a field is not found, skip it rather than guessing an ID.
- Use ADF for description. Convert markdown-like text to ADF nodes.
- Skip signature images (image001.png) when attaching screenshots.
- If the user's project label mapping is missing, prompt them to add it first via `gmail-new --project-labels`.
- If Jira or Gmail auth is incomplete, stop and report exactly which vars are missing.
- Redact secrets if they appear anywhere in output.
