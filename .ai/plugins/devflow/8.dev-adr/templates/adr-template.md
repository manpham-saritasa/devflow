# ADR Template Instructions

- Condense the text into simple, short, and direct English while keeping all core concepts.
- Do not write like a marketing document with long paragraphs.
- In table, use list format in the cell if needed.
- Record decisions, constraints, pending items, impacts, cost considerations, and long-term considerations clearly.
- Separate what is decided now from what is still pending or out of scope.
- If cost is important, distinguish between confirmed cost facts and estimated cost assumptions.
- If long-term direction is important, distinguish between current decision, expected future direction, and deferred future decisions.
- Use `Decision Reasons` for why the chosen option is better, including architecture fit, team fit, cost reasoning, and long-term direction when relevant.
- Use `Options Considered` to compare benefits and tradeoffs across options, including short-term cost, long-term cost, maintenance effort, rewrite effort, and long-term sustainability when relevant.
- Use `Expected Outcomes` for what will likely happen after the decision is applied, including benefits, tradeoffs, follow-up work, risks, and long-term effects.
- Use `Pending Items` for unresolved validations, dependencies, deferred decisions, and any cost or long-term assumptions that are not validated yet.
- If there are open questions that still need an answer from the client, team, owner, or reviewer, ask them in the chat window — do not include them in the ADR file.
- Use `Review Guidance` only for future change rules and revisit triggers, including cost thresholds, strategy changes, or new findings that may invalidate the decision later.
- Do not repeat `Pending Items`, `Change Impact`, or `Expected Outcomes` inside `Review Guidance`.
- Every `[Summary or explanation about...]` placeholder must be replaced with a real 1-2 sentence summary. Never remove them silently — fill them with task-specific context.

# ADR: [Short Decision Title]

**Status:** [PROPOSED | ACCEPTED | SUPERSEDED]
**Task URL:** [JIRA-KEY](https://your-company.atlassian.net/browse/JIRA-KEY)
**Date:** YYYY-MM-DD

***

## 1. Current Context

[Summary or explanation about the Current Context.]

| Area                         | Details                                  |
| ---------------------------- | ---------------------------------------- |
| Task goal                    | [What the task needs to achieve.]        |
| Change trigger               | [Why this ADR is needed now.]            |
| Relevant constraints         | [Use list format in the cell if needed.] |
| Existing pattern or baseline | [What exists today.]                     |

***

## 2. Chosen Direction

- **Bold the key decision, product, solution, or direction.** Use 1-3 short bullets.
- Describe the chosen approach or boundary.
- State any hard rule that future work must follow.

***

## 3. Decision Scope

[Summary or explanation about the Decision Scope.]

| Scope Type   | Details                                      | Client-friendly explanation    |
| ------------ | -------------------------------------------- | ------------------------------ |
| In scope     | [What this ADR decides now.]                 | [Client-friendly explanation]  |
| Out of scope | [What this ADR does not decide.]             | [Client-friendly explanation]  |
| Assumptions  | [Facts assumed true at the time of writing.] | [Client-friendly explanation]  |

***

## 4. Decision Reasons

#### Main reasons

- [Restate the main decision and why this option was chosen.]
- [If relevant, summarize why it is the better cost or long-term direction.]

#### Why it fits the current architecture or team direction?

| Category                   | Reason              | Client-friendly explanation    |
| -------------------------- | ------------------- | ------------------------------ |
| [Category in 2-4 words]    | [Reason]            | [Client-friendly explanation]  |
| [Category in 2-4 words]    | [Reason]            | [Client-friendly explanation]  |

#### Why it is better than the likely alternatives for this case?

| Summary                    | Reason              | Client-friendly explanation    |
| -------------------------- | ------------------- | ------------------------------ |
| [Summary in a few words]   | [Reason]            | [Client-friendly explanation]  |
| [Summary in a few words]   | [Reason]            | [Client-friendly explanation]  |

***

## 5. Options Considered

[Summary or explanation about the Options Considered.]

| Option                                     | Benefits             | Tradeoffs         | Client-friendly explanation    |
| ------------------------------------------ | -------------------- | ----------------- | ------------------------------ |
| **Option 1 — [Chosen option]**             | [Benefits, including cost or long-term benefits if relevant.] | [Tradeoffs, including cost or long-term tradeoffs if relevant.] | [Client-friendly explanation]  |
| Option 2 — [Alternative]                   | [Benefits]           | [Tradeoffs]       | [Client-friendly explanation]  |
| Option 3 — [Alternative or `Not needed`]   | [Benefits]           | [Tradeoffs]       | [Client-friendly explanation]  |

***

## 6. Change Impact

[Summary or explanation about the Change Impact.]

| Area                 | Impact                                                    |
| -------------------- | --------------------------------------------------------- |
| Code impact          | [Modules, services, files, or boundaries affected.]       |
| Data / schema impact | [Schema, migration, storage, or `None`.]                  |
| Security impact      | [Auth, secrets, validation, or exposure risk, or `None`.] |
| Performance impact   | [Runtime, DB load, latency, cache, or `None`.]            |
| Operational impact   | [Deploy, config, monitoring, rollback, or `None`.]        |
| Testing impact       | [New checks, changed tests, or verification needs.]       |

***

## 7. Expected Outcomes

[Summary or explanation about the Expected Outcomes.]

| Area           | Details                                                | Client-friendly explanation    |
| -------------- | ------------------------------------------------------ | ------------------------------ |
| Benefits       | [What becomes better or simpler, including long-term benefits if relevant.] | [Client-friendly explanation]  |
| Tradeoffs      | [What becomes harder, more coupled, or less flexible.] | [Client-friendly explanation]  |
| Follow-up work | [Next steps, cleanup, migration, or `None`.]           | [Client-friendly explanation]  |
| Risks          | [Known risks, blockers, or `None`.]                    | [Client-friendly explanation]  |

***

## 8. Pending Items

[Summary or explanation about the Pending Items.]

| Type                 | Details                                                                       |
| -------------------- | ----------------------------------------------------------------------------- |
| Pending validations  | [Open checks still needed, including cost validation or long-term assumptions if relevant.] |
| Pending dependencies | [Access, approval, client input, infra setup, or external work needed first.] |
| Deferred decisions   | [Related decisions that will be handled later, including future long-term direction if relevant.] |

***

## 9. Supporting Evidence

- **Task evidence:** 
	[List of tasks' details, Jira comments, or user request that support this ADR.]
- **PR evidence:** 
	[List of PRs details that support this ADR.]	
- **Related ADRs / prior tasks:** 
	[List of relevant prior decisions, or `None`.]
- **Additional references:**
	[List of external sources (Microsoft Learn, official docs, etc.) with clickable links that support the decision.]
