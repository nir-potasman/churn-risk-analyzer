FROM python:3.12-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
ENV PYTHONPATH=/app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy service pyproject.toml and install deps
COPY services/transcript/pyproject.toml ./
RUN uv sync --frozen --no-install-project || uv sync --no-install-project

# Copy only what's needed for this service
COPY config.py .
COPY agents/__init__.py agents/
COPY agents/models.py agents/
COPY agents/call_transcripts_agent.py agents/
COPY agents/tools/__init__.py agents/tools/
COPY agents/tools/redshift_tools.py agents/tools/
COPY agents/apps/__init__.py agents/apps/
COPY agents/apps/transcript_app.py agents/apps/

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

CMD ["uv", "run", "uvicorn", "agents.apps.transcript_app:app", "--host", "0.0.0.0", "--port", "8001"]

