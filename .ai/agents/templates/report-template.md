# Report Template

Lightweight reporting format for GitHub PR body and Jira task comments.
Reuses the core sections from `changelog-template.md` — drop the operational
detail (Verification, Deferred, Files Touched) and keep what reviewers and
stakeholders actually need to read. 

---

## [KEY] — [Title]

**Important**: Write everything in plain, human-readable language for testers, PMs, and clients. Avoid technical jargon, implementation details, code-specific terms, and developer-focused explanations.

### Summary
[1-2 sentence description of what was delivered or fixed in this task.]

### Changes
- [implemented change]
- [implemented change]

### Fixes
- [bug fix or regression fix]
- [or `None`]

### Bug Analysis
**[Bug title — omit section entirely if no bugs were fixed]**
- Symptom: [What users or the system experienced]
- Root Cause: [Confirmed cause, or "Best-supported hypothesis:" with uncertainty stated]
- Fix Strategy: [What was changed to address it]
- Regression Risk / Prevention: [Test added, guardrail, follow-up, or `None`]
