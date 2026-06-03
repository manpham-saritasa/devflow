# RefFlow Plugin

Planning-first refactoring — review, plan + self-grill, execute, verify.
Two modes: agent (auto-drives) or manual (numbered skills).

## Modes

### Agent mode (auto)

```
User: "refactor OrderService"

Agent drives full flow:
  → ref-plan → diagnoses, writes plan, self-grills → "Proceed?"
  → ref-structure / ref-api / ref-simplify execute each step
  → ref-verify → final report ✅
```

### Manual mode (numbered)

```
Run numbered skills in order:
  ref-plan → plan written + self-grilled
  ref-structure / ref-api / ref-simplify → execute each step
  ref-verify → final report ✅
```

## What's inside

| Skill | Purpose |
|-------|---------|
| `plan` | Diagnose friction, coupling, ownership — writes plan + self-grills |
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
| "I don't know what's wrong here" | `refflow` (starts with ref-plan) |

## File map

```
refflow/
├── config.md               All configuration (paths + behavior)
├── README.md                This file
├── PRINCIPLES.md            Shared rules for all 5 skills
├── skills/
│   ├── 1.ref-plan/          Architecture diagnosis → plan + self-grill
│   ├── 2.ref-structure/     Boundaries & ownership
│   ├── 3.ref-api/           Contract redesign
│   ├── 4.ref-simplify/      Local readability
│   └── 5.ref-verify/        Verify against original specs
├── templates/
│   └── refactor-plan.md     Plan template with fill guidance
└── references/              Stack-specific guidance (13 frameworks)
    └── INDEX.md             Manifest of all 13 refs
```

## Principles

- Plan first, always. Plan + self-grill → execute → verify. No skipping.
- Preserve behavior unless explicitly asked to change it.
- One step at a time — reviewable, reversible.
- Plan is source of truth (see `config.md` for path resolution).
- When unsure, review before executing.
- When plan is vague, self-grill before executing.
- For quick single-concern refactors, use `quick-refactor` instead.
