# AI Coding Rules

## Task Workflow

### 1. Clarify
- Turn request into checkable goals.
- Break into logical groups.
- Define verification per phase.
- Multiple valid interpretations → stop, ask.

### 2. Plan
- Short phase-by-phase plan before coding.
- Multi-function script/plugin/tool: propose module/file structure BEFORE code. List modules + ownership. Get approval. Single-file 700+ lines never acceptable for new code regardless of language.
- Show plan first when: multi-step, high-risk, or broad diff expected.
- Group work into review slices (Data Model, Business Logic, API, UI, Tests).
- Each phase: concrete check (test, build, lint, command).

### 3. Implement
- Work incrementally. Verify one group before next.
- Touch only relevant files.
- Preserve existing behavior unless task asks to change.
- No unrelated refactors, broad reformatting, extra features.
- Small related refactors ok only when improving correctness, reuse, maintainability, verification.

### 4. Stop Conditions
Stop and ask if:
- assumption fails
- requirements conflict
- existing code/behavior conflicts with plan
- verification fails and correct fix unclear
- change violates invariant, architecture, or business rule
- implementation becomes significantly more complex/broader
- plan needs scope change or re-planning

### 5. Verification
- After every change, verify thresholds: file ≤300 lines, function ≤40 lines, ≤4 params. Run `python .ai/skills/check-thresholds/scripts/scan.py <target_dir>`.
- scan.py for Python only. .NET: Roslyn analyzers via `.editorconfig`.
- Run relevant tests, builds, linters, checks.
- Smallest verification that proves behavior.
- Full verification too expensive? Say what ran, what skipped, why.
- Bug fixes: add/update test when practical. If not, explain verification.
- New behavior/logic: add/update tests when practical.
- Never mark verified without saying what was checked.
- Never pretend verification happened.

### 6. Report
Format:
**What changed** — grouped by feature area, not file list.
**What was verified** — tests run, checks passed, commands executed.
**What was not verified** — explain what + why.
**Remaining assumptions, risks, or follow-ups** — list or `None`.
**Evidence / uncertainty** — key assumptions, missing context, inferred conclusions.

## Reuse Over Duplication

One shared implementation for shared knowledge.

- Same rule, transform, validation, mapping, workflow in 2+ places → shared function, class, component, extension, helper. Not copy-paste.
- Don't duplicate core rules to keep patch local.
- Extract when real shared invariant or likely to grow.
- Avoid speculative/framework abstractions for one-off logic.
- Name by domain intent, not vague utility names.
- Put shared code in correct layer (domain, app, infra, UI, test).
- One authoritative implementation per shared knowledge.
- Add/update tests around shared abstraction.
- Keep refactor and behavior changes separate when practical.

Extract: domain rules, validations, mapping/formatting, cross-cutting workflows (retry/backoff, auth, logging), reusable UI.
Avoid: one-off code, similar code with different reasons, "clever" helpers hiding logic, framework abstractions for one feature.

Example:
- ✅ `ValidateEmail()` in 3 controllers → shared helper + unit tests.
- ❌ Generic `ValidationEngine` for one-off.
- Extract when real shared invariant or likely to grow. Not "prepare for future."

## Minimal and Surgical Changes

Solve requested problem. Don't expand scope.

Do:
- Touch only relevant files.
- Preserve existing behavior unless task asks to change.
- Clean up only code your change made dead or wrong.
- Keep diffs small, reviewable.

Don't:
- Add features or "flexibility" nobody asked for.
- Refactor unrelated code.
- Reformat whole files.
- Rewrite working code for style preference.

Tradeoff local patch vs shared abstraction:
- Duplicates core rule/invariant → shared abstraction.
- Truly one-off → keep local.

Example:
- ✅ Rename confusing variable while fixing bug in same function.
- ❌ Reorganize whole module for new feature.
- Refactor only what improves current task. Stop at task boundary.

## Change Constraints

### Architecture
- Extend existing patterns before introducing new ones.
- No parallel architectural systems unless requested.
- Avoid alternate: state management, validation, routing, DI, data access.

### Error Handling
- Handle errors explicitly. Never silently ignore.
- Fail fast at boundaries: invalid input, impossible state, missing dep with no fallback, logic bug.
- Degrade gracefully only when partial failure intentional.
- Error messages: say what went wrong + what to do next.
- Never expose stack traces or internals to users.
- Log enough context for debugging.

### Async
- Catch async errors at boundaries.
- No fire-and-forget when failure has observable consequences.
- Retry only idempotent operations.
- Capped exponential backoff with jitter.
- Every external call: timeout.
- Never wait indefinitely.

### Tests and Errors
- Test setup must not fail silently.
- Let assertion failures propagate.
- Don't swallow errors in test helpers.

## Security

### Secrets
- Never hardcode secrets, passwords, tokens, credentials.
- Use env vars or approved secrets manager.
- Tests: fake values or mocks, never real credentials.
- Secret committed accidentally? Rotate, remove from history.

### Input Validation
- Validate and sanitize all external input at boundaries.
- External input: file paths, CLI args, HTTP input, network responses, subprocess output, env vars.
- Allowlists over denylists where practical.

### Command Execution
- Never interpolate untrusted input directly into shell command strings.
- Pass subprocess args as arrays/structured, not raw strings.
- Validate file paths and args before subprocess.

### Dependencies
- Prefer existing dependencies.
- New dep only when clearly justified, change stays minimal.
- Document why new dep.
- No deps with known critical vulns.
- Intentionally frozen dep: document reason + next review date.

### Secure by Default
- New features: safest sensible config.
- Loosen only when needed, documented.

## Quality Thresholds (Mandatory for new code)

Apply to all new/modified code. Legacy untouched exempt.

### Code Size
- Function >40 lines → extract/simplify.
- File >300 lines → split/restructure.
- One class per file.
- Params >4 → parameter object or simplify.
- Nesting >4 → early returns or extraction.
- Chain >3 calls → named intermediates.
- Class >10 methods → split into composed classes.

### Organization
- Standalone utils → domain-specific utility classes, not bare functions.
- Group modules by domain into subdirs. Shared types in `dto/` or `models/`.
- Directory structure expresses ownership, not comments.

### Complexity
- High cyclomatic/cognitive complexity → simplify when editing.
- Deep inheritance → composition.
- Multiple distinct responsibility groups → split each into own class. Compose. One reason to change.

### Naming
- Clear, readable names.
- Very short names ok in small local scopes, loops, or catch variables.

### Documentation
- Comments/docstrings for every class, public method, protected method added/modified.
- Also for global static vars, properties, methods.
- API docs: explain intent, behavior, inputs/outputs, invariants, constraints, side effects. Not restate obvious code.
- Local comments: tricky line/block, workaround, non-obvious business rule, edge case warnings.
- Follow language convention (Python docstrings, C# XML docs, TS/JSDoc).
- Docstrings for classes/methods. Regular comments for local details.

### Change Size
- >10 files touched → stop, verify scope.
- New dep → justify explicitly.
- Duplicated business logic → shared abstraction.

Generated/vendored/config-only code exempt.
