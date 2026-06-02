# Refflow Principles

Shared principles for all refflow skills. Every sub-skill follows these.

## Invocation modes

All execution skills support two modes:

- **Auto mode**: Invoked by the refflow agent during the full workflow.
- **Manual mode**: Run directly by the user. Each skill's "When to use" section specifies its manual trigger.

Require a plan from `1.plan` before running any execution skill manually.

## Core principles

- Preserve behavior unless behavior changes are explicitly requested.
- Prefer small, reviewable steps that can be easily reverted if needed.
- Make risks, invariants, and validation explicit before execution.
- Keep the saved plan as the source of truth.
- Avoid giant rewrites and "do everything in one go" changes.
- Request only the minimal extra context necessary to proceed safely.

## Execution rules

- Touch only files relevant to the task.
- Preserve existing behavior unless the task explicitly asks to change it.
- Avoid unrelated refactors, broad reformatting, or extra features.
- Stop after one bounded step unless the user explicitly asks to continue.

## Safety rules

- If the user asks "what would you change?" or "show me first", output proposed changes without applying them. Mark as `[PREVIEW]`. Only apply after confirmation.
- Run relevant tests before starting and after every change.
- If tests don't exist for the target code, flag the risk and ask before continuing.
- If a test fails and the fix isn't obvious, revert the change and report.
- Do not implement code changes unless explicitly asked and the scope is clear.
- Prefer concrete findings over generic advice.
- If the codebase is very large, narrow to the most critical slice.
- Ask for confirmation when structural changes affect many files or modules.
