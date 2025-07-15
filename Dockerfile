# Stage 1 – Dependencies and build
FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y gcc build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt
# Copy source and build frontend
COPY . .

# Stage 2 – Production runtime with Gunicorn
FROM python:3.12-slim
RUN adduser --system --no-create-home nonroot
WORKDIR /app
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache /wheels/* && rm -rf /wheels
COPY --from=builder /app .  # includes built Tailwind assets
USER nonroot
EXPOSE 5000
HEALTHCHECK CMD curl --fail http://localhost:5000/healthz || exit 1
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "main:app"]
