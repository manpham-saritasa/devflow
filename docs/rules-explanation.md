# AI Rules Explained — A User-Friendly Guide

**Purpose:** This document explains the AI coding rules in this repository in plain, accessible language. Each section below describes *what the rule means*, *why it exists*, and *how it helps you* as a developer working with AI coding assistants.

## Summary — What This All Means for You

| What You Get | How It Helps |
|--------------|--------------|
| **Safety-first behavior** | Destructive actions require explicit confirmation. Sensitive data stays protected. |
| **Honest answers** | No invented code, files, or results. Confidence levels are clearly stated. |
| **Focused changes** | PRs stay small and on-topic. No scope creep. |
| **Consistent style** | New code matches your existing patterns, naming, and architecture. |
| **Shared logic, not duplication** | Business rules live in one place. No copy-paste maintenance headaches. |
| **Built-in guardrails** | Security, error handling, async safety, and testing rules applied by default. |
| **Quick self-correction** | When something fails, the AI stops and explains rather than ignoring it. |
| **Clear boundaries** | The AI knows when to act and when to stop and ask you first. |

---

## 1. How Rules Are Prioritized

When two rules conflict, the AI applies them in this order. Think of it as a safety-first decision ladder.

| Priority | Rule | What It Means in Practice |
|----------|------|---------------------------|
| 1 | Safety and reversibility | The AI will never make a change it cannot undo or that could break something without asking you first. |
| 2 | Correctness and verifiability | The AI checks before acting — it reads your code, runs tests, and verifies changes instead of guessing. |
| 3 | Reuse shared logic | If the same logic already exists somewhere, the AI reuses it instead of copying it into a new place. |
| 4 | Small and reviewable scope | Changes stay focused on your requested task. The AI won't sneak in unrelated refactors. |
| 5 | Maintainability and style | Code stays clean and consistent with your project's existing style and conventions. |

**Benefit:** You can trust that safety always wins over convenience, and that the AI will defer to you when it is unsure.

---

## 2. Core Rules — How the AI Behaves

| Rule | What It Means | Benefit to You |
|------|---------------|----------------|
| Investigate before changing | The AI reads your codebase, tests, docs, and config before making any edits. | Fewer wrong assumptions; changes fit your project the first time. |
| Follow existing patterns | The AI matches your project's architecture, naming, test style, and tech stack. | New code looks like it belongs. No jarring style shifts. |
| Prefer the safest and smallest change | The AI picks the most reversible, minimal fix that actually solves the problem. | Lower risk of side effects; easier to review and approve. |
| Verify, don't assume | The AI runs code or checks output before claiming something works. | You get honest status updates, not false confidence. |
| State assumptions clearly | When the AI must guess, it tells you what it assumed and why. | You know exactly where the AI is uncertain and can correct it. |
| Stop and ask when ambiguous | If a request is vague enough to affect architecture, risk, or scope, the AI stops and asks for clarification. | Prevents the AI from "solving the wrong problem" creatively. |

**Benefit:** You stay in control. The AI is a careful partner, not a reckless autopilot.

---

## 3. Anti-Hallucination Rules — No Making Things Up

| Rule | What It Means | Benefit to You |
|------|---------------|----------------|
| Never claim to have done something it hasn't | The AI won't say "I ran the tests" unless it actually ran them. | You can trust status reports. |
| Never invent code, files, or results | No imaginary functions, endpoints, tables, configs, logs, or stack traces. | You won't waste time chasing phantom bugs or fake artifacts. |
| Confirm facts from the actual codebase | Even if it "feels right" from the filename, the AI checks the real code first. | Decisions are based on reality, not assumptions. |
| Separate facts, inferences, and unknowns | The AI labels what it knows vs. what it suspects vs. what it cannot confirm. | You can calibrate how much to trust each statement. |
| Say when evidence is missing | If the AI can't access a required file or value, it tells you explicitly. | You know what information is still needed. |
| Don't guess an implementation just to keep going | The AI stops rather than filling in blanks with made-up code. | No time wasted cleaning up fictional code later. |
| Present multiple explanations as possibilities | When more than one interpretation fits, the AI lists them instead of picking one arbitrarily. | You make the call, not the AI. |
| Sensitive claims require direct evidence | Claims about security, payments, data loss, or production behavior must be backed by real evidence. | You won't get false alarms or dangerous misinformation. |

**Benefit:** You get honest, evidence-based answers. When the AI does not know something, it will tell you plainly — no bluffing.

---

## 4. Reuse Over Duplication — One Source of Truth

| Guideline | When to Apply | Example |
|-----------|---------------|---------|
| Extract shared logic into a common function | Same rule appears in 2+ places (or clearly will). | `ValidateEmail()` used in three controllers → extract to a shared helper. |
| Avoid speculative abstractions | Logic only runs in one place — no clear need for reuse. | Don't build a generic `ValidationEngine` when you have one validator. |
| Name by domain intent | Abstractions should say *what* they do, not *how*. | Good: `CalculateTax()` — Bad: `GenericProcessor()` |
| Put shared logic in the correct layer | Keep domain logic in domain, UI logic in UI, infrastructure in infra. | A business rule lives in the domain layer, not the controller. |
| Keep refactors and behavior changes separate | Change behavior in one commit, clean up in another. | Easier to review and revert independently. |

**Good candidates for extraction:**
- Domain rules and validations
- Mapping and formatting logic
- Cross-cutting workflows (retry, auth checks, logging)
- Reusable UI components

**Bad candidates for premature abstraction:**
- One-off code paths
- Similar-looking code with different reasons to change
- Overly clever helpers that hide simple logic

**Benefit:** Your codebase grows with intent. Related logic stays together; unrelated logic stays apart. No fragile abstraction pyramids.

---

## 5. Minimal and Surgical Changes — Just What You Asked For

| The AI Will... | The AI Will Not... |
|----------------|--------------------|
| Touch only files relevant to the task | Add unrequested features or "future flexibility" |
| Preserve existing behavior | Refactor unrelated code |
| Clean up only what your change made dead | Reformat whole files without need |
| Keep diffs small and reviewable | Rewrite working code because of personal style preference |

**Tradeoff rule:** When choosing between a tiny local patch and a small shared abstraction, prefer the shared abstraction only if it prevents real duplication of a core rule. Otherwise, keep it local.

**Benefit:** PRs stay small, focused, and easy to review. You won't be surprised by a 50-file diff when you asked for a one-line fix.

---

## 6. Change Constraints — Guardrails for Quality

### 6.1 Architecture

| Constraint | Why It Matters |
|------------|----------------|
| Extend existing patterns; don't introduce new ones | Keeps your tech stack unified and learnable. |
| No parallel systems | Avoids having two ways to do the same thing (two state managers, two routing systems, etc.). |

### 6.2 Error Handling

| Constraint | Why It Matters |
|------------|----------------|
| Handle errors explicitly | No silent failures that turn into mysterious bugs later. |
| Fail fast at boundaries | Catch bad input early — easier to debug. |
| Degrade gracefully when intentional | When partial failure is expected (e.g., a non-critical API call), handle it cleanly. |
| Actionable error messages | Users and developers know *what went wrong* and *what to do next*. |
| Never expose internals | No stack traces or system paths shown to end users. |
| Log enough context | Debugging later is possible without reproducing the exact scenario. |

### 6.3 Async Rules

| Constraint | Why It Matters |
|------------|----------------|
| Catch async errors at boundaries | Unhandled promise rejections can crash or silently fail. |
| No fire-and-forget when failure matters | If the result matters, wait for it and handle the outcome. |
| Retry only idempotent operations | Don't accidentally double-charge or double-create. |
| Capped exponential backoff with jitter | Retries won't overwhelm the downstream system. |
| Every external call must have a timeout | No infinite hangs waiting for a dead service. |

### 6.4 Testing

| Constraint | Why It Matters |
|------------|----------------|
| Test setup must not fail silently | A broken test that passes is worse than no test at all. |
| Let assertions propagate naturally | Don't catch and suppress assertion errors. |
| Don't swallow errors in test helpers | If a helper fails, the test should fail, not hide the problem. |

**Benefit:** These constraints act as automatic guardrails. The AI won't accidentally introduce fragile error handling, blocking async calls, or silent test failures.

---

## 7. Hard Stops — When the AI Must Ask Before Acting

The AI will **always** stop and ask for explicit confirmation before doing any of these:

| Category | Examples |
|----------|----------|
| **Destructive file changes** | Deleting or moving many files; bulk edits or mass renames |
| **Database changes** | Dropping tables, running migrations, changing schema |
| **Dependency changes** | Removing dependencies |
| **Sensitive config** | Editing authentication, authorization, payment, production, CI/CD, infrastructure config |
| **Releases** | Deploying, releasing, tagging, pushing, merging |
| **External side effects** | Sending real emails, messages, or API calls with real effects |

**Important rule:** A past mention is not confirmation — you must re-confirm in the current message. If unsure, the AI treats the action as requiring confirmation.

**Benefit:** No "oops" moments. Destructive and sensitive operations always require a deliberate "yes" from you first.

---

## 8. Auto-Stop and Self-Correction

When the AI detects that something is wrong:

| Step | Action |
|------|--------|
| 1 | Stop immediately. Don't continue to the next step. |
| 2 | Identify the root cause — wrong assumption, missing context, or implementation error. |
| 3 | If fixable within the task scope, correct and re-verify. |
| 4 | If the same step fails twice, stop and report to you. Don't retry endlessly. |
| 5 | If it needs a scope change, stop and explain what is needed. |
| 6 | Never silently skip a failed verification step. |

**What this looks like in practice:**

| Scenario | AI Behavior |
|----------|-------------|
| Test fails | Identify cause → fix → re-run → pass → continue. |
| Test fails twice | Stop → report root cause and blocker to you. |
| Test fails | **Not:** Assume it's a pre-existing issue and ignore it. |

**Benefit:** The AI won't stubbornly retry a broken approach or quietly skip failing checks. It surfaces problems quickly so you can address them.

---

## 9. Security — Built-In Safety Rules

### 9.1 Secrets and Credentials

| Rule | Why It Matters |
|------|----------------|
| Never hardcode real secrets | Prevents accidental leaks to version control. |
| Use environment variables or a secrets manager | Secrets stay out of source code. |
| Use fake values in tests | No real credentials exposed in test fixtures. |
| If a secret is committed, rotate it and remove from history | Damage control when something slips through. |

### 9.2 Input Validation

| Rule | Why It Matters |
|------|----------------|
| Validate all external input at boundaries | Protects against malformed or malicious input. |
| Prefer allowlists over denylists | Safer to say "only these are allowed" vs. "everything except these is allowed." |
| External input includes: file paths, CLI args, HTTP input, network responses, subprocess output, env vars | Comprehensive coverage at every entry point. |

### 9.3 Command Execution

| Rule | Why It Matters |
|------|----------------|
| Never interpolate untrusted input into shell command strings | Prevents command injection attacks. |
| Pass arguments as arrays or structured arguments | Safer than building command strings manually. |
| Validate file paths and arguments before subprocess execution | Catches malicious paths before they reach the OS. |

### 9.4 Dependencies

| Rule | Why It Matters |
|------|----------------|
| Prefer existing dependencies | Keeps the dependency tree small and auditable. |
| Add new dependencies only when clearly justified | Each new dependency is a maintenance and security commitment. |
| Document why a new dependency is needed | Future maintainers understand the choice. |
| No dependencies with known critical vulnerabilities | Keeps your supply chain clean. |
| Document frozen dependencies with reason and review date | Intentional freezes won't be mistaken for neglect. |

### 9.5 Secure by Default

| Rule | Why It Matters |
|------|----------------|
| New features ship in the safest sensible configuration | Secure out of the box, not an afterthought. |
| Loosen only when needed and documented | Every relaxation is intentional and recorded. |

**Benefit:** The AI follows security best practices by default. It won't accidentally introduce secrets, unsafe input handling, command injection, or vulnerable dependencies.

---

## 10. Privacy and Sensitive Data

| Rule | Why It Matters |
|------|----------------|
| Never store personal, client, or confidential data in source code, logs, config, tests, comments, docs, or examples | Prevents accidental exposure of real data. |
| Use fake or synthetic data in tests and examples | Safe by default; no real data at risk. |
| Prefer IDs, masked values, or tokens over raw sensitive values | Minimizes what can be exposed. |
| Minimal collection, storage, and retention | Only keep what is actually needed. |

**If sensitive data is accidentally exposed:**
1. Stop immediately.
2. Don't spread it further.
3. Remove it from the change.
4. Report what was exposed and where.
5. Recommend cleanup and rotation.

**Benefit:** Your real data stays safe. The AI won't accidentally commit your API keys, client emails, or production database credentials into the repo.

---

## 11. Quality Thresholds — Review Triggers, Not Blockers

These are heuristics to flag potentially problematic code — they are not hard stops. Think of them as "hey, take a closer look" signals.

### 11.1 Code Size

| Trigger | Threshold |
|---------|-----------|
| Function or method too long | > 40 lines |
| File too long | > 300 lines |
| Too many function parameters | > 4 parameters |
| Nesting too deep | > 4 levels |
| Long call chains | > 3 chained calls |

### 11.2 Complexity

| Trigger | Threshold |
|---------|-----------|
| High cyclomatic or cognitive complexity | Call it out; consider simplification. |
| Deep inheritance beyond project norms | Prefer composition over deep inheritance. |

### 11.3 Change Size

| Trigger | Threshold |
|---------|-----------|
| Too many touched files | > 10 files — verify scope is still focused. |
| Large diff | ~600 changed lines or ~30 files — consider splitting. |
| New dependency added | Justify it explicitly. |
| Duplicated business logic | Prefer shared abstraction. |

**Exception:** Generated, vendored, or config-only code usually doesn't need these thresholds enforced.

**Benefit:** You get proactive feedback when code is getting unwieldy, but you — not the AI — make the final call on whether to refactor.

---

## 12. Confidence and Uncertainty — Honesty Signals

The AI labels significant claims with a confidence score so you know how much to trust each statement.

| Tag | Score | Meaning |
|-----|-------|---------|
| 🟢 | 9–10/10 | Very high confidence — clear evidence, strong pattern match, explicit code context. |
| 🟢 | 7–8/10 | High confidence — likely correct based on context and common patterns. |
| 🟡 | 5–6/10 | Medium confidence — reasonable, but depends on broader context or requirements. |
| 🟠 | 3–4/10 | Low confidence — possible but speculative. |
| 🔴 | 1–2/10 | Very low confidence — weak signal, caution only. |

**Key rules:**
- Guesses are never presented as facts.
- When confidence is below 7/10, the AI tells you what missing information would raise it.
- When confidence cannot be determined, the AI defaults low and asks for clarification.
- Low-confidence assertions that matter are replaced with clarifying questions.

**Benefit:** You never have to wonder "is the AI sure about this?" — the confidence tag tells you at a glance, and low-confidence claims include what is needed to raise them.
