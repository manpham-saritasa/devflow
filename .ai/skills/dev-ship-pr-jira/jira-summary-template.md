## Fill guide
- Audience: Testers, PMs, clients.
- Rule: Describe behavior and user impact only. Do not mention code-level details.
- Use these evidence sources, in this order:
  1. Jira task title and description.
  2. Acceptance criteria or business notes.
  3. Commit messages.
  4. Local changed files and diff, but translate technical changes into user-visible behavior.
- Prefer facts stated in Jira when available.
- Use local code changes only to confirm what behavior changed.
- Do not mention variable names, function names, class names, file paths, method calls, database tables, or internal architecture.
- If a detail is not clear from evidence, omit it.
- Extract from evidence only. Do not invent reasons, impacts, or root causes.
- Group small technical edits into one meaningful user-facing change.
- If unclear, omit rather than guess.
- Omit empty sections.
- Use past tense.

## Fill rules by section
- Summary: One short sentence. State the main delivered outcome.
- Added: Use for new user-visible capabilities only.
- Changed: Use for behavior updates, workflow changes, wording changes, validation changes, or UX improvements.
- Fixed: Use for bugs or incorrect previous behavior. Root cause should be written in plain business language, not technical internals.
- Notes: Use only for important tester guidance, rollout notes, or clear limitations.

## Output template

```md
## [KEY] — [Task summary]

## Added
**[1] - [Category] - [Item].**
  - Purpose: ...
  - Details: ...

## Changed
**[1] - [Category] - [Item].**
  - Reason: ...
  - Impact: ...

## Fixed
**[1] - [Category] - [Item].**
  - Root cause: ...
  - Resolution: ...

## Notes
- [Testing focus / rollout note / known limitation]

## [PR title - Github PR URL]
```