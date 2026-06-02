# Node.js guidance

## Architecture review focus
- Examine module boundaries, import direction, and whether side effects are isolated.
- Check whether entry points (CLI, server, worker, script) are explicit and discoverable.
- Look for business logic leaking into HTTP handlers, middleware, or route definitions.
- Identify duplicated cross-cutting concerns (auth, logging, error handling, validation)
  that should be centralized middleware or shared modules.

## Structure refactor focus
- Prefer feature-oriented grouping over technical-layer grouping.

  Good:
  ```
  src/
  ├── features/
  │   ├── orders/
  │   │   ├── orderController.js    Thin — delegates to service
  │   │   ├── orderService.js       Business logic
  │   │   ├── orderRepository.js    Data access
  │   │   └── orderRoutes.js        Route definitions
  │   └── customers/
  │       ├── customerController.js
  │       ├── customerService.js
  │       └── customerRoutes.js
  └── shared/
      ├── middleware/
      │   ├── auth.js
      │   └── errorHandler.js
      └── utils/
          └── validate.js
  ```

  Avoid:
  ```
  src/
  ├── controllers/   (all controllers, no ownership)
  ├── services/      (all services, no ownership)
  ├── routes/        (flat route list)
  └── utils/         (catch-all)
  ```

- Keep HTTP concerns (req/res, status codes, headers) in controllers/routes.
  Business logic lives in services — no `req` or `res` objects there.
- Separate infrastructure (DB, file system, external APIs) behind interfaces
  or simple module boundaries. Don't `require('pg')` in a service.
- Avoid `utils.js`, `helpers.js`, `common.js` catch-alls.
  Name modules by intent: `formatCurrency.js`, not `utils.js`.

## Simplify refactor focus
- Prefer early returns over deep `if/else` nesting.
- Extract repeated validation or transformation logic into named functions.
- Replace callback pyramids with `async/await` and proper error handling.
- Be careful with Promise chains — unhandled rejections crash Node processes.
- Use `try/catch` at async boundaries; don't let errors propagate silently.
- Avoid mutating shared objects; prefer immutable patterns or explicit copies.
- Use `const` by default, `let` only when reassignment is necessary.
