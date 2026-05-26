FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (locked for supply chain security)
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Run migrations and start the bot
RUN groupadd -r appuser && useradd -r -m -g appuser appuser
RUN mkdir -p /data && chown -R appuser:appuser /app /data /home/appuser
USER appuser
CMD ["sh", "-c", "uv run alembic upgrade head && uv run python -m src.shadow_bot.main run"]
