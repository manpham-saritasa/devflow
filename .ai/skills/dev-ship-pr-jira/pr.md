# [DEV-03](https://github.com/quansaritasa/devflow/pull/5) — Update dev-ship-pr-jira to use separate templates

## Goal
- Split single `report-template.md` into two audience-specific templates: Jira (non-technical) and PR body (technical).

## Changes
- Replaced `report-template.md` with `jira-summary-template.md` and `pr-summary-template.md`.
- Updated `SKILL.md`: Paths, Output Style, Step 3 (dual reports), Step 5 preview, Step 6/8 body variables.
- Updated `README.md` to reflect split workflow.
- Generated `SKILL.html` and `README.html`.

## Key decisions
- Jira template: `Added / Changed / Fixed` with business sub-bullets. No code details.
- PR template: `Goal / Changes / Key decisions / Risks / Testing / Reuse later`. Code-level details allowed.
- Both use explicit path variables (`JIRA_TEMPLATE`, `PR_TEMPLATE`) to prevent agent confusion.

## Risks
- Agent may confuse which template for which channel — mitigated by explicit path variables in SKILL.md.

## Testing
- Verified: zero remaining `report-template.md` references in SKILL.md.
- Not verified: end-to-end dev-ship run with actual PR + Jira comment.

## Reuse later
- Safe to copy: YES
- Reusable pattern: Audience-specific templates with separate fill guides.
