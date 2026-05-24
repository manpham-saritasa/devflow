# Get Summary

Generate both non-technical (Jira) and technical (PR) changelog reports from task evidence.
Preview reports without creating a PR or commenting Jira. Useful for past PRs, standalone reports, or dry-run previews.

## What do I need?

Pick one:

- **A GitHub PR URL** — just paste the link, the skill fetches everything from GitHub
- **A task key** (like `PROJ-123`) — from your branch name or you can provide it, plus a changelog at `.local/tasks/[KEY]/changelog.md`
- **A feature branch** — run it from the branch and it falls back to `git diff`

## When to use it

Use this skill when:
- You want a **clean report for a past PR** (for email, docs, or review)
- You want to **preview reports** before shipping (dry-run, test format and wording)
- You want **both Jira and PR reports** generated from the same source
- Another skill needs a clean non-technical or technical summary of your changes

## How to run it

```
/dev-get-summary [KEY | PR_URL]
```

Examples:
- `/dev-get-summary PROJ-123` — from local changelog
- `/dev-get-summary` — auto-detect key from current branch
- `/dev-get-summary https://github.com/owner/repo/pull/123` — from a GitHub PR

The skill will:
1. Extract evidence (PR API → local changelog → git diff, in that order)
2. Generate a **non-technical Jira report** (for testers, PMs, clients)
3. Generate a **technical PR report** (for future engineers)
4. Output both as **separate copyable code blocks**

## Output format

Reports are displayed in two standalone fenced code blocks — triple-click to copy each one.

**Jira Report:** links to the PR, title format: `[KEY] — PR #[N]`
**PR Report:** links to the Jira task, title format: `[KEY] — Task summary`

## Templates

This skill uses the same templates as `/dev-ship`:

- `jira-summary-template.md` — non-technical report: Added / Changed / Fixed / Testers / Notes
- `pr-summary-template.md` — technical report: Goal / Added / Changed / Fixed / Key decisions / Risks / Testing / Related areas / Future reuse guidance

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
