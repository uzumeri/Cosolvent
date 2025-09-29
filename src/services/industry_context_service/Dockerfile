# ---- Base stage with PNPM and Corepack ----
FROM node:20-slim AS base

# Set environment variables for pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
# Install a pinned pnpm to avoid Corepack network lookups during build
RUN npm i -g pnpm@10.15.1
WORKDIR /app

# ---- Dependencies stage (only prod deps) ----
FROM base AS prod-deps

COPY pnpm-lock.yaml package.json pnpm-workspace.yaml* ./

# Use Docker cache for node_modules
RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
	pnpm install --prod --frozen-lockfile

# ---- Build stage ----
FROM base AS build

COPY . .

# Use Docker cache for dependencies
RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
	pnpm install --frozen-lockfile

RUN pnpm run build

# ---- Final production image ----
FROM node:20-slim AS final

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
WORKDIR /app
# Install a pinned pnpm runtime for start script
RUN npm i -g pnpm@10.15.1

# Copy built app and only required files
COPY --from=prod-deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package.json pnpm-lock.yaml ./

CMD ["pnpm", "start"]
