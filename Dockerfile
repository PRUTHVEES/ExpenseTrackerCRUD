# ==============================================================================
# Multi-Stage Dockerfile for Smart Expense Tracker
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Test Runner (Automated CI Quality Gate)
# ------------------------------------------------------------------------------
FROM python:3.13-slim AS test

WORKDIR /app

# Copy dependency specifications and pytest configuration
COPY requirements.txt pytest.ini ./

# Install unit & DOM testing dependencies
RUN pip install --no-cache-dir pytest beautifulsoup4

# Copy source code and test suite
COPY . .

# Run unit and DOM contract tests (103 tests)
RUN pytest -m "unit or dom"

# ------------------------------------------------------------------------------
# Stage 2: Production Web Server
# ------------------------------------------------------------------------------
FROM nginx:alpine AS production

# Set working directory
WORKDIR /usr/share/nginx/html

# Remove default nginx static assets
RUN rm -rf ./*

# Copy custom Nginx web server configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy production static assets
COPY index.html style.css app.js ./

# Expose HTTP port 80
EXPOSE 80

# Health check to ensure Nginx is actively responding
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://127.0.0.1/health || exit 1

# Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
