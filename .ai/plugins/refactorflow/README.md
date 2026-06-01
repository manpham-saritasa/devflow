# Refactorflow Plugin

Planning-first refactoring — review, plan, grill, execute, verify.
Two modes: agent (auto-drives) or manual (numbered skills).

## Modes

### Agent mode (auto)

```
User: "refactor OrderService"

Agent drives full flow:
  → 1.review → shows plan → "Proceed?"
  → 2.grill → hardens plan
  → 3/4/5 execute each step
  → 6.verify → final report ✅
```

### Manual mode (numbered)

```
Run numbered skills in order:
  1.review → plan written
  2.grill → plan hardened
  3/4/5 → execute each step
  6.verify → final report ✅
```

## What's inside

| Skill | Purpose |
|-------|---------|
| `review` | Diagnose friction, coupling, ownership — writes the plan |
| `grill` | Pressure-test plan before execution |
| `verify` | Compare against original specs — confirm nothing broke |
| `structure` | Fix module boundaries, dependency direction, layout |
| `simplify` | Reduce local complexity, nesting, naming, duplication |
| `api` | Redesign contracts with compatibility migration planning |

## When to use which

| Scenario | Use |
|----------|-----|
| Quick single-file cleanup | `quick-refactor` (standalone skill) |
| Multi-step planned refactor | `refactorflow` agent or numbered skills |
| Rename a method, extract a helper | `quick-refactor` |
| Split a god class, redesign boundaries | `refactorflow` |
| "I don't know what's wrong here" | `refactorflow` (starts with 1.review) |

## File map

```
refactorflow/
├── config.md               All configuration (paths + behavior)
├── README.md                This file
├── PRINCIPLES.md            Shared rules for all 6 skills
├── skills/
│   ├── 1.review/            Architecture diagnosis → plan
│   ├── 2.grill/             Plan pressure-test
│   ├── 3.structure/         Boundaries & ownership
│   ├── 4.api/               Contract redesign
│   ├── 5.simplify/          Local readability
│   └── 6.verify/            Compare against original specs
├── templates/
│   └── refactor-plan.md     Plan template with fill guidance
└── references/              Stack-specific guidance (13 frameworks)
    └── INDEX.md             Manifest of all 13 refs
```

## Principles

- Plan first, always. Review → grill → execute → verify. No skipping.
- Preserve behavior unless explicitly asked to change it.
- One step at a time — reviewable, reversible.
- Plan is source of truth (see `config.md` for path resolution).
- When unsure, review before executing.
- When plan is vague, grill before executing.
- For quick single-concern refactors, use `quick-refactor` instead.
