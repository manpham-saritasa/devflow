---
name: quick-refactor
version: 0.1.0
description: Quick, test-driven refactoring for single concerns. No plan file, ≤ 3 files, tests must pass before and after.
---

## When to Use

Trigger on requests to refactor, clean up, restructure, simplify, or improve code structure. Never use for feature work, bug fixes, or behavior changes.

For multi-step planned refactors, use `refactorflow` instead.

## Rules

### Hard Constraints

- Do not change any behavior, output, API contract, or user-facing result.
- Do not add or remove features. Do not fix bugs unless the refactor incidentally exposes one — flag it separately.
- Tests must pass before and after. Run them before starting and after every change.
- If tests don't exist for the target code, flag the risk and ask before continuing.

### Scope

- One concern per refactor. Don't rename variables AND extract methods AND reorganize files in one pass.
- Touch only the files needed for the stated refactor goal. No drive-by cleanups.
- If the refactor grows beyond 3 files, stop and confirm the scope.

### Verification

- After each logical change, run the relevant test suite.
- If a test fails and the fix isn't obvious, revert the change and report.
- When done, confirm all tests pass, then show a before/after summary.

## Workflow

### Step 1: Understand

- Read the code to be refactored. Identify the exact pattern, method, or structure to improve.
- State the refactor goal in one sentence. Ask user to confirm.

### Step 2: Verify baseline

Run the relevant tests before touching anything. If any test fails, report and stop — the code must be green before refactoring.

### Step 3: Refactor incrementally

- Make the smallest change that moves toward the goal.
- Run tests after each change.
- Commit each logical step separately with a clear message.

### Step 4: Final check

- Run the full test suite. All must pass.
- Show a concise before/after summary of what changed and why.

## Commit Format

```
Refactor [what] [KEY]
```

Example: `Refactor extract auth middleware from controller DEV-14`

## Anti-Patterns

- Do not refactor AND add features in the same change.
- Do not rewrite code just because of personal style preference.
- Do not introduce new abstractions "for the future" — only extract what's already duplicated.
- Do not change variable names, method signatures, or file structure unless it directly supports the stated refactor goal.
