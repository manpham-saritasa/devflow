---
name: release-note
description: Generate a client-friendly release note from tasks in a JIRA release. Categorizes into Changed and Fixed sections.
triggers:
  - "release-note"
  - "releasenote"
  - "rnote"
  - "release-note --full"
---

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

Fetch all issues with this fixVersion using GET:
```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -H "Accept: application/json" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/search/jql?jql=fixVersion%3D[VERSION_ID]&fields=summary,issuetype&maxResults=200"
```

### Step 4: Categorize and Summarize

Categorize each task:

| Issue type | Category |
|------------|----------|
| Story, Task, Improvement, New Feature | **Changed** |
| Bug | **Fixed** |
| Sub-task | Follow parent category |
| Epic, Spike, Tech Debt | Include in **Changed** |

**Summarize each task** into a short, past-tense bullet. One line per task.
- Client-focused: describe the user-visible outcome, not technical details.
- Remove prefixes like "API -" or "Admin -" — Jira component labels.
- Start with a past-tense verb: Added, Updated, Fixed, Improved, Removed.

### Step 5: Format Release Note

Group related tasks by theme (e.g. AD Sync, API, Admin, Budget). Each group gets a sub-heading with individual task bullets. Use this format:

```
## Release Note — [VERSION_NAME]

**[Group Name]:**
- Task description. (KEY)
- Task description. (KEY)
```

**Client copy** (no task IDs):
```
## Release Note — API next version

**AD Sync:**
- Improved employee sync by adding supervisor mapping. (PROJ-1988)
- Added filtering for terminated accounts. (PROJ-1989)
- Adjusted hire dates to midnight. (PROJ-1990)

**API:**
- Updated lab sample date fields. (PROJ-1991)
- Added text positioning for master form PDFs. (PROJ-1992)
```

**Internal copy** (with task IDs, `--full` flag):
```
## Release Note — API next version

**AD Sync:**
- [PROJ-1988](https://JIRA/browse/PROJ-1988) — Improved employee sync by adding supervisor mapping.
- [PROJ-1989](https://JIRA/browse/PROJ-1989) — Added filtering for terminated accounts.

**API:**
- [PROJ-1991](https://JIRA/browse/PROJ-1991) — Updated lab sample date fields.
```

### Step 6: Report

**Default (no flag):** show the client copy only — grouped paragraphs, no task IDs.

**--full:** show the internal copy — grouped paragraphs with `[KEY]` prefix and clickable JIRA URLs. Include a separate block with individual task links for quick access.

Client copy format:
```
## Release Note — [VERSION_NAME]

**[Group Name]:**
- Task description.
- Task description.
```

--full format:
```
## Release Note — [VERSION_NAME]

**[Group Name]:**
- [KEY](https://JIRA/browse/KEY) — Task description.
- [KEY](https://JIRA/browse/KEY) — Task description.
```

Show total counts at the bottom:
```
Release: [VERSION_NAME](https://[DOMAIN].atlassian.net/projects/[KEY]/versions/[ID])
Total: [N] tasks ([N] changed, [N] fixed)
```

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

Read from `.env` or `.env.jira` in repo root:
```
JIRA_COMPANY_DOMAIN=saritasa
JIRA_EMAIL=you@saritasa.com
JIRA_API_TOKEN=your-token
```
