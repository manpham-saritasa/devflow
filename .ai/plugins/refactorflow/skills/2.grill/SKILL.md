---
name: grill
version: 0.1.0
description: Pressure-test a refactor plan against invariants, risks, validation, and safety before execution.
---

# Grill

Use this skill to grill a refactor plan before execution.
Invoked by refactorflow agent when plan exists but needs hardening.

## When to use

This skill is invoked by the refactorflow agent in auto mode.
In manual mode, run directly after 1.plan to harden the plan.

Use `grill` when:
- a plan exists (see `config.md` at plugin root for path resolution) but is weak, vague, or risky,
- the user asks to grill, pressure-test, or harden a plan,
- the plan feels underspecified before execution.

Do not use `grill` when:
- no plan exists (use `plan` first),
- architecture is still unclear (use `plan` first),
- the user wants to execute, not grill.

## Goal

Make the plan execution-ready by tightening invariants, risks, validation, and step sizing.

## Process

1. Verify plan has required sections: Goal, Findings, Invariants, Risks, Phased plan, Validation.
   If any section is missing, flag it and request review before grilling.
2. Read the plan file.
3. Run the checklist below against every step.
4. Flag issues with specific steps.
5. Update the plan file with fixes.
6. Mark steps as ready or needs-rework.

## Grill checklist

For each step in the plan, verify:

1. **Invariants** — Are they explicit and complete? What behaviors must not change?
2. **Risks** — Are per-step risks and rollback paths defined? If this step fails, what is the recovery?
3. **Validation** — Is validation concrete? Specific tests, commands, checks — not vague statements.
4. **Step size** — Is the step reversible and reviewable? Single responsibility, < 5 files touched.
5. **Assumptions** — Are assumptions stated and verified? Unverified assumptions are risks.
6. **Test gaps** — Are missing tests acknowledged? Manual-only validation must be explicit.
7. **Rollback** — If any step fails, what is the rollback plan? `git checkout` or equivalent.

## Output

Update the plan file directly:
- Add `**GRILLED**` to the header with date.
- Add rollback plan section if missing.
- Split oversized steps.
- Replace vague validation with concrete checks.
- Flag steps that need rework with `⚠️ NEEDS REWORK`.
- Mark ready steps with `✅ READY`.

## Rules

Follow `PRINCIPLES.md` at plugin root.

- Do not execute — only diagnose and fix the plan.
- Prefer concrete over vague.
- If a step cannot be made safe, flag it and explain why.

## Stop Conditions

Stop and ask if:
- Plan file is missing, empty, or corrupt
- Plan format is unrecognized (missing required sections)
- User wants to execute without grilling and risks are unclear

## Example

### Before (weak plan)

```
## Phased plan
1. Refactor OrderService — extract logic.
## Validation
- Run tests.
```

Issues: no invariants, vague validation, no rollback, oversized step.

### After (grilled)

```
## Invariants
- POST /api/orders returns same shape.
- Discount calculation unchanged.
## Phased plan
1. Step 1 — Extract OrderDomainService (1 new file, 1 edit).
   Validation: `dotnet test Orders.Domain.Tests`.
   Rollback: `git checkout -- Orders/Domain/OrderService.cs`.
## Validation
- Step 1: run `dotnet test Orders.Domain.Tests`, verify all green.
```

Changes: invariants added, step split + sized, validation concrete, rollback explicit. Marked ✅ READY.

## Fallback

If the matt-pocock `grill-me` skill is available, prefer it for the interview-style
pressure test. Use this skill's checklist as the baseline, then run `grill-me` for
deeper design questioning.
