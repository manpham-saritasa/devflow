---
name: release-note
description: Generate a client-friendly release note from tasks in a JIRA release. Categorizes into Changed and Fixed sections.
triggers:
  - "release-note"
  - "releasenote"
  - "release-note --full"
---

## When to Use

- `release-note "API next version"` — by release name
- `release-note https://saritasa.atlassian.net/projects/PROJ/versions/123` — by URL
- `release-note --full "API next version"` — include task IDs and URLs for internal review
- Generate client-facing changelog before a release

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Client copy only — no task IDs, clean for sharing |
| `--full` | Internal copy — includes task IDs and clickable JIRA URLs |

## Credentials

Read from `.env` or `.env.local` in repo root:
```
JIRA_COMPANY_DOMAIN=saritasa
JIRA_EMAIL=you@saritasa.com
JIRA_API_TOKEN=your-token
```

## Workflow

### Step 1: Parse Input

- Extract release identifier from user input (name or URL)
- If no release: ask "Release name or URL?"

### Step 2: Resolve Release

**If URL:** extract version ID from `https://[DOMAIN].atlassian.net/projects/[KEY]/versions/[ID]`

**If name:** search for the version:
```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/project/[JIRA_PROJECT_KEY]/version?query=[RELEASE_NAME]" \
  | jq -r '.values[0].id'
```

### Step 3: Get Tasks in Release

Fetch all issues with this fixVersion:
```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/search/jql" \
  --data-urlencode "jql=fixVersion=[VERSION_ID]" \
  --data-urlencode "fields=summary,issuetype" \
  --data-urlencode "maxResults=200" \
  | jq '.issues[] | {key, summary: .fields.summary, type: .fields.issuetype.name}'
```

### Step 4: Categorize and Summarize

Categorize each task:

| Issue type | Category |
|------------|----------|
| Story, Task, Improvement, New Feature | **Changed** |
| Bug | **Fixed** |
| Sub-task | Follow parent category |
| Epic, Spike, Tech Debt | Include in **Changed** |

**Summarize each task** into 1 short line.
- Client-focused: describe the user-visible outcome, not technical details.
- Remove prefixes like "API -" or "Admin -" — they are JIRA component labels, not useful to clients.
- Start with a past-tense verb when possible (Added, Updated, Fixed, Improved, Removed).

**Group summary writing rules::**
- Tone: professional, neutral, factual. Like a product changelog.
- Style: one flowing sentence listing the key changes in the group. Use commas and "and" to chain related items.
- Length: 10 to 50 words per group summary.
- Example: "Improved employee sync by adding supervisor mapping, filtering out terminated accounts, adjusting hire dates to midnight, and adding outlier reports for personal emails."

### Step 5: Format Release Note

Group related tasks by theme (e.g. AD Sync, API, Admin, Budget). Each group gets a sub-heading with a short paragraph summarizing the group. Use this format:

```
## Release Note — [VERSION_NAME]

**[Group Name]:**
- A short paragraph summarizing all tasks in this group as one coherent sentence or two.

**[Group Name]:**
- A short paragraph summarizing all tasks in this group.
```

**Client copy** (no task IDs):
```
## Release Note — API next version


**AD Sync:**
- Improved employee sync by adding supervisor mapping, filtering out terminated accounts, adjusting hire dates to midnight, and adding outlier reports for personal emails.

**API:**
- Updated lab sample date fields, added text positioning for master form PDFs, created version management endpoints, and added Copilot instruction files for code review.
```

**Internal copy** (with task IDs):
```
## Release Note — API next version


**AD Sync:**
- [PROJ-1988, PROJ-1989, PROJ-1990, PROJ-1991] Improved employee sync by adding supervisor mapping, filtering out terminated accounts, adjusting hire dates to midnight, and adding outlier reports for personal emails.
```

Rules:
- Group 2-5 related tasks under a thematic sub-heading.
- Follow the group summary writing rules from Step 4 (tone, style, length).
- Client copy: no task IDs. Internal copy: list keys in brackets before the summary.
- If a section has no items, omit it entirely.

### Step 6: Report

**Default (no flag):** show the client copy only — grouped paragraphs, no task IDs.

**--full:** show the internal copy — grouped paragraphs with `[KEY]` prefix and clickable JIRA URLs. Include a separate block with individual task links for quick access.

Client copy format:
```
## Release Note — [VERSION_NAME]

**[Group Name]:**
- Group summary paragraph.
```

--full format:
```
## Release Note — [VERSION_NAME]

**[Group Name]:**
- [KEY, KEY] Group summary paragraph.

---
Tasks:
- [KEY](https://JIRA/browse/KEY) — Task summary
- [KEY](https://JIRA/browse/KEY) — Task summary
```

Show total counts at the bottom:
```
Total: [N] tasks ([N] changed, [N] fixed)
Release: [RELEASE_URL]
```
