# GmailFlow Plugin — Shared Configuration

## Paths

| Variable | Value | Description |
|----------|-------|-------------|
| `PLUGIN_ROOT` | `.ai/plugins/gmailflow` | Plugin root (repo-relative) |
| `ENV_FILE` | `.env.gmail` | Env file cho Gmail auth ở repo root |

## Skills

| Skill | Path | Description |
|-------|------|-------------|
| gmail-new | `skills/gmail-new/` | Read and summarize new Gmail messages |
| gmail-jira | `skills/gmail-jira/` | Create Jira task from email + draft reply |

## Auth

All GmailFlow skills read credentials from `.env.gmail` ở repo root.

Required variables:

- `GOOGLE_CLIENT_ID` — Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` — Google OAuth client secret
- `GOOGLE_REFRESH_TOKEN` — OAuth refresh token for Gmail API access
- `GMAIL_ACCOUNT` — mailbox address to read

## Local config

Optional local config file:

- `.local/gmailflow/project-labels.txt`

Format:

```text
RMASUP=0. RMA=Label_7795671500879232481
SALES=0. Sales=Label_1234567890
PROJ=0. Project
```

Notes:

- Preferred format is `PROJECT=LabelName=LabelId`.
- `LabelId` may be omitted initially.
- On first successful use, GmailFlow should resolve the Gmail label ID from `LabelName` and save it back into the file.

## Expected behavior

- Never print secret values back to the user.
- If required env vars are missing, stop and report exactly which ones are missing.
- Prefer Gmail API over IMAP/SMTP for mailbox reads and thread metadata.
