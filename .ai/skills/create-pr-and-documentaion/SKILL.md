---
name: create-pr-and-documentaion
description: |
  Complete feature shipping workflow: create a GitHub PR, auto-comment the Jira task, and save feature plan + changelog to project knowledge base.

  **When to use:** After finishing a feature/fix and want to ship it in one workflow — creates a clean PR, notifies Jira, and documents the work (plan + changes) in project-knowledge for future reference.

  **Use this skill when:**
  - You have finished a feature and want to open a PR + notify Jira + save project knowledge
  - You want a clean, one-line commit message (e.g., "Complete feature [JIRA_PROJECT]-1234")
  - You want to track all changes and implementation details in project-knowledge for the team
  - You want the PR body, Jira comment, and changelog to match exactly
  - You want to auto-extract task ID from your current branch name
---

## Paths

- DEV_ROOT: `.local`
- TASK_DIR: `[DEV_ROOT]/tasks/[KEY]` — replace [KEY] with the extracted Jira ticket key
- CHANGELOG_TEMPLATE: `.ai/agents/templates/changelog-template.md`
- REPORT_TEMPLATE: `.ai/agents/templates/report-template.md`
- PROGRESS_TEMPLATE: `.ai/agents/templates/progress-template.md`

> **Template usage:**
> - `CHANGELOG_TEMPLATE` — full format for `.local/tasks/[KEY]/changelog.md` (dev-agent internal, includes Verification, Files Touched, etc.)
> - `REPORT_TEMPLATE` — lightweight format for **PR body, Jira comment, and project-knowledge changelog** (Summary + Changes + Fixes + Bug Analysis only)
>
> Files from the dev-agent workflow (dev-planner → dev-coder → dev-reviewer) live under TASK_DIR and are preferred inputs when available.

## Variables
- JIRA_DOMAIN: Use environment variable $JIRA_DOMAIN (or based on AI tools)
- JIRA_PROJECT: Use environment variable $JIRA_PROJECT (or based on AI tools)
---

## Workflow

### Step 1: Check Uncommitted Changes

Run `git status --short` to detect uncommitted files.

If uncommitted files exist:
- Show the list to the user
- Ask: "These files are uncommitted and will NOT be included in the PR. Do you want to commit them first, or skip and proceed without them?"
  - **Commit first**: Stop here and wait for the user to commit. Restart the skill after.
  - **Skip**: Continue with the current committed state.

Do NOT auto-commit or auto-stage anything.

### Step 2: Extract Task ID

Run `git branch --show-current` and extract the task ID using regex `([A-Z0-9]+-\d+)` (e.g., `[JIRA_PROJECT]-1234`).

If extraction fails:
- Ask the user to provide the task ID or a full Jira link.
- Extract from the link if provided.
- Do not proceed without a valid task ID.

Set `[KEY]` = extracted task ID (e.g., `[JIRA_PROJECT]-1234`).

### Step 3: Extract Report Content

This step produces content for the PR body, Jira comment, and project-knowledge changelog.
Read `REPORT_TEMPLATE` to understand the target format: Summary, Changes, Fixes, Bug Analysis.

**Priority order:**

1. **Check `TASK_DIR/changelog.md`** (created by dev-coder agent):
   - If it exists, read the latest iteration section.
   - From that section, extract: Summary, Changes, Fixes, Bug Analysis.
   - Ignore the dev-coder-only sections (Verification, Deferred, Files Touched) — those are internal detail, not needed in the report.

2. **If no changelog.md exists**: Auto-extract from git:
   - Run `git diff develop..HEAD` to analyze changes.
   - From diff and commit messages, populate `REPORT_TEMPLATE` sections:
     - **Summary**: 1-2 sentence description of what was delivered
     - **Changes**: list of implemented changes
     - **Fixes**: bug fixes or corrections (or `None`)
     - **Bug Analysis**: if a bug was fixed, fill Symptom / Root Cause / Fix Strategy / Regression Risk (omit section if no bugs)

### Step 4: Build Commit Message

Format: `{action} {description} [KEY]`

Derive the action and description from the changes or branch name. Keep it concise and meaningful.

Examples:
- `Fix PDF landscape scaling [JIRA_PROJECT]-1234`
- `Add signature persistence for PDF forms [JIRA_PROJECT]-2017`
- `Complete user permissions feature [JIRA_PROJECT]-1234`

### Step 5: Show User What Will Be Created

Display a preview using `REPORT_TEMPLATE` format (this is what goes into PR body and Jira comment):

```
Commit Message:
  Fix PDF landscape scaling [JIRA_PROJECT]-1234

Report ([KEY]):

## [KEY] — [Title]

### Summary
[1-2 sentence summary of what was delivered]

### Changes
- [implemented change]
- [implemented change]

### Fixes
- [bug fix, or `None`]

### Bug Analysis
**[Bug title — omit if no bugs fixed]**
- Symptom: ...
- Root Cause: ...
- Fix Strategy: ...
- Regression Risk / Prevention: ...

---

Actions:
1. Create PR on GitHub (base: develop)
2. Update .local/tasks/[KEY]/progress.md with PR status
3. Comment on [KEY] (PR URL + changelog content)
```

**Ask for confirmation: "Ready to ship? Say YES to proceed."**

### Step 6: Create GitHub PR

Once user confirms, run:
```bash
git push origin $(git branch --show-current)
gh pr create \
  --base develop \
  --head $(git branch --show-current) \
  --title "{COMMIT_MESSAGE}" \
  --body "{PR_BODY}"
```

Where `{PR_BODY}` is the full changelog content from Step 3/5 in `CHANGELOG_TEMPLATE` format.

Capture the PR URL from the output.

### Step 7: Update Progress

Update `TASK_DIR/progress.md` to record that the PR was shipped:

- If `TASK_DIR/progress.md` exists: append a new entry using `PROGRESS_TEMPLATE` format:
  ```
  ## Iteration [N] — YYYY-MM-DD HH:MM ±TZ
  - Trigger: PR created
  - Status: Shipped
  - Summary: PR created at {PR_URL}
  - Files: changelog.md
  - Next Action: Await review / merge
  - ADR Suggested: No
  ```
- If it doesn't exist: create it using `PROGRESS_TEMPLATE` with the above content.

This keeps the dev-agent workflow timeline consistent — future dev-planner or dev-reviewer runs will see that a PR was opened.

### Step 8: Comment on Jira Task

Use Jira MCP to post the full PR body as a comment on the task:

```
cloudId: [JIRA_DOMAIN]
issueIdOrKey: [KEY]
commentBody: PR: {PR_URL}\n\n{FULL_PR_BODY}
contentFormat: markdown
```

### Step 9: Success Message

Show:
```
✅ PR created: {PR_URL}
✅ Progress updated: .local/tasks/[KEY]/progress.md
✅ Jira task [KEY] commented
```

---

## Important Notes

- **Env vars**: Uses `[JIRA_DOMAIN]` and `[JIRA_PROJECT]`
- **Report format** (PR body + Jira + project-knowledge): Always read `REPORT_TEMPLATE` at runtime — Summary, Changes, Fixes, Bug Analysis only
- **Changelog format** (`.local/tasks/[KEY]/changelog.md`): Full `CHANGELOG_TEMPLATE` — internal dev-agent detail, not used for reporting
- **PR base branch**: Always `develop` (or ask user if different)
- **Agent integration**: Prefer content from `TASK_DIR/` when available — it was produced by structured agents and is more reliable than git-only extraction
- **Authentication**: Requires `gh` CLI authenticated + Jira MCP authenticated

---

## Example Workflow

**Scenario A — Full agent workflow (dev-planner + dev-coder ran first):**
- `TASK_DIR/changelog.md` exists → read latest iteration for PR body
- PR body = structured content from dev-coder's changelog
- `TASK_DIR/progress.md` updated with Shipped status + PR URL

**Scenario B — No prior agent artifacts:**
- No `TASK_DIR/` files found
- Changelog: auto-extract from `git diff develop..HEAD`
- PR body = extracted content formatted per `CHANGELOG_TEMPLATE`

**Result in both cases:**
```
✅ PR created: {PR_URL}
✅ Progress updated: .local/tasks/[KEY]/progress.md
✅ Jira task [KEY] commented
```
