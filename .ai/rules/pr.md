# Github PR fixing rules

> Always confirm changes before applying them.

## Category Legend

| Category | Step | Meaning |
|----------|------|---------|
| 🔴 Open | §1, §2 | Not yet resolved — needs a fix or discussion |
| 🔧 Fixed | §3, §4 | Code changed locally, not yet pushed or resolved on PR |
| ✅ Resolved | §4 | Pushed to origin and comment resolved on PR |
| 💬 Replied | §4 | Conversation reply pushed to PR (no code change) |
| 🔒 Kept | §4 | Comment acknowledged but no change made |

**Overlap rule:** If a comment led to both a code change and a reply, use the code change status (🔧 Fixed or ✅ Resolved). Code change supersedes reply.

**Kept rule:** If a human has already replied to the thread with a decision to defer or keep (e.g., "Keep it for now"), mark it as 🔒 Kept — not 🔴 Open.

## Priority Ordering

For §1 and §2 (listing and planning), use 🔴 Open for all unresolved comments.
For §4 (review), use the resolved categories: 🔧 Fixed → ✅ Resolved → 💬 Replied → 🔒 Kept.
Within the same category, order by file path alphabetically.

## 1. List comments step
When asked about any comments unresolved or unanswered in the PR:
- Reread to get the answer from the PR
- Order all comments by priority from top to bottom
- Show all comments in a table format with these columns: category, commented file (file name as clickable URL to the comment using `/files#r{id}` format, e.g., `https://github.com/org/repo/pull/123/files#r456`), who commented, comment's content.

## 2. Planning step
When reviewing changes for fixing comments in a PR:

- **Easy fix**: Single-line change, typo, rename, or already resolved in a later commit. Auto-propose these.
- **Non-trivial**: Logic change, new file creation, deletion, multi-file change, or anything ambiguous. Ask me one by one.
- List all comments by priority from top to bottom in a table format with these columns: category, commented file (file name as clickable URL using `/files#r{id}` format), who commented, comment's content, the change proposed.

## 3. Fixing step

### Changing code
When applying the changes for comments that need code changes:
- Always show me the diff before committing. Do not commit silently.
- If a single comment fix involves multiple files, group them into one commit.
- If a single comment fix involves only one file, group it with other similar fixes, but maximum 3 files per commit. Exception: bulk identical changes (e.g., typos, renames across many files) can go in one commit.
- For multi-fix commits, list each fix as a bullet in the commit body (not just the JIRA key in the subject).
- Use commit message format: `[Task summary] #[JIRA Task KEY]` (e.g., `Fix PR comments #PROJ-2050`).
- Commit on local only, do not push to origin automatically, unless I order you to do so.

### Resolving code-fix comments
After pushing the code fix to origin:

1. Before pushing, show me a list of which PR comment threads will be resolved so I can approve or adjust.
2. After I approve, push and resolve each thread silently. Do not add a reply — just mark it resolved.
3. Only add a reply if there is an important note or breaking change to call out.

**How to resolve:** Use the GraphQL `resolveReviewThread` mutation.

Find unresolved thread IDs:
```sh
gh api graphql -f query='query { repository(owner:"org", name:"repo") { pullRequest(number:N) { reviewThreads(first:50) { nodes { id isResolved } } } } }'
```

Resolve a thread silently:
```sh
gh api graphql -f query='mutation { resolveReviewThread(input: {threadId: "ID"}) { thread { isResolved } } }'
```
Note: posting a reply to a thread also auto-resolves it — use the GraphQL mutation only when you want a silent resolve without a reply. If you add a reply for an important note, skip the mutation — the reply handles it.

### Replying comments
For comments that need a reply to resolve or discuss (does not need a code change yet):
1. Show me the exact reply content in the §4 review table before pushing.
2. After I approve, push the reply to the PR. Do not resolve the comment thread — only the reply. I will resolve conversations myself in the PR UI.

## 4. Reviewing step
After done fixing the comments in step #3, show result for me to review all changes you made.

- For code changes, list them in priority order, in a table format with these columns: category, commented file (file name as clickable URL using `/files#r{id}` format), who commented, comment's content, file diff / change summary.

- If a single comment fix spans multiple files, list each file on its own line within the same row, using compact inline diff per file (e.g., `file1.cs: old → new`, `file2.cs: deleted`). Do not create separate rows for the same comment.

- For comments' replies, list them in priority order, in a table format with these columns: category, commented file (file name as clickable URL using `/files#r{id}` format), who commented, comment's content, the reply you drafted.

## 5. Closure step
After reviewing the tables in step #4, I will tell you to:
- Amend a commit
- Push to origin (after push, resolve code-fix threads silently; do not resolve reply threads)
- Make further changes

Do not proceed until I give one of these instructions.

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Comment on a deleted file | Reply with the reason for deletion; no code change needed |
| Duplicate Copilot comments (re-review cycle) | Group duplicates into one row; note "Duplicate of #N" |
| Existing replies in the thread | Skip — already resolved; list as 🔒 Kept if no further action needed |
| Copilot bot comment (no human follow-up) | Still fix if valid; no reply needed unless a human also flagged it |
| Comment on a line that no longer exists in HEAD | Use the original commit ID and line from the comment's diff hunk |
| Thread already marked `isResolved: true` on GitHub | Mark as ✅ Resolved — no action needed |
