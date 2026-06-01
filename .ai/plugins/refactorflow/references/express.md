# Express guidance

## Architecture review focus
- Examine whether routes, middleware, and business logic have clear separation.
- Check for fat route handlers that mix validation, business rules, and DB calls.
- Look for duplicated middleware logic (auth, validation, error handling)
  that should be centralized.
- Identify where error handling is inconsistent — some routes catch errors,
  others let them propagate to the default handler.

## Structure refactor focus
- Separate routes, controllers, services, and data access.

  Good (Express + layered):
  ```
  src/
  ├── features/
  │   └── orders/
  │       ├── orderRoutes.js        app.use('/orders', orderRoutes)
  │       ├── orderController.js    (req, res) => orderService.create(...)
  │       ├── orderService.js       Business logic, no req/res
  │       └── orderRepository.js    DB queries only
  └── middleware/
      ├── auth.js
      ├── validate.js
      └── errorHandler.js           app.use(errorHandler) at the end
  ```

- Keep route files thin — define paths and HTTP methods, delegate to controllers.
  ```js
  // orderRoutes.js
  const router = require('express').Router();
  const ctrl = require('./orderController');

  router.post('/', validateOrder, ctrl.create);
  router.get('/:id', ctrl.getById);

  module.exports = router;
  ```
- Controllers parse request, call service, send response. No business logic.
  ```js
  // orderController.js
  exports.create = async (req, res, next) => {
    try {
      const order = await orderService.create(req.body);
      res.status(201).json(order);
    } catch (err) {
      next(err); // delegate to errorHandler middleware
    }
  };
  ```
- Use a single error-handling middleware at the end of the middleware chain.
  ```js
  // errorHandler.js
  module.exports = (err, req, res, next) => {
    console.error(err);
    res.status(err.status || 500).json({ error: err.message });
  };
  ```
- Avoid `app.use(express.json())` buried in route files — keep app setup centralized.

## Simplify refactor focus
- Replace nested callbacks with `async/await`.
- Extract validation logic into reusable middleware (e.g., `validateOrder`).
- Use a validation library consistently (Joi, Zod, express-validator) rather
  than ad-hoc checks in each route.
- Avoid magic numbers in status codes — use `res.status(201)` consistently,
  consider named constants for common codes if the team prefers.
- Centralize CORS, helmet, rate-limiting, and other security middleware in one place.
- If using `app.locals` or `req` as a bag of values, consider explicit
  dependency injection or context objects instead.
