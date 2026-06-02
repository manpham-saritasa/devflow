---
name: grill-me
version: 0.1.0
description: Auto-triggers on "should I..." and "why..." questions. Interview the user relentlessly about any plan, design, or decision. Walk down each branch until all trade-offs are explicit.
triggers:
  - "grill me"
  - "grill this"
---

# Grill Me

Stress-test any plan, design, or decision through relentless questioning. Adapted for devflow — works across architecture, tooling, workflow, and code decisions.

## When to use

Trigger on `grill me`, `grill this`, or when:
- User asks "should I...", "should we...", "why...", "what if I..."
- User says "convince me", "convince me on..."

Do not use when:
- User just wants a quick yes/no
- The decision has already been made and executed
- The question is trivial with no real trade-offs

## Rules

- Ask ONE question at a time. Wait for answer before next.
- For every question, propose your recommended answer as default. Make it easy to say "yes" or tweak.
- If a question can be answered by exploring existing codebase or docs, do that instead of asking.
- Walk down each branch of the design tree before going wide.
- Resolve dependencies between decisions one by one.

## Stop conditions

Continue until:
- All major decisions are explicit
- Edge cases, failure modes, and trade-offs have been discussed
- You can summarize the agreed plan clearly

When done:
- Summarize plan and key decisions in a concise bullet list
- Call out any unresolved risks, uncertainties, or open questions

## Example

```
User: grill me: should I merge jira-urgent, jira-task, jira-move into a plugin?

AI: Three skills share Jira auth. Option A: keep separate. Option B: bundle as jiraflow plugin.
Recommended: B — single config.md, shared auth, one folder to copy. Objections?

User: agree, but keep milestones.config in jira-move only

AI: That means jira-urgent won't have milestone labels. jira-task either.
Acceptable tradeoff? Or want milestones shared too?

User: acceptable for now

AI: Summary: jiraflow plugin with 3 skills, config.md shared, milestones per-skill.
Unresolved: jira-log integration timeline.
```
