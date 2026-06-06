# ADR: Standardized Development Workflow with Automated Tooling

**Repo:** [devflow](https://github.com/quansaritasa/devflow)
**Date:** 2026-06-01

---

## 1. Current Context

| Area | Details |
|------|---------|
| Task goal | Define and formalize the team's development workflow from Jira task creation to production. |
| Change trigger | Existing workflow was manual and inconsistent — no enforced planning, review, or traceability. |
| Relevant constraints | Workflow must work with Jira, GitHub, and gitflow branching. Must support both single-task and parallel-task modes. |
| Existing pattern or baseline | Ad-hoc "vibe coding" — developers code directly without structured planning, self-review, or standardized commit conventions. |

---

## 2. Chosen Direction

- Adopt the devflow plugin for the full task lifecycle: start → plan → code → review → ship → fix → finish → document.
- Adopt the jiraflow plugin for daily Jira operations: task listing, urgent item detection, milestone transitions, and time logging.
- Document the entire workflow in a Standard Operating Procedure (`docs/sop.md`) that every team member follows.

---

## 3. Decision Scope

| Scope Type | Details | Client-friendly explanation |
|------------|---------|----------------------------|
| In scope | Full task lifecycle automation, Jira status sync, PR process, commit conventions, team SOP. | Every developer follows the same steps for every task. |
| Out of scope | CI/CD integration (future), team dashboard, non-Jira projects. | CI checks and team-wide views are separate work. |
| Assumptions | Developers have `gh` CLI, Jira API access, and AI tooling that reads SKILL.md files. | Standard developer setup. |

---

## 4. Decision Reasons

#### Main reasons

- Ad-hoc coding has no traceability, safety, or institutional memory. The devflow plugin provides checkpoints at every destructive step, a full changelog trail, and preserved task folders as completed-work snapshots.
- The jiraflow plugin eliminates manual Jira status updates and daily task hunting — status transitions, urgent item detection, and time logging are all automated.

#### Why it fits the current architecture or team direction?

| Category | Reason | Client-friendly explanation |
|----------|--------|----------------------------|
| Consistency | Every task follows the same 9-stage pipeline with the same commands. | No more per-developer workflow variation. |
| Safety | Checkpoints gate every push, merge, and delete. Dry-run available for destructive ops. | Accidental pushes and merges are blocked. |
| Traceability | `changelog.md` + `progress.md` + `review.md` per task = full audit trail. | Every decision and change is recorded per task. |

#### Why it is better than the likely alternatives for this case?

| Summary | Reason | Client-friendly explanation |
|---------|--------|----------------------------|
| Vibe coding | No planning, no review, no changelog. Knowledge walks when developer leaves. | Current way loses information over time. |
| Manual checklist | Checklists are skipped when busy. Automated skills enforce the process. | Tools don't forget steps. People do. |

---

## 5. Options Considered

| Option | Benefits | Tradeoffs | Client-friendly explanation |
|--------|----------|-----------|----------------------------|
| **Option 1 — Automated skills (chosen)** | Enforced consistency, full traceability, auto Jira sync, safety checkpoints. | Requires AI tooling, learning curve for new developers, overkill for tiny fixes. | Tools do the heavy lifting — developers just run commands. |
| Option 2 — Manual checklist | Zero setup, works anywhere. | Skipped under pressure, no enforcement, no automation, no traceability. | Relies on discipline that fades over time. |
| Option 3 — CI/CD-only gates | Catches bugs and broken builds automatically. | Doesn't cover planning, review quality, changelog, or institutional memory. | Only solves the merge gate, not the whole workflow. |

---

## 6. Change Impact

| Area | Impact |
|------|--------|
| Code impact | 11 devflow skills (markdown) + 3 jiraflow skills (Python). No application code changes. |
| Data / schema impact | None. |
| Security impact | Jira credentials stored in `.env.jira` per repo. |
| Performance impact | None. |
| Operational impact | Developers must learn commands from the SOP. Every new repo copies the `.ai/plugins/` folder. |
| Testing impact | Structural tests for SKILL.md validity via `scan.py`. Unit tests for jiraflow Python scripts. |

---

## 7. Expected Outcomes

| Area | Details | Client-friendly explanation |
|------|---------|----------------------------|
| Benefits | Every task has a plan, changelog, review, and preserved folder. Jira stays in sync automatically. | Team moves faster with less manual overhead. |
| Tradeoffs | Small fixes go through the same pipeline. No "quick mode" for 5-minute typo fixes. | Some overhead for tiny tasks. |
| Follow-up work | Integrate CI checks into ship/finish. Add team dashboard. Support non-Jira projects. | More automation coming later. |
| Risks | Adoption depends on developers actually using the commands. AI tooling quality varies. | Process only works if the team follows it. |

---

## 8. Pending Items

| Type | Details |
|------|---------|
| Pending validations | Team adoption rate and feedback after 2-week trial. |
| Pending dependencies | None. |
| Deferred decisions | CI/CD integration (check CI status before merge). Non-Jira project support. Team-wide dashboard. |

---

## 9. References:

- [devflow plugin README](https://github.com/quansaritasa/devflow/blob/main/.ai/plugins/devflow/README.md)
- [SOP document](https://github.com/quansaritasa/devflow/blob/main/docs/sop.md)
