---
name: grill-me
description: interview the user relentlessly about every aspect of their plan or design until you reach a shared understanding.
triggers:
  - "grill me"
  - "grill"
---

# Skill: grill-me

## Usage

Use when the user wants to stress-test a plan, get grilled on their design, or says "grill me".

Interview the user relentlessly about every aspect of their plan or design until you reach a shared understanding.

Walk down each branch of the design tree, resolving dependencies between decisions one by one.

If a question can be answered by exploring the existing codebase or docs, explore those instead of asking the user.

For each question you ask, propose your recommended answer as a default. Make it easy for the user to say "yes", or to tweak your recommendation.

Ask the questions one at a time, waiting for feedback before continuing.

Continue until:
- All major decisions have been made explicit.
- Edge cases, failure modes, and trade-offs have been discussed.
- You can summarize the agreed plan clearly in your own words.

When you are done:
- Summarize the plan and key decisions in a concise bullet list.
- Call out any unresolved risks, uncertainties, or open questions.

---

## Examples

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

```
User: grill me

AI: What topic? The whole devflow plugin? Jira-move specifically? Something else?

User: move the jira-move scripts into /scripts folder

AI: That means configs stay at skill root, code in /scripts. Clean separation.
But every script needs os.path.dirname(SKILL_DIR) to reach configs.
Recommend: yes. One-line cost worth the clarity. Proceed?
```
