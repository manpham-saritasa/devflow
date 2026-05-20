Generate changelog content for the current local branch using all available branch-related context.

Primary goal:
- Produce concise changelog content that can be pasted into a Jira comment or GitHub PR comment.
- Reflect what was actually implemented on this branch, not just what was planned in the Jira ticket.

Use all available inputs if present:
- User input or manual notes.
- Jira key, title, description, comments, acceptance criteria, linked tasks.
- Current branch name.
- PR title and PR description draft.
- Local commit messages.
- Changed files.
- Git diff or staged diff.
- Added or updated tests.
- Screenshots or short implementation notes.

How to interpret sources:
- Use Jira and user input to understand business intent.
- Use the local diff, commit history, and changed files to determine what was actually changed.
- Use file names, symbols, selectors, routes, configuration changes, and test changes to identify scope, affected platform, and bug causes.
- If Jira says one thing but the diff shows a narrower implementation, describe the narrower shipped change.
- If the branch contains multiple distinct outcomes, split them into multiple items.

Filtering rules:
- Include only meaningful user-visible or support-relevant changes.
- Exclude pure refactors, renames, formatting, comments, dead-code cleanup, dependency bumps, and test-only changes unless they changed visible behavior or explain a fix.
- Do not copy commit messages verbatim unless they are already clear, user-facing, and accurate.
- Do not mention files, classes, methods, or PR mechanics in the main bullet unless that detail is necessary for clarity.

Classification rules:
- Added = new capabilities, new flows, new UI elements, new rules, new support behavior.
- Changed = updates to existing behavior, UI, wording, logic, workflow, restrictions, or calculations.
- Fixed = corrected bugs, broken states, incorrect calculations, layout issues, inconsistent behavior, crashes, or regressions.

Writing rules:
- Use the exact headings: Added, Changed, Fixed.
- Number items as [1], [2], [3].
- Keep each main line short, specific, and outcome-focused.
- Main lines should describe the delivered outcome in plain language.
- Sub-bullets should add non-redundant context only.
- Write in past tense.
- Preserve exact product, feature, screen, and platform names if known.
- Omit empty sections.
- Omit optional lines when they are not useful.
- Do not include QA steps, regression risk, testing checklist, deployment notes, or reviewer instructions.
- Do not overclaim. If the branch only partially implements the Jira task, describe only what is supported by the branch.

Field rules:
- Added
  - Purpose: why the new item was introduced.
  - Details: optional scope or useful context.

- Changed
  - Reason: why the existing behavior was updated.
  - Impact: optional resulting effect.

- Fixed
  - Root cause: why the bug happened, based on branch evidence and Jira context.
  - Resolution: what was changed to fix it, based on the implementation.

Output format:

```md
#Changelog for [JIRA TASK ID] — [Task summary]

## Added
**[1] - Added [item].**
  - Purpose: ...
  - Details: ...   // optional

## Changed
**[1] - Changed [item].**
  - Reason: ...
  - Impact: ...   // optional

## Fixed
**[1] - Fixed [item].**
  - Root cause: ...
  - Resolution: ...
```

Final checks:
- Every item is supported by branch evidence or Jira context.
- Main lines are readable in a Jira or PR comment.
- Sub-bullets add information instead of repeating the main line.
- The result is concise, accurate, and ready to paste.