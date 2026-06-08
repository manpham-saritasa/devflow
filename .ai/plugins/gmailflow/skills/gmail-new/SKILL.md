---
name: gmail-new
description: Read and summarize new Gmail messages using Gmail API-based tooling.
triggers:
  - "gmail-new"
  - "new gmail"
  - "summarize new email"
---

## Goal

Read recent Gmail messages and produce a concise summary of what is new and likely important.

## Shared config

Read Gmail auth from `../../config.md`.

Credentials are expected in `.env.gmail` ở repo root.

Required variables:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`
- `GMAIL_ACCOUNT`

The script uses Google official Python libraries and Gmail read-only scope.

## Install dependencies

```bash
python -m pip install -r .ai/plugins/gmailflow/skills/gmail-new/requirements.txt
```

If `python` is not available on Windows, use:

```bash
py.exe -m pip install -r .ai/plugins/gmailflow/skills/gmail-new/requirements.txt
```

## Run

```bash
python .ai/plugins/gmailflow/skills/gmail-new/scripts/main.py
```

Useful flags:

```bash
python .ai/plugins/gmailflow/skills/gmail-new/scripts/main.py --json
python .ai/plugins/gmailflow/skills/gmail-new/scripts/main.py --max-results 20
python .ai/plugins/gmailflow/skills/gmail-new/scripts/main.py --query "is:unread"
python .ai/plugins/gmailflow/skills/gmail-new/scripts/main.py RMASUP
python .ai/plugins/gmailflow/skills/gmail-new/scripts/main.py --projects RMASUP,SALES
python .ai/plugins/gmailflow/skills/gmail-new/scripts/main.py --project-labels
```

## Get refresh token

If `GOOGLE_REFRESH_TOKEN` is missing, run:

```bash
python .ai/plugins/gmailflow/skills/gmail-new/scripts/get_refresh_token.py
```

If `python` is not available on Windows, use:

```bash
py.exe .ai/plugins/gmailflow/skills/gmail-new/scripts/get_refresh_token.py
```

The script opens a local Google OAuth flow and prints a `refresh_token` to copy into `.env.gmail`.

## Output format

If `--json` is used, the script should return structured data. Format it in chat like this:

```text
gmail-new

1. [Importance] Subject
   From: sender@example.com
   Time: 2026-06-05 09:12
   Why it matters: short reason
   Summary: 1-2 sentence summary

2. [Low] Another subject
   From: someone@example.com
   Time: 2026-06-05 08:40
   Why it matters: optional
   Summary: 1-2 sentence summary
```

Then provide:
- urgent items first
- follow-ups or unanswered asks
- anything blocked by missing reply
- group by matched project key when project-label filtering is active

## Rules

- Summarize only what the script actually returns.
- Do not invent email content.
- If auth is incomplete, say so clearly.
- If Gmail API returns no matching messages, say so clearly.
- Prefer unread/recent mail unless the user gives a custom query.
- If `--project-labels` is used, or a positional project like `RMASUP` is provided, read project-to-label mappings from `.local/gmailflow/project-labels.txt`.
- Support mapping lines in `.local/gmailflow/project-labels.txt` as `PROJECT=LabelName=LabelId`.
- If a mapping has no `LabelId` yet, resolve it from Gmail labels on first use and save it back for the user.
- Filter by actual Gmail labels, not guessed project keys in message text.
- Redact secrets if they appear anywhere unexpectedly.
- Use only what the Gmail API actually returned.
