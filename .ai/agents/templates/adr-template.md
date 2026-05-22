# ADR Template Instructions

- Condense the text into simple, short, and direct English while keeping all core concepts.
- Do not write like a marketing document with long paragraphs.
- In table, use list format in the cell if needed.
- Record decisions, constraints, pending items, open questions, and impacts clearly.
- Separate what is decided now from what is still pending or out of scope.
- Use `Pending Items` for unresolved validations, dependencies, and deferred decisions.
- Use `Open Questions` only for questions that still need an answer from the client, team, owner, or reviewer.
- Do not use `Open Questions` for technical facts already known but not yet verified; keep those in `Pending Items`.
- Use `Review Guidance` only for future change rules and revisit triggers.
- Do not repeat `Pending Items`, `Impact`, or `Consequences` inside `Review Guidance`.
- Format open questions as `Q1`, `A1`, `Q2`, `A2`, and so on.

# ADR: [Short Decision Title]

**Status:** [PROPOSED | ACCEPTED | SUPERSEDED]
**Task URL:** [JIRA-KEY](https://your-company.atlassian.net/browse/JIRA-KEY)
**Date:** YYYY-MM-DD

***

## 1. Context

| Area                         | Details                                  |
| ---------------------------- | ---------------------------------------- |
| Task goal                    | [What the task needs to achieve.]        |
| Change trigger               | [Why this ADR is needed now.]            |
| Relevant constraints         | [Use list format in the cell if needed.] |
| Existing pattern or baseline | [What exists today.]                     |

***

## 2. Decision

- [State the main decision in 1-3 short bullets.]
- [Describe the chosen approach or boundary.]
- [State any hard rule that future work must follow.]


***

## 3. Decision Scope

| Scope Type   | Details                                      |
| ------------ | -------------------------------------------- |
| In scope     | [What this ADR decides now.]                 |
| Out of scope | [What this ADR does not decide.]             |
| Assumptions  | [Facts assumed true at the time of writing.] |

***

## 4. Rationale

#### Main decision

- [Why this option was chosen.]

<br>

#### Why it fits the current architecture or team direction?

| Category                   | Reason                                       |
| -------------------------- | -------------------------------------------- |
| [Category in 2-4 words]    | [Reason]                                     |
| [Category in 2-4 words]    | [Reason]                                     |

<br>

#### Why it is better than the likely alternatives for this case?

| Summary                    | Reason                                       |
| -------------------------- | -------------------------------------------- |
| [Summary in a few words]   | [Reason]                                     |
| [Summary in a few words]   | [Reason]                                     |

***

## 5. Options Considered

| Option                                     | Benefits             | Tradeoffs         |
| ------------------------------------------ | ---------------------| ----------------- |
| **Option 1 — [Chosen option]**             | [Benefits]           | [Tradeoffs]       |
| Option 2 — [Alternative]                   | [Benefits]           | [Tradeoffs]       |
| Option 3 — [Alternative or `Not needed`]   | [Benefits]           | [Tradeoffs]       |

***

## 6. Impact

| Area                 | Impact                                                    |
| -------------------- | --------------------------------------------------------- |
| Code impact          | [Modules, services, files, or boundaries affected.]       |
| Data / schema impact | [Schema, migration, storage, or `None`.]                  |
| Security impact      | [Auth, secrets, validation, or exposure risk, or `None`.] |
| Performance impact   | [Runtime, DB load, latency, cache, or `None`.]            |
| Operational impact   | [Deploy, config, monitoring, rollback, or `None`.]        |
| Testing impact       | [New checks, changed tests, or verification needs.]       |

***

## 7. Consequences

| Area           | Details                                                |
| -------------- | ------------------------------------------------------ |
| Benefits       | [What becomes better or simpler.]                      |
| Tradeoffs      | [What becomes harder, more coupled, or less flexible.] |
| Follow-up work | [Next steps, cleanup, migration, or `None`.]           |
| Risks          | [Known risks, blockers, or `None`.]                    |

***

## 8. Pending Items

| Type                 | Details                                                                       |
| -------------------- | ----------------------------------------------------------------------------- |
| Pending validations  | [Open checks still needed.]                                                   |
| Pending dependencies | [Access, approval, client input, infra setup, or external work needed first.] |
| Deferred decisions   | [Related decisions that will be handled later.]                               |

***

## 9. Open Questions

- **Q1:** [Question that still needs an answer.]  
  **A1:**

- **Q2:** [Question about ownership, scope, timing, or approval.]  
  **A2:**

- **Q3:** [Question that may change the final plan.]  
  **A3:**

***

## 10. Evidence

- **Task evidence:** [Task details, Jira comments, or user request that support this ADR.]
- **Plan evidence:** [Plan details that support this ADR, or `None`.]
- **Review evidence:** [Review findings that support this ADR, or `None`.]
- **Related ADRs / prior tasks:** [Relevant prior decisions, or `None`.]

***

## 11. Review Guidance

- Future changes in this area should [follow rule / keep invariant / re-check condition].
- Revisit this ADR if [specific trigger, threshold, or new finding].
