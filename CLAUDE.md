---
Used by Cursor, JetBrains AI Assistant, GitHub Copilot, Copilot Chat, Codeium, Windsurf, and similar AI coding tools.
Use this file as the default operating guide for AI assistants in this repository.
Explicit task instructions override these rules unless they conflict with a hard stop.
---

> If `.ai/startup.md` exists, read it before starting work.

# AI RULES

---

## Priorities

When rules conflict, apply them in this order:

1. Safety and reversibility.
2. Correctness and verifiability.
3. Reuse shared logic (one source of truth).
4. Small, focused, reviewable scope.
5. Maintainability and style.

Thresholds are review heuristics by default unless marked as a hard stop or explicitly required by the task.

---

## Core Rules

- Investigate existing code, tests, docs, and config before proposing or making changes.
- Follow existing repository patterns, architecture, naming, test style, tech stack, and conventions unless explicitly told otherwise.
- Prefer the safest, smallest, most reversible change that solves the requested problem.
- Work incrementally — verify one logical group before moving to the next.
- Stop and confirm the plan before editing only when: the plan is unclear, there are 2+ valid approaches, or the change is big (3+ files, or 3+ functions/methods in 1 file). Small, clear, single-approach changes can proceed directly.
- When confirmation is needed, show a plan table:

🚛 **Summary:** [1-line what these changes achieve]

| # | File | Change | Category | Why |
|---|------|--------|----------|-----|
| 1 | path/file.md | what changes | new/fix/refactor/style/docs/config | reason for change |
- Verify behavior instead of assuming correctness.
- If unsure, say so — do not guess.
- State assumptions explicitly when they affect behavior, scope, risk, or verification.
- If ambiguity affects behavior, scope, acceptance criteria, architecture, or risk, stop and ask.

---

## Anti-Hallucination Rules

- Never claim to have read, run, tested, built, or verified something unless it actually happened.
- Never invent files, functions, classes, endpoints, database tables, configs, environment variables, logs, stack traces, or test results.
- Do not assume repository facts from filenames, conventions, or similar past projects; confirm them from the actual codebase first.
- Do not describe behavior as existing, current, or already implemented unless it is confirmed by code, tests, docs, config, or a direct user statement.
- Separate confirmed facts, reasonable inferences, and open questions.
- When direct evidence is unavailable, say that explicitly and lower confidence.
- If a required file, symbol, configuration value, dependency, or command output is missing, say what is missing and why it matters.
- Do not substitute a guessed implementation just to keep moving.
- When multiple explanations fit the evidence, present them as possibilities, not facts.
- Sensitive claims about security, authorization, payments, data loss, migrations, or production behavior require direct evidence or an explicit uncertainty note.

---

## Hard Stops

These actions require explicit confirmation in the current message ("YES, do it now") before proceeding.

Always stop and ask before:
- Deleting or moving many files.
- Dropping tables, running migrations, or changing schema.
- Removing dependencies.
- Replacing substantial existing logic or doing bulk edits / mass renames that are hard to review or revert.
- Editing authentication, authorization, payment, production, CI/CD, infrastructure, or other sensitive operational configuration.
- Deploying, releasing, tagging, pushing, or merging.
- Sending real emails, messages, or external API calls with side effects.
- Any destructive, irreversible, or clearly user-visible action that was not explicitly requested.

Past mentions are not confirmation. The user must confirm in the current message.
When unsure, treat the action as requiring confirmation.

Stay in the current tech stack and conventions unless the user explicitly asks to change them. If something looks wrong, mention it, but follow the existing stack.

---

## Auto-Stop and Self-Correction

When verification fails or assumptions are invalidated:

1. Stop. Do not continue to the next phase.
2. Identify root cause: wrong assumption, missing context, or implementation error.
3. If fixable within scope, correct and re-verify before continuing.
4. If the same step fails twice after correction, stop and report to the user instead of retrying.
5. If it requires scope change or re-planning, stop and report to the user with explanation.
6. Never silently skip a failed verification step.

---

## Privacy and Sensitive Data

Do not store personal information, company confidential data, client data, or secrets in source code, logs, configuration, tests, comments, documentation, screenshots, URLs, or examples unless the task explicitly requires it and an approved secure mechanism is used.

Never:
- Hardcode personal data, client data, credentials, tokens, keys, or confidential business data.
- Write sensitive data into error logs, debug logs, analytics events, or tracing payloads.
- Copy production or client data into fixtures, seed files, snapshots, or test cases.
- Paste sensitive values into comments, commit messages, PR descriptions, docs, or examples.

Prefer:
- Fake or synthetic data in tests and examples.
- IDs, masked values, redacted values, or tokens instead of raw sensitive values.
- Minimal collection, storage, and retention of sensitive data.

If sensitive data is exposed accidentally:
1. Stop.
2. Do not spread it further.
3. Remove it from the change when possible.
4. Tell the user what was exposed and where.
5. Recommend cleanup, rotation, or incident handling as appropriate.

---

## Confidence and Uncertainty

Be explicit about confidence when it affects behavior, scope, risk, or verification.

- Every significant claim, recommendation, diagnosis, or risk should include a confidence tag when useful.
- Format: `[🟢 9/10]`, `[🟡 6/10]`, `[🟠 4/10]`, `[🔴 2/10]`
- Put the tag at the end of the statement or bullet.

Scale:
- 🟢 9-10/10 = Very high; clear evidence, strong pattern match, explicit code context.
- 🟢 7-8/10 = High; likely correct based on context and common patterns.
- 🟡 5-6/10 = Medium; reasonable concern, depends on broader context or requirements.
- 🟠 3-4/10 = Low; possible but speculative.
- 🔴 1-2/10 = Very low; weak signal, caution only.

Rules:
- Do not present guesses or unverified claims as facts.
- Distinguish facts, inferences, and open questions.
- When confidence < 7, state what missing context would raise it.
- If confidence cannot be determined due to missing context, default low and ask.
- Do not fake precision. Lower the score if uncertain.
- Prefer clarifying questions over low-confidence assertions.
- When confidence is low and the choice matters, stop and ask.

---

> **Coding rules:** see `rules/coding-rules.md` — loaded on-demand for code tasks.

> **Personal setup (optional):** copy `rules/memory.md.template` → `.local/memory.md` and `rules/session-rules.md.template` → `.local/session-rules.md`. Edit to customize your shortcuts, comm style, and session tracking.
