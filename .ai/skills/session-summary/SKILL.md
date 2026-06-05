---
name: session-summary
version: 0.1.0
description: Summarize the current working session into a continuation-ready handoff document for another agent.
triggers:
  - "session summary"
  - "summarize session"
  - "handoff summary"
argument-hint: "Optional: what should the next agent continue or focus on?"
---

# Skill: session-summary

## Purpose

Use this skill when the user wants a compact but reliable summary of the current session so another agent can continue the work without re-reading the full thread.

## Output rules

- Output markdown only.
- Also persist the latest summary to `.local/sessions/last-summary.md`.
- Optionally save an archival copy to `.local/handoffs/session-YYYY-MM-DD-HHMM.md` when the workflow calls for history.
- Base the summary only on:
  - the current conversation
  - tool outputs
  - verified file changes
  - explicit user statements
- Do not invent actions, files, test results, conclusions, or validation.
- Distinguish clearly between:
  - facts discovered
  - outcomes completed
  - pending work
- If something was attempted but not finished, say so explicitly.
- Use repository-relative paths when naming files.
- Keep the tone factual, neutral, and continuation-friendly.
- Preserve enough detail that a fresh agent can resume immediately.

## When to use

Trigger on:
- `session summary`
- `summarize session`
- `handoff summary`

If the user includes extra text after the trigger, treat it as optional context about what the next agent should focus on, and include that as a short note in the next-steps section when relevant.

## Required structure

```md
# Conversation Summary

## 1. Overview
- Briefly explain the main goal of the session.
- Summarize the major phases of work in chronological order.

## 2. Key Facts and Information Discovered
- List important facts learned during the session.
- Group related facts under short subsection headings when useful.
- Include only evidence-backed facts or clearly labeled inferences.

## 3. Outcomes and Conclusions Reached
- List what was completed.
- Name files created, updated, moved, or deleted.
- Summarize meaningful conclusions, decisions, and behavior changes.
- If work was partially completed, include that and describe the current state.

## 4. Action Items / Next Steps
- List the most likely next actions.
- Include expected output files or commands if they are clear.
- Mention optional follow-ups separately from the main pending task.

## Quick Recap
- End with a short bullet recap of the most important points.
```

## Writing style

- Be specific.
- Be concise but not too terse.
- Use nested bullets where they improve scanning.
- Avoid filler.
- Do not address the user directly.
- Do not include speculation unless explicitly labeled as an inference or possible follow-up.

## Persistence

After generating the summary:
- Write the full summary to `.local/sessions/last-summary.md`.
- If keeping historical snapshots is useful, also save a copy to `.local/handoffs/session-YYYY-MM-DD-HHMM.md`.
- If writing fails, report that clearly instead of pretending persistence worked.
- Treat the saved summary as continuation context for the next session, but never as higher priority than a new user instruction.

## Quality checks

Before returning the summary, confirm:
- Every claimed file/path appeared in the session or tool output.
- Completed work is not mixed with proposed work.
- Any incomplete or blocked step is called out explicitly.
- The result is useful as a standalone handoff for another coding agent.
