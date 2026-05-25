# PR Feedback Template

> **LLM**: Follow this format strictly. Extract every actionable review comment. Group by file. Preserve exact reviewer quotes when relevant. Do not invent feedback not present in the PR.

## Source

- **PR:** [PR #[N]](https://github.com/owner/repo/pull/N)
- **Task:** [KEY](https://domain.atlassian.net/browse/KEY)
- **Branch:** `head-branch-name` → `base-branch-name`
- **State:** [OPEN | MERGED | CLOSED]
- **Fetched:** YYYY-MM-DD HH:MM ±TZ

---

## Review Summary

- **Total review threads:** [N]
- **Blocking / must-fix:** [N]
- **Suggestions / nice-to-have:** [N]
- **Resolved:** [N]
- **Unresolved:** [N]

---

## Feedback by File

### `path/to/file1.ts`

| # | Reviewer | Severity | Status | Comment |
|---|----------|----------|--------|---------|
| 1 | @reviewer | blocking | unresolved | [Exact quote or summary of the review comment.] |
| 2 | @reviewer | suggestion | resolved | [Exact quote or summary of the review comment.] |

**Context (diff snippet or surrounding code):**

```
[relevant code context if available]
```

---

### `path/to/file2.ts`

| # | Reviewer | Severity | Status | Comment |
|---|----------|----------|--------|---------|
| 1 | @reviewer | blocking | unresolved | [Exact quote or summary of the review comment.] |

**Context (diff snippet or surrounding code):**

```
[relevant code context if available]
```

---

## Unresolved Items (Action Required)

| # | File | Reviewer | Comment |
|---|------|----------|---------|
| 1 | `path/to/file.ts` | @reviewer | [Comment summary] |
| 2 | `path/to/file.ts` | @reviewer | [Comment summary] |

---

## Resolved Items (For Context)

| # | File | Reviewer | Comment |
|---|------|----------|---------|
| 1 | `path/to/file.ts` | @reviewer | [Comment summary — already addressed.] |

---

## Reviewer Notes

- **@reviewer1:** [Any overall review summary or approval status.]
- **@reviewer2:** [Any overall review summary or approval status.]
