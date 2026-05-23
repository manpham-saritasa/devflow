## Fill guide
- Use these evidence sources, in this order:
  1. PR title and PR body.
  2. Jira task title, description, and acceptance criteria.
  3. Local diff and changed files.
  4. Commit messages.
  5. Review comments and review decisions.
- Prefer explicit facts from PR or Jira text over inference from code.
- Use the local diff to identify actual behavior changes, touched areas, edge cases, and implementation patterns.
- Use review comments to detect risks, rejected approaches, or important concerns.
- Extract from evidence only. Do not invent.
- If evidence is weak, write: Not clear from PR evidence.
- Do not repeat the same fact across multiple sections.
- Group small edits into meaningful change units.
- Omit empty sections.

## Fill rules by section
- Goal: One or two bullets only. State the problem solved and the intended outcome.
- Changes: Summarize the main shipped changes. Prefer grouped behavior-level changes over file-by-file details.
- Key decisions: Include only decisions that affect architecture, data flow, validation rules, state handling, integration behavior, or long-term maintainability.
- Risks: Include regression risk, correctness risk, rollout risk, or known edge cases that matter for future work.
- Testing: Separate what was actually verified from what was not verified.
- Reuse later: Mark Safe to copy as YES only if the pattern appears intentional, review-safe, and not tied to one-off constraints.

## Selection hints
- If a fact is only useful to clients or testers, put it in Jira, not here.
- If a fact will help a future engineer revise similar code safely, put it here.
- If the diff shows a tiny refactor with no behavior impact, omit it unless it supports a key decision or reuse pattern.

## Output template

```md
# [KEY - JIRA task URL] — [PR title]

## Goal
- [Problem solved and why it matters]

## Changes
- [Meaningful change 1]
- [Meaningful change 2]

## Key decisions
- [Decision] — Why: ...
- [Decision] — Why: ...

## Risks
- [Risk] — Mitigation: ...
- [Risk] — Mitigation: ...

## Testing
- Verified: ...
- Not verified: ...

## Reuse later
- Safe to copy: [YES/NO]
- Reusable pattern: ...
- Caveat: ...
```