---
name: dev-adr
description: Create an ADR for a completed Jira task from task folder evidence, based on the repository ADR template. Only creates ADRs for architectural or cross-cutting decisions.
triggers:
  - "dev-adr"
  - "adr"
  - "create-adr"
---

## Paths

Read shared paths from `config.md`. All `TASKS_ROOT`, `TASK_DIR`, and `ADR_DIR` variables are defined there.

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

Read from `TASK_DIR` when present:
- `task.md` — requirements and constraints
- `raw.md` — Jira description, comments, implementation notes
- `plan.md` — intended implementation direction
- `changelog.md` — delivered implementation summary
- `review.md` — quality concerns, tradeoffs, corrections
- `progress.md` — task timeline and state
- `pr.md` — shipped scope, PR links

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

**Section 9 — Supporting Evidence** must use clickable markdown links:

```
- **Jira:** [KEY](https://[domain].atlassian.net/browse/KEY) — short summary.
- **PR evidence:**
    - [PR #N](https://github.com/owner/repo/pull/N) — description.
- **Task files:** list files actually used.
- **Related ADRs:** [ADR-001](docs/adrs/adr-001.md) — related decision, or `None`.
```

### Step 5: Report Result

```
✅ ADR created: docs/adrs/[KEY]-[summary].md

Decision: [1-2 bullet summary]

Evidence used:
- [key files and PRs with clickable URLs]

Tradeoffs:
- [major tradeoffs, risks, follow-ups — or "None"]
```

---

## Self-Check

Before finalizing, verify:
- [ ] ADR reflects the decision actually implemented?
- [ ] Used the repository ADR template exactly?
- [ ] All placeholders replaced with real summaries?
- [ ] Section 9 has clickable markdown links for Jira and all relevant PRs?
- [ ] No ADR created when no architectural decision exists?
- [ ] Filename matches `[KEY]-[short-decision-summary].md` in kebab-case?
- [ ] Existing ADRs checked for duplicates?
