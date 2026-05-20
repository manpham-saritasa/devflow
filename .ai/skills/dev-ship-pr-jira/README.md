# Create PR and Comment Jira

This skill helps you send your code to GitHub and tell the Jira task about it. It does many things in one action.

## What do I need?

Before using this skill, make sure you have:

1. **gh CLI** — GitHub command-line tool, installed and logged in
2. **Jira MCP** — connection to Jira (must be set up)
3. **Environment variables** — these should be set:
   - `JIRA_DOMAIN` — your Jira server address
   - `JIRA_PROJECT` — your project key

## What does this skill do?

1. Creates a pull request on GitHub
2. Writes a comment on your Jira task with the PR link
3. Saves progress information for later
4. Shows you a preview before doing anything

It takes information from your current git branch and your code changes, then creates everything you need to share your work.

## When should I use it?

Use this skill when:
- You finished writing code for a task
- Your code is committed and ready
- You want to create a PR on GitHub
- You want to tell Jira about the PR at the same time
- Your branch name has the task ID in it (like `feature/PROJ-123-add-login`)

## How to run it

Type this in Claude Code:

```
/dev-ship-pr-jira
```

The skill will show you what it will do, then ask you to say "YES" before making changes.

## Important things to know

- Your branch name MUST have the task ID (like `PROJ-123`)
- All your changes must be committed (nothing new uncommitted)
- The PR will be sent to the `develop` branch by default
- You will see a preview and can say NO if something is wrong
- This skill will NOT commit your code, only use what you already committed

## What happens step by step?

1. **Check your code** — looks at what you changed
2. **Get the task ID** — reads it from your branch name
3. **Find your changes** — reads your changelog or git history
4. **Show you a preview** — displays what the PR will look like
5. **Ask for permission** — waits for you to say YES
6. **Create the PR** — sends code to GitHub
7. **Save progress** — writes what happened to a progress file
8. **Comment on Jira** — posts a message with the PR link

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
