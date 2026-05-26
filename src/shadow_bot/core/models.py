from pydantic import BaseModel
from typing import Optional

class Market(BaseModel):
    ticker: str
    title: str
    status: str
    close_ts: int
    yes_bid: float
    yes_ask: float
    no_bid: float
    no_ask: float
    no_ask_depth: int
    volume: float
    result: Optional[str] = None

class Opportunity(BaseModel):
    market: Market
    estimated_true_prob: float
    edge: float

class Signal(BaseModel):
    opportunity: Opportunity
    recommended_contracts: int
    expected_value: float

class Order(BaseModel):
    ticker: str
    action: str  # "buy" or "sell"
    side: str    # "yes" or "no"
    count: int
    price: float

class Trade(BaseModel):
    id: Optional[int] = None
    order: Order
    filled_count: int
    filled_price: float
    total_cost: float
    status: str
    realized_pnl: float = 0.0
