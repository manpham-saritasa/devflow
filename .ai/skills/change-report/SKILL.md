---
name: change-report
description: Generate a structured inline review report of all code changes made. Use when user says "change report", "creport", or wants to review recent changes without reading verbose output.
triggers:
  - "change report"
  - "creport"
  - "change report --diff"
  - "creport --diff"
---

## When to Use

Append this report after finishing any code editing task. Trigger on `creport` or when user asks to see what changed.

## Flags

| Flag | Behavior |
|------|----------|
| (none) | Show inline change report in chat |
| `--diff` | Also save `git diff` of all changed files to `DIFF.md` in the skill folder |

## Rules

- Write the report AFTER all code edits are complete. Do not edit files while writing it.
- Only report uncommitted changes. Committed changes mean the user already reviewed and agreed — skip them.
- If no uncommitted changes remain, report that clearly and skip the rest.
- Group changes by logical purpose, like `dev-commit` groups files:
  - Files changed together in the same step → one group
  - Files with the same purpose (e.g. all templates, all config) → one group
  - Unrelated files → separate groups
- Order groups by timeline — oldest first, newest last.
- Number each group so the user can reference them: "group #3 looks wrong."
- Explanation is required for every group.

## Final Response: Change Report

```text
### 1: [Group title]

🤖: [One-line summary of what changed and why]

- Explanation: [practical impact, benefits, or what this means for the user/project]

- Files: path/a.md, path/b.py

### 2: [Group title]

...

### Integrity Check

- I only changed the files and areas listed above.
- I did not make unrelated refactors or hidden edits.
```
