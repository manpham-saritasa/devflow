# Skill: grill-me

---
name: grill-me
description: interview the user relentlessly about every aspect of their plan or design until you reach a shared understanding.
triggers:
  - "grill me"
  - "grill"
---

## Usage

Use when the user wants to stress-test a plan, get grilled on their design, or says "grill me".

Interview the user relentlessly about every aspect of their plan or design until you reach a shared understanding.

Walk down each branch of the design tree, resolving dependencies between decisions one by one.

If a question can be answered by exploring the existing codebase or docs, explore those instead of asking the user.

For each question you ask, propose your recommended answer as a default. Make it easy for the user to say "yes", or to tweak your recommendation.

Continue until:
- All major decisions have been made explicit.
- Edge cases, failure modes, and trade-offs have been discussed.
- You can summarize the agreed plan clearly in your own words.

When you are done:
- Summarize the plan and key decisions in a concise bullet list.
- Call out any unresolved risks, uncertainties, or open questions.