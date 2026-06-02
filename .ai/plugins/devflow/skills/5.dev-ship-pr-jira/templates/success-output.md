# Success Output

Show the final result in separate blocks so URLs and posted content are easy to copy.

(Omit skipped blocks per flags.)

## New PR Created

```text
✅ PR: {PR_URL}
✅ Progress: .local/tasks/[KEY]/plan.md
```

```md
## PR Body Posted
[exact PR body that was posted]
```

```md
## Jira Comment Posted
[exact Jira comment that was posted]
```

## Existing PR Reused

```text
✅ PR reused: {PR_URL}
✅ PR comment added with recent changes summary
✅ Progress: .local/tasks/[KEY]/plan.md
```

```md
## PR Comment Posted
[exact PR comment that was posted]
```

```md
## Jira Comment Posted
[exact Jira comment that was posted]
```

## --from-pr

```text
✅ Reports generated from PR: {PR_URL}
```

```md
## PR Report
[exact PR report]
```

```md
## Jira Report
[exact Jira report]
```

## --no-jira (New PR)

```text
✅ PR: {PR_URL}
✅ Progress: .local/tasks/[KEY]/plan.md
```

```md
## PR Body Posted
[exact PR body that was posted]
```

## --no-jira (Existing PR)

```text
✅ PR reused: {PR_URL}
✅ PR comment added with recent changes summary
✅ Progress: .local/tasks/[KEY]/plan.md
```

```md
## PR Comment Posted
[exact PR comment that was posted]
```

## --jira-only

```text
✅ Jira: [KEY] commented
✅ Progress: .local/tasks/[KEY]/plan.md
```

```md
## Jira Comment Posted
[exact Jira comment that was posted]
```

## --technical-only

```text
✅ Progress: .local/tasks/[KEY]/plan.md
```

```md
## Technical Changelog (.local)
[exact changelog content written]
```
