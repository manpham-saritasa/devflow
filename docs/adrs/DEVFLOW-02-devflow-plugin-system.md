# ADR: Standardize AI-Assisted Development with Devflow Plugin System

**Status:** ACCEPTED
**Task URL:** [DEVFLOW-02](https://github.com/quansaritasa/devflow)
**Date:** 2026-06-02

***

## 1. Current Context

AI coding assistants (Copilot, Claude, Cursor) enable rapid code generation, but without structure, output is inconsistent across sessions, team members, and projects. Team needed a reusable, auditable workflow that works across repositories.

| Area                         | Details                                  |
| ---------------------------- | ---------------------------------------- |
| Task goal                    | Create a consistent AI-assisted development workflow sharable across the team. |
| Change trigger               | Multiple projects needed the same AI workflow patterns — copy-pasting skills was unsustainable. |
| Relevant constraints         | Must work across repos without project-specific config. Must support existing gitflow workflow. |
| Existing pattern or baseline | Manual .md file copy + ad-hoc coding prompts. No versioning or sync. |

***

## 2. Chosen Direction

- **Plugin-based skill system with agent orchestration and cross-project sync.**
- Skills are self-contained markdown files organized into plugins (devflow, refflow, jiraflow, githubflow).
- Templates and configs live with their owning skills, not in shared folders.
- One-way sync script mirrors `.ai/` to multiple projects via `robocopy`.
- Agent auto-detects task progress and runs appropriate skills.

***

## 3. Decision Scope

| Scope Type   | Details                                      | Client-friendly explanation    |
| ------------ | -------------------------------------------- | ------------------------------ |
| In scope     | Devflow plugin (start → plan → code → review → ship → finish), refflow plugin (structure refactoring), jiraflow (Jira integration), githubflow (PR management), md converters, review tools. | "We built a reusable AI workflow toolkit." |
| Out of scope | Project-specific business logic. IDE-specific integrations beyond Zed/Cursor/Copilot. | "We didn't build custom project code." |
| Assumptions  | Team uses Git, Jira, GitHub. AI tools support markdown-based skill instructions. | "We assumed the team's existing tool stack." |

***

## 4. Decision Reasons

#### Main reasons

- **Skills are versioned, tested, and syncable** — unlike ad-hoc prompts that die with the chat window.
- **Agent auto-orchestration** reduces human decision fatigue per task.
- **Plugin architecture** keeps concerns separated (devflow vs refflow vs utilities).
- **Single source of truth** via `config.md` per plugin, no duplicated paths.

#### Why it fits the current architecture or team direction?

| Category                   | Reason              | Client-friendly explanation    |
| -------------------------- | ------------------- | ------------------------------ |
| Maintainability            | Skills are plain .md — anyone can edit, review, PR | "We can update our workflows like code." |
| Reusability                | One sync script mirrors to all projects | "We write it once, use everywhere." |
| Audit trail                | plan.md, changelog.md, review.md per task | "Every task has a paper trail." |
| Onboarding                 | startup.md + skills-index.md discovers all capabilities | "New team members see the full toolkit immediately." |

#### Why it is better than the likely alternatives for this case?

| Summary                    | Reason              | Client-friendly explanation    |
| -------------------------- | ------------------- | ------------------------------ |
| Vs raw AI coding (vibe)    | No structure, no audit, no team sharing. Skills die with prompt. Devflow persists everything. | "Raw AI coding is fast but messy." |
| Vs SpecKit / BMAD          | Heavy spec overhead per task. Rigid format. Devflow is lightweight — plan.md per task, self-grill, optional. | "Spec systems add complexity we don't need." |
| Vs copy-paste workflows    | Git tracks skills. Sync script propagates changes. No manual copy errors. | "Automated sync saves hours of manual copying." |

***

## 5. Options Considered

| Option                                     | Benefits             | Tradeoffs         | Client-friendly explanation    |
| ------------------------------------------ | -------------------- | ----------------- | ------------------------------ |
| **Option 1 — Devflow plugin system**       | Reusable, versioned, syncable, agent-driven. | Upfront setup cost (creating skills). Learning curve. | "We built a reusable AI toolkit." |
| Option 2 — Raw AI coding per task | Zero setup. Fast for one-off tasks. | No consistency. No team sharing. No audit trail. | "Quick but messy — doesn't scale to a team." |
| Option 3 — SpecKit / BMAD         | Structured. Spec-driven. | Heavy overhead per task. Rigid. Doesn't fit all task types. | "Too much process for our needs." |

***

## 6. Change Impact

| Area                 | Impact                                                    |
| -------------------- | --------------------------------------------------------- |
| Code impact          | `.ai/` folder added to repos. `sync.bat` for propagation. |
| Data / schema impact | None. |
| Security impact      | Secrets in `.env.local` (gitignored). Agent reads skill files only. |
| Performance impact   | None. |
| Operational impact   | Team runs `sync.bat` after devflow updates. Skills versioned via git. |
| Testing impact       | `test_structure.py` validates skill file integrity. |

***

## 7. Expected Outcomes

| Area           | Details                                                | Client-friendly explanation    |
| -------------- | ------------------------------------------------------ | ------------------------------ |
| Benefits       | Consistent AI workflow across projects. Shorter onboarding. Reusable skills. | "Our AI assistant works the same everywhere." |
| Tradeoffs      | Skills need maintenance. New team members must learn skill structure. | "Skills need updating like any codebase." |
| Follow-up work | Integrate sync into CI. Add more plugins (build, deploy). | "We'll automate sync in the future." |
| Risks          | AI model changes may require skill rewrites. Plugin coupling if not carefully maintained. | "AI tools evolve fast — we may need updates." |

***

## 8. Pending Items

| Type                 | Details                                                                       |
| -------------------- | ----------------------------------------------------------------------------- |
| Pending validations  | Team adoption feedback. Sync script reliability over 100+ files. |
| Pending dependencies | None. |
| Deferred decisions   | CI/CD integration. Plugin for cloud deployment. Central skill registry. |

***

## 9. Supporting Evidence

- **Task evidence:** DEVFLOW-01 (initial workflow), DEV-9 through DEV-17 (iterative refinement), RMASUP tasks (field testing).
- **PR evidence:** 1688abc Rename refactorflow → refflow, 655d2c7 Add multi-target sync script, 1d87f1a Fix jiraflow ROOT path, 76ebfb9 Fix cross-plugin paths and refactor jira-move config.
- **Related ADRs / prior tasks:** DEVFLOW-01-standardized-development-workflow (predecessor).
- **Additional references:** [Zed Agent Skills](https://zed.dev/docs/assistant/ai-agent-skills), [Cursor Rules](https://docs.cursor.com/context/rules-for-ai), [GitHub Copilot Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions).
