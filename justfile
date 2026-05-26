default:
    @just --list

# Format code using Ruff
format:
    uv run ruff check --fix .
    uv run ruff format .

# Check types using Pyright
check:
    uv run pyright .

# Run tests
test:
    uv run pytest tests/ -v

# Initialize database
db-init:
    uv run alembic upgrade head

# Run the CLI
run *args:
    uv run python -m src.shadow_bot.main {{args}}
