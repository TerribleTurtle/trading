import pytest
from unittest.mock import Mock
from src.shadow_bot.core.models import Trade, Order, Market

def test_resolver_updates_resolved_trade_and_pnl():
    from src.shadow_bot.resolver import Resolver
    
    repo = Mock()
    kalshi = Mock()
    
    order = Order(ticker="TEST-123", action="buy", side="yes", count=10, price=0.40)
    trade = Trade(order=order, filled_count=10, filled_price=0.40, total_cost=4.0, status="unresolved")
    
    repo.get_unresolved_trades.return_value = [trade]
    
    market = Market(
        ticker="TEST-123",
        title="Test",
        status="finalized",
        result="yes",  # assuming we add this
        close_ts=123,
        yes_bid=0.0,
        yes_ask=0.0,
        no_bid=0.0,
        no_ask=0.0,
        no_ask_depth=0,
        volume=100
    )
    kalshi.get_market.return_value = market
    
    resolver = Resolver(repo=repo, kalshi=kalshi)
    resolver.resolve_trades()
    
    repo.get_unresolved_trades.assert_called_once()
    kalshi.get_market.assert_called_once_with("TEST-123")
    
    # Trade should be updated to resolved and P&L calculated
    # Realized P&L = 10 * 1.0 (win) - 4.0 = +6.0
    assert trade.status == "resolved"
    assert trade.realized_pnl == 6.0
    repo.update_trade.assert_called_once_with(trade)
    repo.add_bankroll.assert_called_once_with(10.0) # wait, bankroll gets the gross payout (10 contracts * $1), or do we just track PNL?
    # Actually, PnL is 6.0, bankroll should just receive the gross amount $10.0 if won, or nothing if lost, since cost was deducted at order time.
