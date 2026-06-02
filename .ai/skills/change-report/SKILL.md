---
name: change-report
version: 0.3.0
description: Auto-detecting change report — smart preview before changes, audit after. Say "change report" and the LLM shows the right report based on current state.
triggers:
  - "change report"
  - "creport"
  - "change report --diff"
  - "creport --diff"
---

## How it works

When user says `creport` (no flags), auto-detect the phase:

```
Is there a pending plan/proposal?
  └─ Yes → show 📋 Planned Changes (preview mode)
  └─ No  → check git status
              └─ Uncommitted changes exist → show ✅ Change Report (after mode)
              └─ No uncommitted changes       → "No changes planned or made."
```

**Note:** Triggers (`creport`, `change report`) are AI-side keywords — the LLM picks them up from frontmatter. User-side shortcuts (like `cush`, `ship`) are separate — add `creport` to `.local/memory.md` shortcuts if you want shorthand.

## Flags

| Flag | Behavior |
|------|----------|
| (none) | **Auto-detect.** Shows preview if plan pending, after-report if changes made. |
| `--diff` | Force after mode + save `git diff` to `DIFF.md` in the skill folder |

### --diff implementation

1. Run `git --no-pager diff` to capture all uncommitted changes.
2. Write the raw diff output to `DIFF.md` inside the skill folder, wrapped in a ` ```diff ` code block.
3. Prefix with `# Change Report — YYYY-MM-DD` heading.
4. Overwrite `DIFF.md` on each run. Delete after commit when no longer needed.
5. If diff is empty, write "No uncommitted changes." instead.

## Rules

### Detection (auto mode)

When user says `creport` with no flag:
1. Check if the LLM has stated a plan with specific files but not yet executed file edits → Preview mode.
2. If no pending plan, run `git --no-pager status --short` to check for uncommitted changes → After mode.
3. If neither → report "No changes planned or made" and stop.

### Preview mode

- Show the plan, not the result. No code changed yet.
- List every file that will be touched and what will happen (edit, new, rename, delete).
- Tag each group with a change type: `new`, `fix`, `refactor`, `style`, `docs`, `config`.
- Assess risk per group: low / medium / high — with a one-line reason.
- If the plan is unclear or scope uncertain, state that explicitly.

### After mode

- Write the report AFTER all code edits are complete. Do not edit files while writing it.
- Only report uncommitted changes. Committed changes mean the user already reviewed and agreed — skip them.
- If no uncommitted changes remain, report that clearly and skip the rest.
- Group changes by logical purpose:
  - Changes made together in the same step → one group
  - Changes with the same purpose (e.g. all templates, all config, all renames) → one group
  - Unrelated changes → separate groups
- Order groups by timeline — oldest first, newest last.
- Number each group so the user can reference them: "group #3 looks wrong."
- Explanation is required for every group.

## Response Templates

### Preview mode

```text
## 📋 Planned Changes

### 1: [Group title]

📝 Plan: [One-line summary of the planned change]

- Files: path/a.md (edit), path/b.py (new)
- Type: refactor / new / fix / docs / config
- Why: [reason for change]
- Risk: low / medium / high — [why]

### 2: [Group title]

...

### Total
- Files: N
- Groups: N
```

### After mode: Change Report (default / `--diff`)

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
