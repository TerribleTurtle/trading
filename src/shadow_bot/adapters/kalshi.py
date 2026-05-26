import httpx
from typing import Iterator
from datetime import datetime, timezone
from tenacity import retry, stop_after_attempt, wait_exponential
from src.shadow_bot.core.models import Market
from src.shadow_bot.core.ports import MarketDataPort

class KalshiAdapter(MarketDataPort):
    def __init__(self, base_url: str = "https://api.elections.kalshi.com/trade-api/v2"):
        self.base_url = base_url
        # In a real setup, we would add auth headers here.
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch_page(self, cursor: str = None) -> dict:
        with httpx.Client() as client:
            params = {"status": "open", "limit": 100}
            if cursor:
                params["cursor"] = cursor
                
            response = client.get(f"{self.base_url}/markets", params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()

    def get_market(self, ticker: str) -> Market:
        with httpx.Client() as client:
            response = client.get(f"{self.base_url}/markets/{ticker}", timeout=10.0)
            response.raise_for_status()
            data = response.json().get("market", {})
            return self._parse_market(data)

    def _parse_market(self, m_data: dict) -> Market:
        close_time_str = m_data.get("close_time", "")
        close_ts = 0
        if close_time_str:
            close_time_str = close_time_str.replace("Z", "+00:00")
            close_ts = int(datetime.fromisoformat(close_time_str).timestamp())
        
        yes_bid = m_data.get("yes_bid", 0) / 100.0
        yes_ask = m_data.get("yes_ask", 0) / 100.0
        no_bid = m_data.get("no_bid", 0) / 100.0
        no_ask = m_data.get("no_ask", 0) / 100.0
        
        no_ask_depth = 0
        orderbook = m_data.get("orderbook", {})
        no_orders = orderbook.get("no", [])
        if no_orders and len(no_orders) > 0:
            no_ask_depth = no_orders[0][1]
            
        market = Market(
            ticker=m_data.get("ticker", ""),
            title=m_data.get("title", ""),
            status=m_data.get("status", ""),
            close_ts=close_ts,
            yes_bid=yes_bid,
            yes_ask=yes_ask,
            no_bid=no_bid,
            no_ask=no_ask,
            no_ask_depth=no_ask_depth,
            volume=m_data.get("volume", 0)
        )
        if "result" in m_data:
            market.result = m_data["result"]
        return market

    def get_active_markets(self) -> Iterator[Market]:
        cursor = None
        pages = 0
        while pages <= 50:
            data = self._fetch_page(cursor)
            pages += 1
            
            for m_data in data.get("markets", []):
                market = self._parse_market(m_data)
                if market.close_ts > 0:
                    yield market
                
            next_cursor = data.get("cursor")
            if not next_cursor or next_cursor == cursor:
                break
            cursor = next_cursor
