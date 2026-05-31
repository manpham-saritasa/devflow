---
name: deep-review
description: Review a workflow, plugin, skill, or process across 13 dimensions. Outputs prioritized findings with reasons and suggested fixes. Use when user says "deep review", "review this plugin", "audit", or wants a comprehensive quality check.
triggers:
  - "deep review"
  - "deep-review"
  - "audit"
---

## When to Use

Review any AI agent workflow: a plugin, skill, process, or pipeline. Read all relevant files first, then evaluate across all dimensions. Output findings sorted by criticality.

## Dimensions

Review across ALL 10 dimensions. Do not skip any.

| # | Dimension | What to check |
|---|-----------|---------------|
| 1 | Structure | SKILL.md frontmatter valid? Sections present? Trigger format correct? Templates/scripts where needed? |
| 2 | Duplication | Repeated patterns across files? Shared config used? Templates referenced or copy-pasted? |
| 3 | Dependencies | Cross-plugin references? Hardcoded paths? Clean boundaries between plugins? |
| 4 | Consistency | Step numbering uniform? Checkpoint format same? Flag tables consistent? Naming conventions? |
| 5 | Safety | Checkpoints before destructive actions? Dry-run support? Hard stops? Push/merge gated? |
| 6 | Completeness | All triggers covered? Error handling? Edge cases? Stop conditions clear? |
| 7 | Independence | Can it run standalone? Or must it be used with other skills/plugins? |
| 8 | Readability | Instructions clear? Steps logical? Too verbose? Easy to follow as an agent? |
| 9 | Automation | Scripts where deterministic? Tests exist? Manual steps minimal? |
| 10 | Scope | Single responsibility? Not too broad? Not too narrow? Boundaries clear? |
| 11 | Correctness | Logical flaws? Wrong assumptions? Does step X actually achieve its stated goal? Would the workflow produce wrong output in any scenario? |
| 12 | Edge Cases | What if a file is missing? What if an API call fails? What if the user is on the wrong branch? What if credentials are missing? Are all branches handled? |
| 13 | Long-Term | Will this still work 12 months from now? Hardcoded dates/versions/URLs? Depends on a service that may change? Can a new team member pick it up? Does it scale with more skills/tasks? |

## Output Format

```text
## Deep Review — [Target Name]

Type: [plugin / skill / workflow / process]
Files reviewed: [N]

### Findings

| # | Criticality | Dimension | Location | Issue | Reason | Suggested Fix |
|---|-------------|-----------|----------|-------|--------|---------------|
| 1 | Critical | Safety | path:line | No checkpoint before merge | Risk of accidental deploy | Add checkpoint: "Proceed? (yes/no)" |

### Summary

- Critical: [N]
- High: [N]
- Medium: [N]
- Low: [N]

### Verdict

[Pass / Pass with Changes / Fail]
```

## Criticality Scale

| Level | When to use |
|-------|------------|
| Critical | Data loss, security flaw, broken workflow, missing safety check on destructive action |
| High | Missing error handling, incomplete trigger coverage, cross-plugin coupling, broken edge case |
| Medium | Duplication, inconsistency, missing dry-run, unclear stop condition |
| Low | Verbosity, naming nitpick, cosmetic, nice-to-have |

## Rules

- Read ALL files in the target before evaluating.
- Every finding must have: location, issue description, reason why it matters, and a suggested fix.
- Do not skip dimensions. If a dimension has no issues, note it: "Dimension X: no issues found."
- Sort findings by Critical → High → Medium → Low.
- If the target references other plugins or skills, check those too for dependency issues.
