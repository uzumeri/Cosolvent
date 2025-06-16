# ---- Build stage ----
FROM node:20-alpine AS builder

WORKDIR /app

# Copy only the necessary files
COPY pnpm-lock.yaml package.json tsconfig.json tsup.config.ts ./
COPY pnpm-workspace.yaml ./
COPY src ./src

# Install deps and build
RUN npm install -g pnpm \
  && pnpm install --frozen-lockfile \
  && pnpm run build

# ---- Production stage ----
FROM node:20-alpine

WORKDIR /app

# Copy only the output and runtime files
COPY --from=builder /app/dist ./dist
COPY package.json pnpm-lock.yaml ./

RUN npm install -g pnpm && pnpm install --prod

CMD ["node", "dist/server.js"]
