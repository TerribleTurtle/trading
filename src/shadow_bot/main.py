import click
import os
import time
from sqlalchemy import create_engine
from src.shadow_bot.scanner import Scanner
from src.shadow_bot.resolver import Resolver
from src.shadow_bot.adapters.kalshi import KalshiAdapter
from src.shadow_bot.adapters.repo_sqlite import SQLiteRepo
from src.shadow_bot.adapters.webhooks.discord import DiscordAlerter

def _build_dependencies():
    api = KalshiAdapter()
    db_path = os.getenv("DB_PATH", "shadow_bot.db")
    engine = create_engine(f"sqlite:///{db_path}")
    repo = SQLiteRepo(engine=engine)
    repo.setup()
    alerter = DiscordAlerter(webhook_url=os.getenv("DISCORD_WEBHOOK_URL", ""))
    return api, repo, alerter

@click.group()
def cli():
    """Kalshi Shadow Trading Bot CLI."""
    pass

@cli.command()
def scan():
    """Run the scanner once."""
    api, repo, alerter = _build_dependencies()
    scanner = Scanner(api=api, repo=repo, alerter=alerter)
    scanner.run_once()

@cli.command()
def resolve():
    """Run the resolver once."""
    api, repo, alerter = _build_dependencies()
    resolver = Resolver(repo=repo, kalshi=api)
    resolver.resolve_trades()

@cli.command()
def run():
    """Run the bot continuously."""
    api, repo, alerter = _build_dependencies()
    scanner = Scanner(api=api, repo=repo, alerter=alerter)
    resolver = Resolver(repo=repo, kalshi=api)
    
    try:
        while True:
            scanner.run_once()
            resolver.resolve_trades()
            time.sleep(60)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    cli()
