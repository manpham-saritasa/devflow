---
name: dev-generate-report
description: |
  Non-technical report format for GitHub PR body and Jira task comments.
  Write for testers, PMs, and clients. Added / Changed / Fixes sections,
  numbered items, optional sub-bullets. No code-level details.
triggers:
  - "dev-generate-report"
---

## Purpose

Defines the canonical format for non-technical changelogs used in PR bodies and Jira comments.

## Format Rules

- Past tense, outcome-focused, minimal English
- **Never**: variable names, function names, class names, file paths, method calls, code-level details
- Describe behavior and user impact only — no exceptions
- Omit empty sections
- Numbered items `[1][2][3]`; sub-bullets only when extra context is needed

## Template

See `./report-template.md`.
