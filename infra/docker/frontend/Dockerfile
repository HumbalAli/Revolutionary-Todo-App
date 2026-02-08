# Multi-stage build for the frontend service
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source code and build
COPY frontend/ .
RUN npm run build

# Frontend runtime stage
FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache curl

# Install production dependencies only
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy built application from builder stage
COPY --from=builder /app/.next ./.next
# COPY --from=builder /app/public ./public # Removed because directory is missing
# COPY --from=builder /app/node_modules ./node_modules # Already installed via npm ci --only=production

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

CMD ["npm", "start"]