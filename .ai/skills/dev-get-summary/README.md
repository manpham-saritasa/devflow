# Get Summary

Generate both non-technical (Jira) and technical (PR) changelog reports from task evidence.
Preview reports without creating a PR or commenting Jira. Useful for past PRs, standalone reports, or dry-run previews.

## What do I need?

Before using this skill:
1. A task key (like `PROJ-123`) — comes from your branch name or you can provide it
2. A changelog file (`.local/tasks/[KEY]/changelog.md`) — where your technical notes are stored

## When to use it

Use this skill when:
- You want a **clean report for a past PR** (for email, docs, or review)
- You want to **preview reports** before shipping (dry-run, test format and wording)
- You already have a `changelog.md` and want to **generate both reports** from it
- Another skill needs a clean non-technical or technical summary of your changes

## How to run it

Type:

```
/dev-get-summary [KEY]
```

Replace `[KEY]` with your task ID (like `PROJ-123`), or omit it to auto-detect from your current branch.

The skill will:
1. Read your technical changelog from `.local/tasks/[KEY]/changelog.md`
2. Generate a **non-technical Jira report** (for testers, PMs, clients)
3. Generate a **technical PR report** (for future engineers)
4. Show you both results

## Templates

This skill uses the same templates as `/dev-ship`:

- `jira-summary-template.md` — non-technical report with Added / Changed / Fixed / Testers / Notes
- `pr-summary-template.md` — technical report with Goal / Added / Changed / Fixed / Key decisions / Risks / Testing / Related areas / Future reuse guidance

## Format rules

### Jira report (non-technical)
- Past tense, outcome-focused, minimal English
- **Never**: variable names, function names, class names, file paths, method calls, code-level details
- Describe behavior and user impact only
- Omit empty sections

### PR report (technical)
- Past tense, design and behavior focused
- Include file paths, method names, architectural decisions, code patterns
- Separate verified from not-verified in testing section
- Mark reuse patterns with Safe to copy: YES/NO/WITH CARE
- Omit empty sections

## Who needs this?

This skill is used by:
- `dev-ship-pr-jira` — automatically generates reports when you ship
- You — when you need clean reports for any other reason (past PRs, docs, review, dry-run)
