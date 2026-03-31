# syntax=docker/dockerfile:1

# Stage 1: generate requirements.txt using uv
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy project definition and lock file
COPY pyproject.toml uv.lock ./

# Export pinned dependencies (no dev) to requirements.txt
RUN uv export --no-dev --no-emit-project --frozen -o requirements.txt

# Stage 2: production image
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements from builder stage and install with pip
COPY --from=builder /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Default command
CMD ["python", "-m", "ninegag_notion_scraper"]
