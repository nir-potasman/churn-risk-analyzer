FROM python:3.12-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv and uvx
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY --from=ghcr.io/astral-sh/uv:latest /uvx /bin/uvx

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Set up environment
WORKDIR /app
ENV PYTHONPATH=/app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Change ownership of /app to appuser
RUN chown appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy project definition
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy source code
COPY --chown=appuser:appuser . .

# Install the project itself
RUN uv sync --frozen

# Default port
EXPOSE 8080 8000 8001 8002

# The command will be overridden by docker-compose
CMD ["uv", "run", "uvicorn", "agents.apps.manager_app:a2a_app", "--host", "0.0.0.0", "--port", "8080"]
