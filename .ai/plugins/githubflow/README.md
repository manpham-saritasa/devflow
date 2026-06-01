# Githubflow Plugin

GitHub release workflow skills for preparing and managing releases.

## Structure

```
githubflow/
  release-list/               ← list tasks pending release (develop → main)
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
