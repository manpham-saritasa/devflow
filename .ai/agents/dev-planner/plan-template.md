# Plan for [JIRA-KEY]: [Task Summary]

**ID:** [JIRA-KEY]
**Title:** [TASK-TITLE]
**Status:** Draft

## Plan

[One or two sentences. Overall goal of this task and the expected user/business outcome.]

---

## Scope

**In scope:**
1. [Work this task must complete.]
2. [Another explicit in-scope item.]

**Out of scope:**
1. [Work explicitly excluded from this task.]
2. [Another excluded area, refactor, or enhancement.]

**Do not modify:**
1. [Critical file, folder, artifact, API contract, or behavior that must remain unchanged.]
2. [Another protected area if applicable.]

---

## Proposed Changes

[Add as many change sections as needed. Order them in the recommended implementation sequence. If a change depends on an earlier one or can run in parallel, state that explicitly inside the change.]

### 1. [Small meaningful feature or fix name]

- **User outcome:** [What user gets. One sentence.]
- **Why:** [Why this change exists. One sentence.]
- **Affected area:** [Main component, module, or workflow affected.]
- **Confidence:** [Confirmed | Likely | Needs verification]

- **Implementation**
  - `[path/to/file.ts or placeholder]` — [What changes and why. Class or method name if known.]
  - `[path/to/file.ts or placeholder]` — [What changes and why. Class or method name if known.]
  - **Verify:** [One concrete check. Proves this item is done.]

- **Test Impact**
  - **Add:** [New test needed for new logic in this change. "None" + reason if not needed.]
  - **Update:** [Existing test that breaks or needs change. "None" if not applicable.]
  - **Verify manually:** [Flow or area to verify manually or e2e for this change.]

---

### 2. [Small meaningful feature or fix name]

- **User outcome:** [What user gets. One sentence.]
- **Why:** [Why this change exists. One sentence.]
- **Affected area:** [Main component, module, or workflow affected.]
- **Confidence:** [Confirmed | Likely | Needs verification]

- **Implementation**
  - `[path/to/file.ts or placeholder]` — [What changes and why. Class or method name if known.]
  - **Verify:** [Concrete validation step.]

- **Test Impact**
  - **Add:** [New test. "None" + reason if not needed.]
  - **Update:** [Existing test. "None" if not applicable.]
  - **Verify manually:** [Integration area.]

---

## Done Criteria

1. [Observable task-level outcome proving the overall task is complete.]
2. [Protected areas, contracts, and must-not-break behaviors remain unchanged.]
3. [Required acceptance, parity, or rollout conditions are satisfied.]

---

## Risks, Constraints & Open Questions

**Constraints:**
1. [Hard constraint from task context. Technical or business rule that must be respected.]
2. [Another rule that limits implementation choices.]

**Risks:**
1. [Risk or known limitation.]
2. [Potential regression, integration issue, or uncertainty.]

**Open Questions:**
1. [Unresolved question. Flag if it blocks implementation.]
2. [Decision that may require clarification.]

---

## Impact Related Tasks

| Source | Type | Impact (0-10) | Why |
|--------|------|----------------|-----|
| [Current repository / codebase] | Codebase | [0-10] | [How much the current codebase shaped the plan.] |
| [JIRA-KEY or task reference] | Related task | [0-10] | [Why this task is impacted or how much it informed the plan.] |
| [Add more rows as needed] | [Type] | [0-10] | [Reason] |