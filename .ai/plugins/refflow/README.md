# Refflow = Refactor Flow

Planning-first refactoring — review, plan, grill, execute, verify.
Two modes: agent (auto-drives) or manual (numbered skills).

## Modes

### Agent mode (auto)

```
User: "refactor OrderService"

Agent drives full flow:
  → 1.plan → shows plan → "Proceed?"
  → 2.grill → hardens plan
  → 3/4/5 execute each step
  → 6.verify → final report ✅
```

### Manual mode (numbered)

```
Run numbered skills in order:
  1.plan → plan written
  2.grill → plan hardened
  3/4/5 → execute each step
  6.verify → final report ✅
```

## What's inside

| Skill | Purpose |
|-------|---------|
| `plan` | Diagnose friction, coupling, ownership — writes the plan |
| `grill` | Pressure-test plan before execution |
| `structure` | Fix module boundaries, dependency direction, layout |
| `api` | Redesign contracts with compatibility migration planning |
| `simplify` | Reduce local complexity, nesting, naming, duplication |
| `verify` | Verify against original specs — confirm nothing broke |

## When to use which

| Scenario | Use |
|----------|-----|
| Quick single-file cleanup | `quick-refactor` (standalone skill) |
| Multi-step planned refactor | `refflow` agent or numbered skills |
| Rename a method, extract a helper | `quick-refactor` |
| Split a god class, redesign boundaries | `refflow` |
| "I don't know what's wrong here" | `refflow` (starts with 1.plan) |

## File map

```
refflow/
├── config.md               All configuration (paths + behavior)
├── README.md                This file
├── PRINCIPLES.md            Shared rules for all 6 skills
├── skills/
│   ├── 1.plan/              Architecture diagnosis → plan
│   ├── 2.grill/             Plan pressure-test
│   ├── 3.structure/         Boundaries & ownership
│   ├── 4.api/               Contract redesign
│   ├── 5.simplify/          Local readability
│   └── 6.verify/            Verify against original specs
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
