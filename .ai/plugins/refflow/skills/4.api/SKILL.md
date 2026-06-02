---
name: api
version: 0.1.0
description: Redesign internal or external API contracts safely with compatibility-aware migration planning, adapters, and deprecation paths.
---

# API

Use this skill when the plan step is tagged `[api]`.
Invoked by refflow agent during execution.

## When to use

See `PRINCIPLES.md` for invocation modes.
Manual trigger: run when a plan step is tagged `[api]`.

## Goal

Improve APIs without casual breaking changes.

## Focus

Apply this skill to:
- method signatures,
- DTOs,
- endpoints,
- requests and responses,
- props and hook contracts,
- service interfaces,
- adapters,
- versioning and migration plans.

## Required classification

You MUST classify every change as one of:
- internal only (no external callers),
- backward compatible,
- breaking.

If you cannot determine the classification, you MUST ask for more information before proceeding.

## Preferred approach

1. Read the plan file and find the step tagged `[api]`.
2. Run relevant tests before touching anything. If any test fails, report and stop.
3. Classify the change (internal only / backward compatible / breaking).
4. Apply the change following the preferred approach:
   - Add new contract first.
   - Keep old contract delegating when feasible.
   - Migrate callers gradually where possible.
   - Use adapters or translation layers when old and new must coexist.
   - Make deprecation explicit and time-bounded.
5. Run tests after the change. If a test fails and the fix isn't obvious, revert and report.

## Output format

Use `templates/refactor-plan.md` at plugin root as the output template.

1. API findings.
2. Compatibility classification.
3. Proposed contract changes.
4. Migration plan.
5. Risks and validation.
6. Step 1 only when implementation is requested.

## Rules

Follow `PRINCIPLES.md` at plugin root.

- Do not introduce breaking changes without a clear migration and rollback plan.
- Do not silently change behavior for existing callers.
- Make versioning and deprecation plans explicit in the plan file
  (see `config.md` at plugin root for path resolution; default: `.local/tasks/refactor/refactor-plan.md`).
- Align with any existing API guidelines or architecture documents if available.

## Stop Conditions

Stop and ask if:
- Plan file is missing or the step tagged `[api]` cannot be found
- Compatibility classification is unclear — must classify before proceeding
- Breaking change detected without explicit migration plan
- Tests fail and the fix is not obvious — revert and report

## Example

### Scenario

Existing endpoint:

- Route: `POST /api/orders`
- Request body:
  - `customerId` (string)
  - `items` (array of `{ productId, quantity }`)
- Response:
  - `orderId`
  - `status`
  - `total`

New requirements:
- support discount codes,
- support additional metadata,
- avoid breaking existing clients.

### Example classification

- Change: introduce `discountCode` and `metadata` fields in the request.  
- Classification: backward compatible (fields are optional, existing clients still work).

### Example contract evolution

- New request shape (conceptual):

```json
{
  "customerId": "...",
  "items": [ { "productId": "...", "quantity": 1 } ],
  "discountCode": "OPTIONAL",
  "metadata": {
    "source": "web",
    "campaign": "spring-sale"
  }
}
```

- Strategy:
  - accept both old and new shapes by treating `discountCode` and `metadata` as optional,
  - keep endpoint path and response shape stable,
  - add server-side defaults for metadata when missing.

### Example migration plan (abridged)

1. Phase 1:
   - Update server to accept optional `discountCode` and `metadata`.
   - Keep response unchanged.
   - Add tests for old and new request shapes.

2. Phase 2:
   - Update official clients to send `metadata` and `discountCode` when needed.

3. Phase 3 (optional):
   - Deprecate legacy use-cases if any behavior will change in future, documenting timeline.