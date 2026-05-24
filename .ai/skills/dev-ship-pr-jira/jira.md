## [DEV-03] — Update dev-ship-pr-jira to use separate templates

## Changed
**[1] - Split report template into two audience-specific templates.**
  - Reason: Single template served both PR and Jira but audiences need different content.
  - Impact: PR gets technical report (architecture, decisions, risks). Jira gets non-technical summary (behavior, user impact).

**[2] - Updated skill workflow to generate two separate reports.**
  - Reason: Step 3 now creates both reports using different templates and rules.
  - Impact: Preview shows both side by side. PR body uses `{PR_BODY}`, Jira comment uses `{JIRA_BODY}`.

## Notes
- `report-template.md` deleted, replaced by `jira-summary-template.md` and `pr-summary-template.md`.
- HTML previews of SKILL.md and README.md generated alongside.

[View PR](https://github.com/quansaritasa/devflow/pull/5)
