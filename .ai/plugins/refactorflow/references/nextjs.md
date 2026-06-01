# Next.js guidance

## Architecture review focus
- Examine how the app is structured by routes, layouts, and segments.
- Check whether server components, client components, and shared modules have clear responsibilities.
- Look for data-fetching logic scattered across many components instead of being centralized at route boundaries.
- Identify where API routes, middleware, and edge functions mix concerns with UI or domain logic.

## Structure refactor focus
- Prefer feature- or route-oriented grouping (e.g., `app/orders`, `app/customers`) instead of generic buckets.

  Good:
  ```
  app/
  ├── orders/
  │   ├── page.tsx           Server component — fetches data
  │   ├── OrderList.tsx      Client component — interactive UI
  │   ├── actions.ts         Server actions for mutations
  │   └── orderService.ts    Domain logic, shared between server + route handlers
  └── customers/
      ├── page.tsx
      └── CustomerCard.tsx
  ```

- Separate server components (data fetching, orchestration) from client components (interactive UI) with clear boundaries.
  ```tsx
  // app/orders/page.tsx — SERVER component (no 'use client')
  import { getOrders } from './orderService';
  import { OrderList } from './OrderList';

  export default async function OrdersPage() {
    const orders = await getOrders();
    return <OrderList orders={orders} />;
  }
  ```
  ```tsx
  // app/orders/OrderList.tsx — CLIENT component
  'use client';
  export function OrderList({ orders }: { orders: Order[] }) {
    // interactive state, handlers, etc.
  }
  ```

- Keep cross-cutting utilities (auth, logging, error handling) in well-named modules.
  ```ts
  // lib/auth.ts — one place for auth
  // lib/logger.ts — one place for logging
  ```
  Avoid `utils/helpers.ts` catch-alls.

- Avoid deeply nested layout trees where simpler composition or shared layouts would work.

## Simplify refactor focus
- Move heavy conditional rendering and data-massaging logic out of JSX into named functions or hooks.

  Before:
  ```tsx
  {orders.filter(o => o.status === 'pending').map(o => (
    <div>{o.items.reduce((sum, i) => sum + i.price * i.qty, 0)}</div>
  )).slice(0, 5)}
  ```

  After:
  ```tsx
  const recentPendingOrders = getRecentPendingOrders(orders);
  // ...
  {recentPendingOrders.map(o => <OrderRow key={o.id} total={calculateTotal(o)} />)}
  ```

- Clarify responsibilities between route-level components, shared UI, and hooks.
- Be careful when changing data-fetching patterns (e.g., moving between `fetch` in server components, `getServerSideProps`, or client-side fetching) so behavior and caching semantics remain correct.
- Avoid mixing client-only browser APIs (`window`, `localStorage`) into server components; enforce clear client/server separation.
