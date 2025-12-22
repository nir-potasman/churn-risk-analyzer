FROM python:3.12-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
ENV PYTHONPATH=/app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy service pyproject.toml and install deps
COPY services/frontend/pyproject.toml ./
RUN uv sync --frozen --no-install-project || uv sync --no-install-project

# Copy only what's needed for this service
COPY frontend/ frontend/

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/health')" || exit 1

CMD ["uv", "run", "uvicorn", "frontend.main:app", "--host", "0.0.0.0", "--port", "3000"]

