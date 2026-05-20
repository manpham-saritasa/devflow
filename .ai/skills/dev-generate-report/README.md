# Generate Report

Generate a non-technical changelog for pull requests, Jira comments, or standalone use.
Converts technical changes into clear summaries for testers, project managers, and clients.

## What do I need?

Before using this skill:
1. A task key (like `PROJ-123`) — comes from your branch name or you can provide it
2. A changelog file (`.local/tasks/[KEY]/changelog.md`) — where your technical notes are stored

## When to use it

Use this skill when:
- You want to **preview** a non-technical report before shipping (test format and wording)
- You already have a `changelog.md` and want to **generate a report** from it (for email, docs, or review)
- You want to see what the report looks like without actually creating a PR or commenting Jira
- Another skill needs a clean, non-technical summary of your changes

## How to run it

Type in Claude Code:

```
/dev-generate-report [KEY]
```

Replace `[KEY]` with your task ID (like `PROJ-123`). The skill will:
1. Read your technical changelog from `.local/tasks/[KEY]/changelog.md`
2. Convert it to a non-technical report
3. Show you the result

## Format rules

**Keep it short and scannable.**

- Write in past tense (Added, Changed, Fixed — not Add, Change, Fix)
- **One line per item is the default** — that's usually enough
- Only add a sub-bullet if the main line needs explanation
- Never mention: variable names, function names, file paths, classes, methods, code details
- Skip empty sections (Added, Changed, Fixes) if they have nothing

## Template

See `./report-template.md` for the exact format.

## Example

**Input** (from technical changelog):
```
### Changes
- Reduced dashboard load time by optimizing queries
- Added filtering by date range on reports page
```

**Output** (non-technical report):
```
## Changed
[1] - Dashboard now loads faster.

## Added
[1] - Added date filter on reports.
  - Users can narrow results to a date range.
```

## Good vs. bad

### ✅ Good (non-technical)
```
## Added
[1] - Added export to PDF for monthly reports.

## Fixes
[1] - Fixed crash when opening a project with no tasks.
  - Only happened on first login after account creation.
```

### ❌ Bad (too technical)
```
## Added
[1] - Added exportToPdf() method in ReportService.cs.
  - Called from /api/reports/export endpoint.
  - Uses PdfSharp library v1.5.0.

## Fixes
[1] - Fixed NullReferenceException in SessionManager.Initialize().
```

## Who needs this?

This skill is used by:
- `dev-ship-pr-jira` — automatically generates reports when you ship
- You — when you need a clean report for any other reason
