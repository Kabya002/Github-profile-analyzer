# Stage 1: Tailwind CSS Build
FROM node:18 AS tailwind_builder

WORKDIR /app

# Copy Tailwind-related files
COPY frontend/package.json frontend/tailwind.config.js ./
COPY frontend/src ./src
COPY backend/templates ../backend/templates

# Install and build Tailwind
RUN npm install --legacy-peer-deps
RUN npx tailwindcss -i ./src/input.css -o ./tailwind.css --minify

# Stage 2: Python backend with Gunicorn
FROM python:3.12-slim

# Creates a non-root user for security
RUN adduser --system --no-create-home nonroot

WORKDIR /app

# Installs system dependencies
RUN apt-get update && apt-get install -y build-essential curl git && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/ /app/

# Copy built Tailwind output
COPY --from=tailwind_builder /app/tailwind.css /app/static/css/tailwind.css

# Installs Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER nonroot

# Set Render port
EXPOSE 5000

# Health check for Render
HEALTHCHECK CMD curl --fail http://localhost:5000/healthz || exit 1

# Run with Gunicorn
CMD ["gunicorn", "--workers=2", "--bind=0.0.0.0:5000", "main:app"]
