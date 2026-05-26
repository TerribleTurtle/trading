from typing import Protocol, List, Iterator
from src.shadow_bot.core.models import Market, Trade

class MarketDataPort(Protocol):
    def get_active_markets(self) -> Iterator[Market]:
        ...
        
    def get_market(self, ticker: str) -> Market:
        ...

class RepoPort(Protocol):
    def save_trade(self, trade: Trade) -> None:
        ...
        
    def update_trade(self, trade: Trade) -> None:
        ...
        
    def get_unresolved_trades(self) -> List[Trade]:
        ...
        
    def get_bankroll(self) -> float:
        ...
        
    def deduct_bankroll(self, amount: float) -> None:
        ...
        
    def add_bankroll(self, amount: float) -> None:
        ...

class AlertPort(Protocol):
    def send_alert(self, msg: str) -> None:
        ...
