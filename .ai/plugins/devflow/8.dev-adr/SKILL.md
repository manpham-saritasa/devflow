---
name: dev-adr
description: Create an ADR for a completed Jira task from task folder evidence, based on the repository ADR template. Only creates ADRs for architectural or cross-cutting decisions.
triggers:
  - "dev-adr"
  - "adr"
  - "create-adr"
---

## Paths

Read shared paths from `config.md`.
---

## Decision Triggers

Only create an ADR when the task introduced one or more of:

- New third-party service or external API
- New library/package introducing a new capability or pattern
- Existing technical approach replaced
- Database schema or persistence strategy changed
- Auth flow, permission boundary, or trust boundary changed
- Significant module boundary, integration contract, background processing, or deployment change

If none apply: stop — "No ADR needed for this task."

---

## Workflow

### Step 1: Parse Input

- Extract `KEY` from user input (regex: `([A-Z0-9]+-\d+)`, case-insensitive).
- If no KEY: `git branch --show-current`, extract KEY.
- If still no KEY: ask user. Stop if none provided.

### Step 2: Gather Evidence

**If `TASK_DIR` is missing or incomplete:** run `dev-get [KEY]` to fetch Jira context in-memory. Do not persist raw.md or task.md. Then search for merged PRs as additional evidence.

Read all available files from `TASK_DIR/`. Missing files are not errors.



**When `TASK_DIR` is missing or incomplete:** search for merged PRs:
```bash
gh search prs "[KEY]" --merged --json number,title,url,headRepository
```
Fetch PR details and diff:
```bash
gh pr view [NUMBER] --repo [OWNER]/[REPO] --json title,body,commits,files
gh pr diff [NUMBER] --repo [OWNER]/[REPO]
```

Also read repository context: `AGENTS.md`, `README.md`, `docs/`, and existing ADRs in `ADR_DIR`.

### Step 3: Analyze

Check `templates/adr-template.md` exists next to this skill. Missing → stop: "Error: ADR template not found."

Read existing ADRs in `ADR_DIR` to:
- Match naming conventions
- Avoid duplicate ADRs for the same decision
- Understand related decisions

**Decision analysis:**
- Base the ADR on the decision actually implemented (not an idealized alternative)
- Prefer repository evidence over plan/changelog claims when they conflict
- If evidence is incomplete, use best-supported conclusion and note uncertainty
- Derive ADR title from the decision itself, not Jira summary

**Skip if:**
- No architectural decision found → "No ADR needed for this task."
- Duplicate ADR exists → report the overlap and existing ADR path
- Task is cosmetic UI, copy edits, trivial refactors, tests-only, or config-only tweaks

### Step 4: Write ADR

Write to `ADR_DIR/[KEY]-[short-decision-summary].md` using kebab-case.

- Use `templates/adr-template.md` exactly — fill every section, replace all placeholders
- Default status to `Accepted` when work is already merged
- Use today's date
- Use concrete repository terms: real services, modules, interfaces, schemas
- Never invent technical details not supported by evidence

If there are open questions that need answers, show them in the chat window after the report — do not include them in the ADR file.

**Section 9 — Supporting Evidence** — omit sub-items that have no content:

```
- **Task evidence:** [omit this line if no task evidence]
- **PR evidence:** [omit this line if no PRs]
- **Related ADRs / prior tasks:** [omit this line if none, or write `None`]
- **External references:** [omit this line if no external sources]
```

### Step 5: Report Result

```
✅ ADR created: docs/adrs/[KEY]-[summary].md

Decision: [1-2 bullet summary]

Evidence used:
- [key files and PRs with clickable URLs]

Tradeoffs:

Open questions:
- [list questions that need answers, or "None"]
- [major tradeoffs, risks, follow-ups — or "None"]
```

---

## Self-Check

Before finalizing, verify:
- [ ] Open questions shown in chat, not in the ADR file?
- [ ] ADR reflects the decision actually implemented?
- [ ] Used the repository ADR template exactly?
- [ ] All placeholders replaced with real summaries?
- [ ] Section 9 has clickable markdown links for Jira and all relevant PRs? Empty sub-items omitted?
- [ ] No ADR created when no architectural decision exists?
- [ ] Filename matches `[KEY]-[short-decision-summary].md` in kebab-case?
- [ ] Existing ADRs checked for duplicates?
