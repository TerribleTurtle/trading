# Kalshi Shadow Trading Bot

A high-performance, strictly-typed trading bot for exploiting the Favorite-Longshot Bias on Kalshi, built using Hexagonal Architecture.

## Features
- **Clean Architecture:** Core logic is 100% isolated from Kalshi APIs and SQLite.
- **Safety First:** Hardcoded drawdown limits, infinite loop protection, and a `DRY_RUN=True` default.
- **Modern Stack:** Built with `uv`, `Ruff`, `Pyright` (strict mode), `Pydantic`, and `SQLAlchemy 2.0`.
- **Kelly Criterion:** Mathematically sound position sizing bounded by orderbook depth.

## Local Development
1. Install [uv](https://github.com/astral-sh/uv).
2. Clone the repository.
3. Run `uv sync --all-extras --dev` to install dependencies.
4. Copy `.env.example` to `.env`.
5. Run `just check` and `just format` to verify tooling.
