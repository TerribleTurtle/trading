from typing import Protocol, List
from src.shadow_bot.core.models import Trade, Market

class ResolverRepoPort(Protocol):
    def get_unresolved_trades(self) -> List[Trade]:
        ...
        
    def update_trade(self, trade: Trade) -> None:
        ...
        
    def add_bankroll(self, amount: float) -> None:
        ...

class ResolverMarketDataPort(Protocol):
    def get_market(self, ticker: str) -> Market:
        ...

class Resolver:
    def __init__(self, repo: ResolverRepoPort, kalshi: ResolverMarketDataPort):
        self.repo = repo
        self.kalshi = kalshi
        
    def resolve_trades(self):
        trades = self.repo.get_unresolved_trades()
        for trade in trades:
            market = self.kalshi.get_market(trade.order.ticker)
            if market.status == "finalized" and market.result:
                won = (trade.order.side == market.result)
                payout = trade.filled_count * 1.0 if won else 0.0
                trade.realized_pnl = payout - trade.total_cost
                trade.status = "resolved"
                
                self.repo.update_trade(trade)
                if payout > 0:
                    self.repo.add_bankroll(payout)
