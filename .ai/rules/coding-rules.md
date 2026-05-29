# AI Coding Rules

> Loaded on-demand for coding tasks. See `AGENTS.md` for always-on rules.

---

## Task Workflow

> If not specified, use this workflow when asked to implement a feature, fix a bug, or complete a multi-step coding task.

### 1. Clarify

- Turn the request into checkable goals.
- Break work into logical groups.
- Define verification steps for each phase.
- If multiple valid interpretations remain, stop and ask instead of guessing.

### 2. Plan

- Make a short, phase-by-phase plan before coding.
- Show the plan first when the task is multi-step, high-risk, or likely to produce a broad diff.
- Group work into meaningful review slices, for example: "Data Model", "Business Logic", "API", "UI", or "Tests".
- Each phase must include a concrete check such as a test, build, lint, or command.

### 3. Implement

- Work incrementally and verify one logical group before moving to the next.
- Touch only files relevant to the task.
- Preserve existing behavior unless the task explicitly asks to change it.
- Avoid unrelated refactors, broad reformatting, or extra features.
- Small related refactors are acceptable only when they directly improve correctness, reuse, maintainability, or verification.

### 4. Stop Conditions

Stop and ask if:

- an assumption fails;
- requirements conflict;
- existing code or behavior conflicts with the plan;
- a verification step fails and the correct fix is unclear;
- the requested change appears to violate an invariant, architectural boundary, or business rule;
- the implementation becomes significantly more complex or broader than planned;
- the plan requires a scope change or re-planning.

### 5. Verification

- Run the tests, builds, linters, or checks relevant to the change.
- Prefer the smallest verification that proves the requested behavior.
- If full verification is too expensive or unavailable, say what you ran, what you did not run, and why.
- For bug fixes, add or update a test when practical; if not, explain how the fix was verified.
- For behavior changes or new business logic, add or update tests when practical.
- Never mark something as verified without saying what was actually checked.
- Never pretend verification happened.

### 6. Report

Summarize using this format:

**What changed**
- Grouped by logical feature area, not file list.

**What was verified**
- Tests run, checks passed, and commands executed.

**What was not verified**
- Explain what was not verified and why.

**Remaining assumptions, risks, or follow-ups**
- List them explicitly, or say `None`.

**Evidence / uncertainty**
- List key assumptions, missing context, and any conclusions that are inferred rather than directly verified.

---

## Reuse Over Duplication

Prefer one shared implementation for shared knowledge.

- If the same business rule, transformation, validation, mapping, or workflow appears in 2 or more places, or is clearly going to, prefer a shared function, class, component, extension, or helper instead of copy-paste.
- Do not duplicate core rules or invariants just to keep a patch local.
- Extract shared business logic when duplication represents a real shared invariant or is likely to grow.
- Avoid speculative or framework-like abstractions for one-off logic.
- Name abstractions by domain intent, not vague utility names.
- Put shared code in the correct layer (domain, application, infrastructure, UI, test support).
- Keep one authoritative implementation for each piece of shared knowledge.
- Add or update tests around the shared abstraction.
- Keep refactor and behavior changes separate when practical.

Good to extract:
- Domain rules and validations.
- Mapping and formatting logic.
- Cross-cutting workflows and policies (retry / backoff, authorization checks, logging).
- Reusable UI components or layout patterns.

Avoid premature abstraction:
- One-off code or one-time paths.
- Similar code with different reasons to change.
- "Clever" helpers that hide simple logic and reduce clarity.
- Framework-like abstractions introduced only for one feature.

#### Example

- ✅ Good: `ValidateEmail()` used in 3 controllers -> extract to shared helper with unit tests.
- ❌ Bad: Extract a generic `ValidationEngine` for one-off logic that only runs in one place.
- Rule: Extract when duplication represents a real shared invariant or is likely to grow. Do not extract to "prepare for the future."

---

## Minimal and Surgical Changes

Solve the requested problem without expanding product scope.

Do:
- Touch only files relevant to the task.
- Preserve existing behavior unless the task asks to change it.
- Clean up only code your change made dead or obviously wrong.
- Keep diffs small and reviewable.

Do not:
- Add new features or "flexibility" nobody asked for.
- Refactor unrelated code.
- Reformat whole files without need.
- Rewrite working code just because of personal style preference.

If there is a tradeoff between a very small local patch and a small shared abstraction:
- If it duplicates a core rule or invariant, prefer the shared abstraction.
- If it is truly one-off and unlikely to repeat, keep it local.

#### Example

- ✅ Acceptable: Rename a confusing variable while fixing a bug in the same function.
- ❌ Not acceptable: Reorganize an entire module while implementing a new feature.
- Rule: Refactor only what directly improves the current task. Stop at the boundary of the task scope.

---

## Change Constraints

### Architecture

- Extend existing patterns before introducing new ones.
- Do not introduce parallel architectural systems unless explicitly requested.
- Avoid introducing alternate:
  - state management
  - validation systems
  - routing patterns
  - dependency injection
  - data access layers

### Error Handling and Reliability

- Handle errors explicitly; never silently ignore them.
- Fail fast at boundaries when input is invalid, state is impossible, a required dependency is missing with no fallback, or the error reveals a logic bug.
- Degrade gracefully only when partial failure is intentional.
- Error messages must be actionable: say what went wrong and what to do next.
- Never expose internal stack traces or sensitive internals to end users.
- Log enough context for debugging.

### Async Rules

- Catch async errors at boundaries.
- Do not use fire-and-forget when failure has observable consequences.
- Retry only idempotent operations.
- Use capped exponential backoff with jitter.
- Every external call must have a timeout.
- Never wait indefinitely.

### Tests and Errors

- Test setup must not fail silently.
- Let assertion failures propagate naturally.
- Do not swallow errors in test helpers.

---

## Security

### Secrets and Credentials

- Never hardcode real secrets, passwords, tokens, or credentials.
- Use environment variables or an approved secrets manager.
- In tests, use fake values or mocks, never real credentials.
- If a secret is committed accidentally, rotate it and remove it from history as part of the fix.

### Input Validation

- Validate and sanitize all external input at the boundaries.
- External input includes file paths, CLI arguments, HTTP input, network responses, subprocess output, and environment variables.
- Prefer allowlists over denylists where practical.

### Command Execution

- Never interpolate untrusted input directly into shell command strings.
- Prefer passing subprocess arguments as arrays or structured arguments, not raw strings.
- Validate file paths and arguments before passing them to subprocesses.

### Dependencies

- Prefer existing dependencies first.
- Add new dependencies only when clearly justified and the change stays minimal.
- Document why a new dependency is needed when adding one.
- Do not introduce dependencies with known critical vulnerabilities.
- When a dependency is intentionally frozen, document the reason and next review date.

### Secure by Default

- New features should ship in the safest sensible configuration.
- Loosen only when needed and documented.

---

## Quality Thresholds (Mandatory for new code)

These thresholds apply to all new or modified code. Legacy code that was not touched is exempt by default — do not refactor it just to meet thresholds.

### Code Size
- Function or method > 40 lines: extract or simplify.
- File > 300 lines: split or restructure.
- Function parameters > 4: use a parameter object or simplify.
- Nesting depth > 4: use early returns or extraction.
- Long chains of calls: if more than 3 chained calls, use named intermediates.

### Complexity
- High cyclomatic or cognitive complexity: simplify when editing that code.
- Deep inheritance beyond project norms: use composition.

### Naming
- Use clear, readable names.
- Very short names ok in small local scopes, loops, or catch variables.

### Change Size
- More than 10 touched files: stop and verify scope is still focused.
- New dependency: justify it explicitly.
- Duplicated business logic: use shared abstraction.

Generated, vendored, or config-only code is exempt.
