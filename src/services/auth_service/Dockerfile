# ---- Base stage with PNPM and Corepack ----
FROM node:20-slim AS base

# Set environment variables for pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
WORKDIR /app

# ---- Dependencies stage (only prod deps) ----
FROM base AS prod-deps

COPY pnpm-lock.yaml package.json pnpm-workspace.yaml* ./

# Use Docker cache for node_modules
RUN pnpm install --prod --no-frozen-lockfile

# ---- Build stage ----
FROM base AS build

COPY . .

# Use Docker cache for dependencies
RUN pnpm install --no-frozen-lockfile

RUN pnpm run build

# ---- Final production image ----
FROM node:20-slim AS final

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
WORKDIR /app

# Install pnpm only
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy built app and only required files
COPY --from=prod-deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package.json pnpm-lock.yaml ./

CMD ["pnpm", "start"]
