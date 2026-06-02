> **LLM**: Follow this format strictly. Read all instructions below before writing. Do not skip sections, reorder items, or change the output structure.

## Output template

```md
# [[KEY] — PR #[N]](https://github.com/.../pull/123)

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

## Testers
- Start here: ...
- Preconditions: ...
- Test data / account: ...
- API / endpoint / URL: ...
- How to verify: ...
- Known limitation: ...

## Notes
- [Rollout note / no product behavior change / important context]
```

Audience: Testers, PMs, clients.
Purpose: Store a short business-facing history of what changed and how to start testing it.
Rule: Describe behavior and user impact only. No code-level detail.

Tone and style:
- Use simple, short, direct, non-marketing English.
- Do not trim away core or important details needed for understanding or testing.
- Write for testers, PMs, and clients.
- Focus on user-visible behavior and impact, not implementation details.
- Prefer durable domain terms over temporary implementation labels.
- Use past tense.

## Source priority
1. Jira task title and description.
2. Acceptance criteria or business notes.
3. PR title and PR body.
4. Commit messages.
5. Local code changes and diff, but only to confirm visible behavior and testing entry points.

## Core rules
- Extract. Do not invent.
- Prefer explicit business context from Jira over inference from code.
- Use code changes only to confirm what behavior changed and how testers can access it.
- If a detail is unclear and not important to testers, omit it.
- Group small technical edits into one meaningful user-facing change.
- Use stable categories such as feature area, workflow, API, validation, permissions, notifications, reporting, sync, or UI.
- Do not use file names, class names, function names, or vague categories like `Misc`.
- Do not mention variable names, function names, class names, file paths, method names, database tables, or internal implementation mechanics.
- Omit empty sections.

## Section rules
- Added: New user-visible capability or new stakeholder-visible workflow only.
- Changed: Existing behavior, workflow, wording, validation, or UX changed.
- Fixed: Previous behavior was wrong and is now corrected. Write root cause in plain business language only.
- Testers: Give only the minimum practical information needed to begin testing. Include entry URL, API route, request example, feature flag, account, environment, seed data, or manual setup only when they are required to test the task.
- Notes: Only rollout note, limitation, dependency note, or “no product behavior change” note.

## Tester rules
- Include `API / endpoint / URL` only when testers need it to execute or validate the task.
- Include example request shape only when the task introduces or changes an API and the request is not obvious from the Jira description.
- Include credentials, account type, role, seed data, feature flag, or environment name only when needed for testing.
- If there are multiple ways to test, prefer the shortest reliable path.
- If testing cannot start without another task, environment, or dependency, say that clearly.
- Do not dump raw curl commands, payloads, or internal implementation details unless they are the only practical way for testers to start.
- If no special setup is needed, write: `- Start here: No special setup required.`

## Omit rules
- Omit any item that is only about internal refactor, docs-only cleanup, template path changes, placeholder variable changes, or generated artifacts.
- Omit technical implementation details even if they appear in commits or diff.
- If the task changes internal workflow only, say that clearly in Notes instead of pretending there is product impact.
- If unclear, omit rather than guess.