import time
import pytest
from unittest.mock import MagicMock
from src.shadow_bot.scanner import Scanner
from src.shadow_bot.core.models import Market
from src.shadow_bot.core.ports import MarketDataPort, RepoPort, AlertPort

def test_scanner_executes_trades_on_opportunities():
    # Arrange
    mock_api = MagicMock(spec=MarketDataPort)
    mock_repo = MagicMock(spec=RepoPort)
    mock_alert = MagicMock(spec=AlertPort)
    
    # Provide one valid market and one invalid market
    now = int(time.time())
    valid_market = Market(
        ticker="KX-GOOD",
        title="Good Market",
        status="active",
        close_ts=now + 36 * 3600,
        yes_bid=0.03, yes_ask=0.04,
        no_bid=0.96, no_ask=0.96,
        no_ask_depth=100,
        volume=10000
    )
    invalid_market = Market(
        ticker="KX-BAD",
        title="Bad Market",
        status="closed",
        close_ts=now + 36 * 3600,
        yes_bid=0.50, yes_ask=0.55,
        no_bid=0.45, no_ask=0.50,
        no_ask_depth=100,
        volume=10000
    )
    mock_api.get_active_markets.return_value = [valid_market, invalid_market]
    mock_repo.get_bankroll.return_value = 50.0
    
    scanner = Scanner(api=mock_api, repo=mock_repo, alerter=mock_alert)
    
    # Act
    scanner.run_once()
    
    # Assert
    # Filter should only accept the valid market.
    # Risk should size the valid market > 0.
    # Then it should save the trade to the repo.
    assert mock_repo.save_trade.call_count == 1
    
    # Check that bankroll was deducted
    assert mock_repo.deduct_bankroll.call_count == 1
    
    # Check that alert was sent
    assert mock_alert.send_alert.call_count == 1

def test_scanner_continues_on_market_processing_error(mocker):
    mock_api = MagicMock(spec=MarketDataPort)
    mock_repo = MagicMock(spec=RepoPort)
    mock_alert = MagicMock(spec=AlertPort)
    
    now = int(time.time())
    m1 = Market(ticker="M1", title="", status="active", close_ts=now+3600, yes_bid=0.1, yes_ask=0.1, no_bid=0.9, no_ask=0.9, no_ask_depth=10, volume=100)
    m2 = Market(ticker="M2", title="", status="active", close_ts=now+3600, yes_bid=0.1, yes_ask=0.1, no_bid=0.9, no_ask=0.9, no_ask_depth=10, volume=100)
    m3 = Market(ticker="M3", title="", status="active", close_ts=now+3600, yes_bid=0.1, yes_ask=0.1, no_bid=0.9, no_ask=0.9, no_ask_depth=10, volume=100)
    
    mock_api.get_active_markets.return_value = [m1, m2, m3]
    mock_repo.get_bankroll.return_value = 50.0
    
    mock_filter = mocker.patch("src.shadow_bot.scanner.filter_market")
    mock_filter.side_effect = [True, Exception("Crash"), True]
    
    mocker.patch("src.shadow_bot.scanner.calculate_true_prob", return_value=0.5)
    mocker.patch("src.shadow_bot.scanner.size_position", return_value=1)
    
    scanner = Scanner(api=mock_api, repo=mock_repo, alerter=mock_alert)
    scanner.run_once()
    
    assert mock_repo.save_trade.call_count == 2
