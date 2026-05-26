# Create PR and Comment Jira

This skill helps you send your code to GitHub and tell the Jira task about it. It does many things in one action.

## What do I need?

Before using this skill, make sure you have:

1. **gh CLI** - GitHub command-line tool, installed and logged in
2. **Jira MCP** - connection to Jira (must be set up)
3. **`.env` file** - create a `.env` file in the repo root with your Jira credentials:
   ```
   JIRA_COMPANY_DOMAIN=saritasa
   JIRA_PROJECT_KEY=RMASUP
   JIRA_EMAIL=john.doe@saritasa.com
   JIRA_API_TOKEN=ATATT3xFfGF0eq6-JnkSzR-Example
   ```
   - `JIRA_COMPANY_DOMAIN` — your Jira subdomain (the part before `.atlassian.net`)
   - `JIRA_PROJECT_KEY` — your project key (e.g. `RMASUP`)
   - `JIRA_EMAIL` — your Atlassian account email
   - `JIRA_API_TOKEN` — API token from https://id.atlassian.com/manage-profile/security/api-tokens

## What does this skill do?

1. Creates a pull request on GitHub with a technical report for future developers
2. Writes a comment on your Jira task with a non-technical summary for testers and PMs
3. Saves progress information for later
4. Shows you a preview before doing anything

It uses two different templates:
- **PR body** - technical (architecture, decisions, risks, reuse patterns)
- **Jira comment** - non-technical (behavior, user impact, testing notes)

## When should I use it?

Use this skill when:
- You finished writing code for a task
- Your code is committed and ready
- You want to create a PR on GitHub
- You want to tell Jira about the PR at the same time
- Your branch name has the task ID in it (like `feature/PROJ-123-add-login`)

## How to run it

Type one of these in Claude Code:

| Command | What it does |
|---------|-------------|
| `/dev-ship` | Create PR + comment Jira (default) |
| `/dev-ship --pr-only` | Create PR only, skip Jira |
| `/dev-ship --jira-only` | Comment Jira only, skip PR |
| `/dev-ship --dry-run` | Preview both changelogs only, no action |
| `/dev-ship --technical-only` | Save technical changelog to `.local` only |
| `/dev-ship [KEY]` | Use a specific task key |

The skill will show you what it will do, then ask you to say "YES" before making changes.

## Important things to know

- Your branch name MUST have the task ID (like `PROJ-123`)
- All your changes must be committed (nothing new uncommitted)
- The PR will be sent to the `develop` branch by default
- You will see a preview and can say NO if something is wrong
- This skill will NOT commit your code, only use what you already committed

## What happens step by step?

1. **Check your code** - looks at what you changed
2. **Get the task ID** - reads it from your branch name
3. **Generate reports** - creates two reports:
   - Technical PR report (for future developers)
   - Non-technical Jira report (for testers and PMs)
4. **Show you a preview** - displays both reports
5. **Ask for permission** - waits for you to say YES
6. **Create the PR** - sends code to GitHub with the technical report
7. **Save progress** - updates `.local/tasks/[KEY]/progress.md`
8. **Comment on Jira** - posts the non-technical report with the PR link

## Examples

### Example 1: Add a login feature

Your branch is: `feature/PROJ-123-add-login`

The skill:
- Takes the task ID: `PROJ-123`
- Reads your changes
- Creates a PR with title: `Add login feature PROJ-123`
- Comments on Jira task `PROJ-123` with the PR link

### Example 2: Fix a bug

Your branch is: `bugfix/PROJ-456-fix-crash`

The skill:
- Takes the task ID: `PROJ-456`
- Reads what you fixed
- Creates a PR with title: `Fix crash PROJ-456`
- Comments on Jira task `PROJ-456` with the PR link

## Future reuse guidance

This section exists in the PR template.

Use it to record whether part of the implementation is safe to copy into future work, what exact pattern is reusable, and what caveat must be checked before reuse.

This helps future engineers and LLMs answer questions like:
- Can we follow the same pattern in a similar task?
- Is this a stable approach or only a one-off workaround?
- What condition must be checked before reusing it?

Write it like this:

```md
## Future reuse guidance
- Safe to copy: [YES / NO / WITH CARE]
- Reusable pattern: ...
- Caveat: ...
```

### When to use it

Use this section when the PR shows a reusable pattern clearly enough, for example:
- Request validation flow
- State handling pattern
- API request shaping
- Mapping logic
- UI interaction flow
- Integration boundary rule
- Permission check pattern

### When not to use it

Do not use this section for:
- Vague advice
- One-off hacks
- Temporary debug code
- Legacy fallback logic that should not spread
- Anything not clearly supported by the PR evidence

### Example: safe to copy

```md
## Future reuse guidance
- Safe to copy: YES
- Reusable pattern: Reuse the same request-validation pipeline for new admin write endpoints.
- Caveat: Keep the same role check and error response shape.
```

Use `YES` when the pattern looks intentional, review-safe, and not tightly coupled to one-off constraints.

### Example: use with care

```md
## Future reuse guidance
- Safe to copy: WITH CARE
- Reusable pattern: Reuse the optimistic UI update pattern for small inline field edits.
- Caveat: Confirm rollback behavior and stale-data handling before applying it to multi-step flows.
```

Use `WITH CARE` when the pattern is probably useful but depends on assumptions, missing verification, or context-specific trade-offs.

### Example: do not copy

```md
## Future reuse guidance
- Safe to copy: NO
- Reusable pattern: Temporary fallback mapping for legacy invoice status values.
- Caveat: This exists only for backward compatibility and should not be used in new flows.
```

Use `NO` when the logic is transitional, workaround-based, legacy-only, or clearly unsuitable as a standard pattern.
