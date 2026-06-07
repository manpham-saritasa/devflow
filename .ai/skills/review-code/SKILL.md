---
name: review-code
version: 0.3.0
description: Review code changes for structure, quality, security, performance, and edge cases. Shows findings before applying fixes. Portable — no project-specific dependencies.
triggers:
  - "review code"
  - "review-code"
  - "code review"
  - "check this code"
---

# Review Code

Audit code changes across 8 dimensions. Show all findings first, then ask before applying fixes.

## When to Use

After any LLM code change — user says "review code" or equivalent. Also run before committing milestone changes.

## Target

- User specifies files or directories. If none, review the current git diff.
- Accept file paths, directories, or `--diff` for staged/unstaged changes.
- Language-agnostic. Apply appropriate linters/analyzers for the project's language.

## Quality Thresholds

These thresholds apply to all new or modified code. Legacy code that was not touched is exempt — do not refactor it just to meet thresholds.

### Code Size
- Function or method > 40 lines: extract or simplify.
- File > 300 lines: split or restructure.
- One class per file — no multiple classes in a single module.
- Function parameters > 4: use a parameter object or simplify.
- Nesting depth > 4: use early returns or extraction.
- Long chains of calls: if more than 3 chained calls, use named intermediates.
- Class > 10 methods: split distinct responsibility groups into composed classes.

### Organization
- Standalone utility functions belong in domain-specific utility classes, not as bare module-level functions.
- Group modules by domain into subdirectories. Use directory structure to express ownership, not comments.
- Shared types belong in a `dto/` or `models/` folder.

### Complexity
- High cyclomatic or cognitive complexity: simplify when editing that code.
- Deep inheritance beyond project norms: use composition.
- If a class has multiple distinct responsibility groups, split each into its own class.

### Naming
- Use clear, readable names.
- Very short names ok in small local scopes, loops, or catch variables.

### Documentation
- Add comments/docstrings for every class, public method, and protected method added or modified.
- Comments must explain intent, behavior, inputs/outputs, invariants, or side effects — not restate obvious code.
- Prefer the language and repository convention (Python docstrings, C# XML docs, TS/JSDoc).

### Change Size
- More than 10 touched files: stop and verify scope is still focused.
- New dependency: justify it explicitly.
- Duplicated business logic: use shared abstraction.

## Workflow

### Step 1: Run Tests

Run the test suite for the changed area.
- If tests **fail**: list failures, flag as 🔴 Critical, **STOP**. Do not produce a verdict until tests pass.
- If no tests exist: note it as a gap under Dimension 8 (Testing).

### Step 2: Check Scope

- Compare changed files against what the user asked for.
- Flag unexpected files (changed but outside declared scope) as 🟡 High. Do not auto-fail — the change may be justified.
- If >10 files touched: flag and verify scope is still focused.

### Step 3: Review Across 8 Dimensions

| # | Dimension | What to check |
|---|-----------|---------------|
| 1 | Structure | See Quality Thresholds above. File/function size, params, nesting, naming, docs. |
| 2 | Security | SQL injection? Prompt injection? Hardcoded secrets? Unsanitized input? Unsafe command execution? Auth/authz bypass? Sensitive data in logs? New dependency with known vuln? |
| 3 | Performance | N+1 queries? Unbounded loops? Missing timeouts on external calls? Repeated work in loops? Large in-memory allocations? Missing indexes for new queries? |
| 4 | Edge Cases | Null/empty inputs handled? Boundary conditions? Error states? Concurrent access? Race conditions? What if file missing, API down, credentials expired? |
| 5 | Correctness | Control flow correct? Regression risk? Logic errors? Wrong assumptions? Public interface intact (same signatures, same return types, no removed/renamed public methods, exceptions unchanged)? Does the change actually solve the stated problem? |
| 6 | Design | Follows existing patterns? Single responsibility? No duplicated business logic? Correct layer placement (domain/app/infra)? Clean boundaries? |
| 7 | Error Handling | Errors logged with enough context? Fail fast at boundaries? Graceful degradation where appropriate? No swallowed exceptions? Actionable error messages? No stack traces to users? |
| 8 | Testing | New tests for new behavior? Edge cases covered? Test setup not silently failing? Coverage adequate for critical paths? |

### Step 4: Show Findings

Present all findings before applying fixes.

## Severity

| Level | When to use |
|-------|------------|
| 🔴 Critical | Security flaw, data loss risk, crash, broken core invariant, regression of key behavior, tests failing |
| 🟡 High | Missing error handling, N+1 query, missing timeout, untested critical path, unexpected files |
| 🟠 Medium | Quality threshold violation, design issue, undocumented public API, duplicated logic |
| 🟢 Low | Naming nit, minor cleanup, style preference |

## Output Format

**Number findings continuously** — #1, #2, #3, ... across the entire review.

```
## Code Review — [target]

Files reviewed: [N]
Date: [YYYY-MM-DD]

### Findings

| # | Severity | Dimension | Location | Issue | Suggested Fix |
|---|----------|-----------|----------|-------|---------------|
| 1 | 🔴 Critical | Security | src/auth.py:42 | SQL injection in raw query | Use parameterized query |
| 2 | 🟡 High | Performance | src/api.py:88 | N+1 query in loop | Eager-load with .Include() |
| 3 | 🟠 Medium | Structure | src/utils.py | Function >40 lines | Extract helper methods |

### Summary

- Critical: [N]
- High: [N]
- Medium: [N]
- Low: [N]

### Verdict

[Pass / Pass with Changes / Fail]
```

## Rules

- Read ALL files in the target before evaluating. If >20 files, sample key files and note.
- Every finding must have: severity, dimension, file:line location, issue description, suggested fix.
- Do not skip dimensions. If clean, note briefly: "Dimension N: no issues found."
- Sort by severity: Critical → High → Medium → Low.
- Show findings FIRST. Ask "Apply fixes?" before making any changes.
- If a fix is beyond LLM capability (e.g., architectural redesign), flag as `[manual]` and skip auto-fix.
- Do not fix unrelated issues. Stay in scope.
- If new dependency added, verify no known vulnerabilities.
- If target is empty or has no changed files, report and stop.
- No project-specific dependencies. All thresholds and rules are self-contained.
