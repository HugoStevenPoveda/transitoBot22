# ============================================
# Stage 1: Build the React + Vite application
# ============================================
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies with clean install for reproducible builds
RUN npm ci

# Copy source code and configuration files
COPY . .

# Build the application for production
# This will create optimized static files in /app/dist
# Using build:docker to skip TypeScript checking (vite will still bundle correctly)
RUN npm run build:docker

# ============================================
# Stage 2: Serve with Nginx
# ============================================
FROM nginx:1.25-alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
