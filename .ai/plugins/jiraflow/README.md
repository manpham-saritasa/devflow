# Jiraflow Plugin

JIRA workflow skills for task management and release operations.

## Structure

```
jiraflow/
  config.md                   ← shared transitions and milestones
  skills/
    jira-urgent/              ← list tasks waiting on your reply
    jira-mine/                ← list your assigned tasks
    jira-comment/             ← post a comment to a JIRA issue
    jira-move/                ← transition issue between statuses
    release-add/              ← add task(s) to a JIRA release version
    release-note/             ← generate client-friendly release notes
```

## Skills

| # | Skill | Benefits | Example |
|---|-------|----------|---------|
| 1 | `jira-mine` | List your assigned tasks, ordered by priority | `jira-mine` or `jmine` |
| 2 | `jira-urgent` | Find tasks where team is waiting on you | `jira-urgent` |
| 3 | `jira-comment` | Post comment to JIRA issue | `jira-comment PROJ-123` |
| 4 | `jira-move` | Transition issue between statuses | `jira-move PROJ-123 "In Review"` |
| 5 | `release-add` | Add task to JIRA release version | `release-add PROJ-2143 "API next version"` |
| 6 | `release-note` | Generate client-facing release note | `release-note "API next version"` |
