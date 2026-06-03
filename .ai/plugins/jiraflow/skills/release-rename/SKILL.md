---
name: release-rename
version: 0.1.0
description: Update the name of a JIRA release version. Provide release URL and new name.
triggers:
  - "release-rename"
  - "releaserename"
  - "rrename"
  - "rename release"
---

## Usage

- `release-rename https://saritasa.atlassian.net/projects/PROJ/versions/123 "New Release Name"`

## Workflow

### Step 1: Parse Input

Extract version ID from URL: `https://[DOMAIN].atlassian.net/projects/[KEY]/versions/[ID]`.
New name is the second argument (quoted string).

### Step 2: Get Current Name

```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -H "Accept: application/json" \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/version/[VERSION_ID]"
```

Show current name and ask confirmation:
```
Rename release:
  Current: [CURRENT_NAME]
  New:     [NEW_NAME]

Proceed? (yes/no)
```

### Step 3: Update Name

```bash
curl -s -u "[JIRA_EMAIL]:[JIRA_API_TOKEN]" \
  -X PUT \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"name": "[NEW_NAME]"}' \
  "https://[JIRA_COMPANY_DOMAIN].atlassian.net/rest/api/3/version/[VERSION_ID]"
```

### Step 4: Report

```
✅ Release renamed
   [NEW_NAME](https://[DOMAIN].atlassian.net/projects/[KEY]/versions/[ID])
   (was: [CURRENT_NAME])
```

## Credentials

Read from `.env` or `.env.local`:
```
JIRA_COMPANY_DOMAIN=saritasa
JIRA_EMAIL=you@saritasa.com
JIRA_API_TOKEN=your-token
```

## Rules

| Rule | Detail |
|------|--------|
| Always confirm | Show before/after before updating |
| Show release URL | Always include clickable link in final output |
