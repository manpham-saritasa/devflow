---
name: handoff
version: 0.1.0
description: Compact the current conversation into a handoff document for another agent to pick up.
triggers:
  - "handoff"
  - "hand-off"
  - "hand off"
argument-hint: "What will the next session be used for?"
---

# Handoff

Compact the current conversation into a structured document so a fresh agent can continue the work. Save to `.local/handoffs/` in the repo — persistent, gitignored, discoverable.

## When to use

Trigger on `handoff`, `hand-off`, or when the user wants to pass context to another agent.

If the user provides arguments after `handoff` (e.g. `handoff review the new skill`), treat them as the next session's purpose and include as the **Next session** section.

## Rules

- Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.
- Redact any sensitive information: API keys, passwords, PII.
- Save to `.local/handoffs/` (create directory if missing).
- If no prior work exists in the session, state that and write a minimal doc.

## Output format

Save as `handoff-YYYY-MM-DD.md` to `.local/handoffs/`.

```markdown
# Handoff — YYYY-MM-DD

## What happened

[1-2 sentence summary]

## Tasks completed

### 1. [Task title]

- [Key detail]
- [Key detail]

### 2. [Task title]

...

## Key files changed

### New
- `path/file.md`

### Modified
- `path/file.md` — [what changed]

### Deleted
- `path/file.md`

## Suggested skills

| Skill | Why |
|-------|-----|
| `skill-name` | [reason the next agent should invoke it] |

## Next session

[Purpose from user's argument-handoff, or "Not specified"]

## Current state

- Branch: [name]
- Commits: [hashes] (see `git --no-pager log --oneline -N`)
- Uncommitted: [files, or "none"]
```

### Reference examples

| Instead of... | Reference... |
|---------------|-------------|
| Pasting the full commit diff | `Commits: 1688abc, 36b0bc9 (see git log)` |
| Copying a plan file | `Plan: .local/tasks/DEV-15/plan.md` |
| Regurgitating a changelog | `Changelog: .local/tasks/DEV-15/changelog.md` |

## Stop conditions

Stop and ask if:
- Next session purpose is unclear and user didn't provide arguments
- Sensitive data is detected that can't be safely redacted
- `.local/handoffs/` is not writable
