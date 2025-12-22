FROM python:3.12-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
ENV PYTHONPATH=/app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy service pyproject.toml and install deps
COPY services/manager/pyproject.toml ./
RUN uv sync --frozen --no-install-project || uv sync --no-install-project

# Copy only what's needed for this service
COPY config.py .
COPY agents/__init__.py agents/
COPY agents/models.py agents/
COPY agents/manager.py agents/
COPY agents/apps/__init__.py agents/apps/
COPY agents/apps/manager_app.py agents/apps/

EXPOSE 8080
CMD ["uv", "run", "uvicorn", "agents.apps.manager_app:app", "--host", "0.0.0.0", "--port", "8080"]

