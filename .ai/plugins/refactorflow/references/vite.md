# Vite (Vite.js) guidance

## Architecture review focus
- Differentiate between application code and build/tooling code.
- Examine Vite config (`vite.config.*`) for logic that properly belongs in the app or infrastructure.
- Check how plugins, aliases, and env handling are organized and whether they leak build concerns into app modules.

## Structure refactor focus
- Keep Vite config focused on build-time concerns (bundling, plugins, aliases) and move business logic out of it.
- Organize app code by feature or domain rather than by purely technical layers when it improves navigability.

  Good:
  ```
  src/
  ├── features/
  │   ├── orders/
  │   │   ├── OrderList.tsx
  │   │   ├── OrderDetail.tsx
  │   │   └── orderApi.ts
  │   └── customers/
  │       ├── CustomerCard.tsx
  │       └── customerApi.ts
  └── shared/
      ├── Button.tsx
      └── formatDate.ts
  ```

  Avoid:
  ```
  src/
  ├── components/   (all components, no ownership)
  ├── hooks/        (all hooks, no ownership)
  ├── utils/        (catch-all)
  └── api/          (flat list of unrelated API modules)
  ```

- Ensure aliases and import paths reflect stable boundaries (e.g., `@features/orders`) rather than generic buckets.
  ```ts
  // vite.config.ts
  resolve: {
    alias: {
      '@features': '/src/features',
      '@shared': '/src/shared',
    }
  }
  ```
- Avoid spreading environment-variable access throughout the app; centralize configuration where possible.
  ```ts
  // src/config.ts — single source for env
  export const config = {
    apiUrl: import.meta.env.VITE_API_URL,
    enableDebug: import.meta.env.VITE_DEBUG === 'true',
  };
  ```

## Simplify refactor focus
- Simplify Vite config by extracting complex plugin or alias setups into small helper modules when needed.
- Reduce conditional build logic where a clearer environment or mode split would suffice.
- Clarify any code that behaves differently in dev vs build by making the mode checks explicit and well-named.
- Avoid hiding significant behavior in inline Vite plugins when a regular module or library would be clearer.
