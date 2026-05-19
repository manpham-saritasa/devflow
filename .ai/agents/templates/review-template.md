# Task Review

## Task Context
- ID: [JIRA-KEY or task identifier]
- Title: [Task title]
- Repository / Project: [name]
- Review objective: [what this review file covers across the task lifetime]

## Stable Review Criteria
- Fit criteria:
  - Meets task requirements and acceptance criteria.
  - Matches active plan iteration intent and scope.
  - Respects constraints and do-not-modify boundaries.
- Quality criteria:
  - Correctness, maintainability, test adequacy, safety, and consistency with repository patterns.
- Severity model:
  - `[blocking]` = broken requirement, serious regression risk, security flaw, crash/data-loss risk, or critical invariant violation.
  - `[minor]` = non-blocking maintainability, consistency, readability, or verification issue.

## Notes for Future Iterations
- Keep the sections above stable across the task lifetime.
- Append new review passes below. Do not delete prior passes.
- First review pass usually follows the Jira-driven first iteration; later passes may review work triggered by PR comments, reviewer findings, or direct user instructions.

---

## Review Pass [N] — YYYY-MM-DD HH:MM ±TZ
**Iteration:** [matching iteration number]
**Trigger:** [planned review | PR comments | review follow-up | user request | bug fix validation | other]
**Verdict:** [Pass | Pass with Changes | Fail]

### Fit Check
**Acceptance Criteria Review**
1. [AC or requirement] — [Pass | Partial | Fail] — [evidence]
2. [AC or requirement] — [Pass | Partial | Fail] — [evidence]

**Plan Coverage Review**
1. [Proposed Change title or planned item] — [Pass | Partial | Fail] — [evidence]
2. [Proposed Change title or planned item] — [Pass | Partial | Fail] — [evidence]

**Scope Review**
- Unexpected files changed: [list or `None`]
- Scope drift: [details or `None`]
- Constraints / do-not-modify respected: [Yes/No + notes]

**Fit Issues**
1. [Issue or `None`.]

### Quality Check
1. [[blocking] or [minor]] [Category] — [file:path or area]
   - Details: [what is wrong and why it matters]
   - Suggested fix: [specific next action]
2. [[blocking] or [minor]] [Category] — [file:path or area]
   - Details: [what is wrong and why it matters]
   - Suggested fix: [specific next action]

### Test & Verification Review
- Reviewer checks run: [commands, tests, manual review steps]
- Coverage assessment: [adequate / gaps]
- Verification gaps or regression risk: [details or `None`]

### Changelog Review
- Matches implementation: [Yes/No + notes]
- Missing or misleading entries: [details or `None`]

### Previous Issues Status
- [Resolved / Still open / Deferred / Not applicable]

### ADR Suggestion
- Suggested: [Yes/No]
- Reason: [short reason or `None`]

### Final Recommendation
- [Approve | Approve with Changes | Reject]
- [Required next steps or `None`]
