import pytest
from unittest.mock import MagicMock
from src.shadow_bot.adapters.kalshi import KalshiAdapter
from src.shadow_bot.core.models import Market

def test_kalshi_adapter_fetches_markets(mocker):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "markets": [
            {
                "ticker": "KX-TEST",
                "title": "Test Market",
                "status": "active",
                "close_time": "2026-05-30T12:00:00Z",
                "yes_bid": 2,
                "yes_ask": 4,
                "no_bid": 96,
                "no_ask": 98,
                "volume": 5000,
                "orderbook": {
                    "no": [
                        [98, 100]  # price, quantity
                    ]
                }
            }
        ],
        "cursor": None
    }
    
    mock_httpx_get = mocker.patch("httpx.Client.get", return_value=mock_response)
    
    adapter = KalshiAdapter(base_url="https://trading-api.kalshi.com/trade-api/v2")
    
    # Act
    markets = list(adapter.get_active_markets())
    
    # Assert
    assert len(markets) == 1
    assert isinstance(markets[0], Market)
    assert markets[0].ticker == "KX-TEST"
    assert markets[0].yes_ask == 0.04
    assert markets[0].no_ask_depth == 100
    assert mock_httpx_get.called

import httpx

def test_kalshi_adapter_uses_connection_pooling(mocker):
    mock_client_class = mocker.patch("src.shadow_bot.adapters.kalshi.httpx.Client", autospec=True)
    mock_client_instance = mock_client_class.return_value.__enter__.return_value
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"markets": [], "cursor": None}
    mock_client_instance.get.return_value = mock_response
    
    adapter = KalshiAdapter()
    list(adapter.get_active_markets())
    
    mock_client_class.assert_called_once()

def test_kalshi_adapter_retries_on_http_errors(mocker):
    mock_client_class = mocker.patch("src.shadow_bot.adapters.kalshi.httpx.Client", autospec=True)
    mock_client_instance = mock_client_class.return_value.__enter__.return_value
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"markets": [], "cursor": None}
    
    mock_client_instance.get.side_effect = [
        httpx.RequestError("Network error", request=MagicMock()),
        httpx.HTTPStatusError("500 Server Error", request=MagicMock(), response=MagicMock()),
        mock_response
    ]
    
    adapter = KalshiAdapter()
    mocker.patch("time.sleep")
    
    list(adapter.get_active_markets())
    
    assert mock_client_instance.get.call_count == 3

def test_kalshi_adapter_pagination_limits(mocker):
    mock_client_class = mocker.patch("src.shadow_bot.adapters.kalshi.httpx.Client", autospec=True)
    mock_client_instance = mock_client_class.return_value.__enter__.return_value
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    
    def mock_json(*args, **kwargs):
        mock_json.calls += 1
        return {"markets": [], "cursor": f"cursor_{mock_json.calls}"}
    mock_json.calls = 0
    mock_response.json.side_effect = mock_json
    mock_client_instance.get.return_value = mock_response
    
    adapter = KalshiAdapter()
    list(adapter.get_active_markets())
    
    assert mock_client_instance.get.call_count == 51

def test_kalshi_adapter_breaks_on_stuck_cursor(mocker):
    mock_client_class = mocker.patch("src.shadow_bot.adapters.kalshi.httpx.Client", autospec=True)
    mock_client_instance = mock_client_class.return_value.__enter__.return_value
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"markets": [], "cursor": "stuck_cursor"}
    mock_client_instance.get.return_value = mock_response
    
    adapter = KalshiAdapter()
    list(adapter.get_active_markets())
    
    assert mock_client_instance.get.call_count == 2

def test_kalshi_adapter_fetches_single_market(mocker):
    mock_client_class = mocker.patch("src.shadow_bot.adapters.kalshi.httpx.Client", autospec=True)
    mock_client_instance = mock_client_class.return_value.__enter__.return_value
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "market": {
            "ticker": "KX-TEST-SINGLE",
            "title": "Test Single Market",
            "status": "finalized",
            "result": "yes",
            "close_time": "2026-05-30T12:00:00Z",
            "yes_bid": 100,
            "yes_ask": 100,
            "no_bid": 0,
            "no_ask": 0,
            "volume": 5000,
            "orderbook": {}
        }
    }
    
    mock_client_instance.get.return_value = mock_response
    
    adapter = KalshiAdapter()
    
    market = adapter.get_market("KX-TEST-SINGLE")
    
    mock_client_instance.get.assert_called_once_with("https://trading-api.kalshi.com/trade-api/v2/markets/KX-TEST-SINGLE", timeout=10.0)
    assert market.ticker == "KX-TEST-SINGLE"
    assert market.status == "finalized"
    assert market.result == "yes"
    assert market.yes_ask == 1.0
