# -------- Base Image with PNPM --------
FROM node:18-alpine AS base
RUN npm install -g pnpm
WORKDIR /app

# -------- Dependencies Layer --------
FROM base AS deps
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# -------- Build Layer --------
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

# -------- Runtime / Runner Layer --------
FROM node:18-alpine AS runner
ENV NODE_ENV=production
WORKDIR /app

# Optional: only include necessary runtime deps
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./package.json

# Expose app port
EXPOSE 3000

# Start the production server
CMD ["node_modules/.bin/next", "start"]
