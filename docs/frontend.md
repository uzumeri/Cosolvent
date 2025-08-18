# Frontend

Next.js app for user onboarding, browsing, and match workflows.

## Commands (run in `frontend/`)
- `pnpm install`
- `pnpm dev` — start development server on `http://localhost:3000`.
- `pnpm build && pnpm start` — production build and serve.
- `pnpm lint` / `pnpm format` / `pnpm typecheck` — code quality.

## Configuration
- Copy `.env.example` to `.env` and provide API base URLs and auth config.

## Notes
- Uses React 19, Next 15, and Biome. Place shared libs in `lib/`, providers in `providers/`, and UI in `components/`.
