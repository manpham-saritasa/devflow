# Githubflow Plugin

GitHub release workflow skills for preparing and managing releases.

## Structure

```
githubflow/
  skills/
    create-pr/                ← create or reuse GitHub PR
    fix-pr/                   ← fix PR review comments
    release-list/             ← list tasks pending release
    review-pr/                ← review any PR across dimensions
```

## Skills

| # | Skill | Benefits | Example |
|---|-------|----------|---------|
| 1 | `release-list` | List tasks on develop not on main, PR summaries, JIRA links | `release-list` |

## Usage

```
release-list
```

Shows all tasks pending release from `develop` to `main`, newest first, with clickable JIRA and PR links.

## Future

- `release-add` — add tasks to JIRA release version (`jiraflow` plugin)
