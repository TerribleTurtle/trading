import pytest
from sqlalchemy import create_engine
from src.shadow_bot.adapters.repo_sqlite import SQLiteRepo
from src.shadow_bot.core.models import Order, Trade

def test_repo_saves_and_retrieves_bankroll():
    # Arrange
    engine = create_engine("sqlite:///:memory:")
    repo = SQLiteRepo(engine)
    repo.setup()
    
    # Act / Assert
    # Default bankroll is 0
    assert repo.get_bankroll() == 0.0
    
    repo.add_bankroll(50.0)
    assert repo.get_bankroll() == 50.0
    
    repo.deduct_bankroll(10.5)
    assert repo.get_bankroll() == 39.5

def test_repo_saves_trade():
    # Arrange
    engine = create_engine("sqlite:///:memory:")
    repo = SQLiteRepo(engine)
    repo.setup()
    
    order = Order(ticker="KX-123", action="buy", side="no", count=10, price=0.90)
    trade = Trade(order=order, filled_count=10, filled_price=0.90, total_cost=9.50, status="filled")
    
    # Act
    repo.save_trade(trade)
    
    # Assert
    trades = repo.get_all_trades()
    assert len(trades) == 1
    assert trades[0].order.ticker == "KX-123"
    assert trades[0].total_cost == 9.50

def test_repo_gets_unresolved_trades():
    engine = create_engine("sqlite:///:memory:")
    repo = SQLiteRepo(engine)
    repo.setup()
    
    order1 = Order(ticker="KX-1", action="buy", side="yes", count=1, price=0.5)
    trade1 = Trade(order=order1, filled_count=1, filled_price=0.5, total_cost=0.5, status="unresolved")
    repo.save_trade(trade1)
    
    order2 = Order(ticker="KX-2", action="buy", side="no", count=1, price=0.5)
    trade2 = Trade(order=order2, filled_count=1, filled_price=0.5, total_cost=0.5, status="resolved")
    repo.save_trade(trade2)
    
    unresolved = repo.get_unresolved_trades()
    assert len(unresolved) == 1
    assert unresolved[0].order.ticker == "KX-1"

def test_repo_updates_trade():
    engine = create_engine("sqlite:///:memory:")
    repo = SQLiteRepo(engine)
    repo.setup()
    
    order = Order(ticker="KX-1", action="buy", side="yes", count=10, price=0.5)
    trade = Trade(order=order, filled_count=10, filled_price=0.5, total_cost=5.0, status="unresolved", realized_pnl=0.0)
    repo.save_trade(trade)
    
    saved_trades = repo.get_all_trades()
    saved_trade = saved_trades[0]
    
    saved_trade.status = "resolved"
    saved_trade.realized_pnl = 5.0
    repo.update_trade(saved_trade)
    
    updated_trades = repo.get_all_trades()
    assert updated_trades[0].status == "resolved"
    assert updated_trades[0].realized_pnl == 5.0
