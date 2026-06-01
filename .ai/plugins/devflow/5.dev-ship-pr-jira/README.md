# Create PR and Comment Jira

This skill helps you send your code to GitHub and tell the Jira task about it. It does many things in one action.

## What do I need?

Before using this skill, make sure you have:

1. **gh CLI** - GitHub command-line tool, installed and logged in
2. **Jira MCP** - connection to Jira (must be set up)
3. **Jira credentials** — in `.env` or `.env.local` at repo root:

   ```
   JIRA_COMPANY_DOMAIN=saritasa
   JIRA_PROJECT_KEY=PROJ
   JIRA_EMAIL=john.doe@saritasa.com
   JIRA_API_TOKEN=ATATT3xFfGF0eq6-JnkSzR-Example
   ```
   - `JIRA_COMPANY_DOMAIN` — your Jira subdomain (the part before `.atlassian.net`)
   - `JIRA_PROJECT_KEY` — your project key (e.g. `PROJ`)
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
7. **Save progress** - updates `.local/tasks/[KEY]/plan.md` progress section
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
