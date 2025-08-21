# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Set environment variables
ENV POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION

# Add Poetry to PATH
ENV PATH="$PATH:/root/.local/bin"

# Set workdir
WORKDIR /app

# Copy only requirements to cache dependencies
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Copy the rest of the code
COPY . .

# Default command
CMD ["python", "-m", "ninegag_notion_scraper"]
