> **LLM**: Follow this format strictly. Read all instructions below before writing. Do not skip sections, reorder items, or change the output structure.

## Output template

```md
# [[KEY] — [Task summary]](https://your-jira-site.atlassian.net/browse/KEY)

## Goal
- [Problem solved and why it matters]

## Added
**[1] - [Category] - [Item].**
- Purpose: ...
- Details: ...

## Changed
**[1] - [Category] - [Item].**
- Reason: ...
- Impact: ...

## Fixed
**[1] - [Category] - [Item].**
- Root cause: ...
- Resolution: ...

## Key decisions
- [Decision] — Why: ...
- [Decision] — Why: ...

## Risks
- [Risk] — Mitigation: ...
- [Risk] — Mitigation: ...

## Testing
- Verified: ...
- Not verified: ...

## Related areas
- [Feature / flow / module / integration / component]
```

Purpose: Store technical memory from this PR so future engineers and LLMs can safely revise related changes.

Tone and style:
- Use simple, short, direct, non-marketing English.
- Do not trim away core or important technical details.
- Write for future engineers and LLMs.
- Focus on behavior, design, decisions, risks, and verification.
- Prefer durable domain terms over temporary implementation details.
- Use past tense.

## Source priority
1. PR title and PR body.
2. Jira task title, description, and acceptance criteria.
3. Local changed files and diff.
4. Commit messages.
5. Review comments and review decisions.

## Core rules
- Extract. Do not invent.
- Prefer explicit facts from PR/Jira text over code inference.
- Use local diff to identify actual changed behavior, touched flows, edge cases, constraints, and reusable implementation patterns.
- Use review comments to capture rejected approaches, concerns, and important caveats.
- Group small edits into meaningful change units.
- Use stable categories such as feature area, workflow, API, validation, permissions, notifications, reporting, sync, state handling, or integration.
- Do not use file names as categories unless they are true domain terms.
- Do not repeat the same fact across sections.
- Omit empty sections.

## Section rules
- Goal: One or two bullets only. State the problem solved and intended outcome.
- Added / Changed / Fixed: Use the same grouped change format as Jira, but allow slightly more technical precision when it improves future reuse. Keep the wording at behavior or design level, not file-by-file diff narration.
- Key decisions: Keep only decisions that affect architecture, data flow, validation, integration boundaries, state handling, or maintainability.
- Risks: Include regression risk, correctness risk, rollout risk, hidden assumptions, or known edge cases relevant to future work.
- Testing: Separate what was actually verified from what was not verified. Do not imply verification that did not happen.
- Related areas: Name the feature, flow, module, integration, or component area touched. Prefer stable domain terms over file names.

## Uncertainty rules
- If evidence is weak, write: Not clear from PR evidence.
- If a decision seems implied but not explicit, include it only when the diff and review comments strongly support it.
- If a risk is possible but not evidenced, omit it.
- If end-to-end behavior was not verified, say so in Testing.

## Omit rules
- Omit trivial formatting edits, generated preview artifacts, and file rename inventory unless they matter to design, workflow, or future reuse.
- Omit stakeholder-only wording that belongs in Jira unless it also matters technically.
- Omit raw diff narration.
- If unclear, omit rather than guess.