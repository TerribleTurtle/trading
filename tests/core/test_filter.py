import time
import pytest
from src.shadow_bot.core.models import Market
from src.shadow_bot.core.filter import filter_market

def test_filter_market_accepts_valid():
    now = int(time.time())
    market = Market(
        ticker="KX-VALID",
        title="Valid Market",
        status="active",
        close_ts=now + 36 * 3600,  # 36 hours from now
        yes_bid=0.03,
        yes_ask=0.05,
        no_bid=0.95,
        no_ask=0.97,
        no_ask_depth=100,
        volume=10000
    )
    assert filter_market(market, current_ts=now) is True

def test_filter_market_rejects_closed():
    now = int(time.time())
    market = Market(
        ticker="KX-CLOSED",
        title="Closed Market",
        status="closed",
        close_ts=now + 36 * 3600,
        yes_bid=0.03,
        yes_ask=0.05,
        no_bid=0.95,
        no_ask=0.97,
        no_ask_depth=100,
        volume=10000
    )
    assert filter_market(market, current_ts=now) is False

def test_filter_market_rejects_fee_trap():
    now = int(time.time())
    market = Market(
        ticker="KX-TRAP",
        title="Fee Trap Market",
        status="active",
        close_ts=now + 36 * 3600,
        yes_bid=0.01,
        yes_ask=0.02,
        no_bid=0.98,
        no_ask=0.99,
        no_ask_depth=100,
        volume=10000
    )
    # YES ask is 2 cents. This is a fee trap.
    assert filter_market(market, current_ts=now) is False

def test_filter_market_rejects_far_expiration():
    now = int(time.time())
    market = Market(
        ticker="KX-FAR",
        title="Far Market",
        status="active",
        close_ts=now + 100 * 3600, # 100 hours
        yes_bid=0.03,
        yes_ask=0.05,
        no_bid=0.95,
        no_ask=0.97,
        no_ask_depth=100,
        volume=10000
    )
    assert filter_market(market, current_ts=now) is False

def test_filter_market_rejects_no_depth():
    now = int(time.time())
    market = Market(
        ticker="KX-NODEPTH",
        title="No Depth Market",
        status="active",
        close_ts=now + 36 * 3600,
        yes_bid=0.03,
        yes_ask=0.05,
        no_bid=0.95,
        no_ask=0.97,
        no_ask_depth=0,
        volume=10000
    )
    assert filter_market(market, current_ts=now) is False

def test_filter_market_rejects_time_decay():
    now = int(time.time())
    # At 36 hours, max yes ask is 6.5c.
    market = Market(
        ticker="KX-DECAY",
        title="Time Decay Market",
        status="active",
        close_ts=now + 36 * 3600,
        yes_bid=0.06,
        yes_ask=0.08, # 8c is > 6.5c
        no_bid=0.90,
        no_ask=0.92,
        no_ask_depth=100,
        volume=10000
    )
    assert filter_market(market, current_ts=now) is False

def test_filter_market_rejects_crossed_books():
    now = int(time.time())
    market = Market(
        ticker="KX-CROSSED",
        title="Crossed Book Market",
        status="active",
        close_ts=now + 36 * 3600,
        yes_bid=0.03,
        yes_ask=0.05,
        no_bid=0.90,
        no_ask=0.92, # 0.05 + 0.92 = 0.97 < 0.99
        no_ask_depth=100,
        volume=10000
    )
    assert filter_market(market, current_ts=now) is False

def test_filter_market_rejects_wide_spread():
    now = int(time.time())
    market = Market(
        ticker="KX-SPREAD",
        title="Wide Spread Market",
        status="active",
        close_ts=now + 36 * 3600,
        yes_bid=0.01,
        yes_ask=0.05, # spread is 0.04 > 0.03
        no_bid=0.95,
        no_ask=0.97,
        no_ask_depth=100,
        volume=10000
    )
    assert filter_market(market, current_ts=now) is False

def test_filter_market_rejects_insufficient_depth():
    now = int(time.time())
    market = Market(
        ticker="KX-DEPTH",
        title="Insufficient Depth Market",
        status="active",
        close_ts=now + 36 * 3600,
        yes_bid=0.03,
        yes_ask=0.05,
        no_bid=0.95,
        no_ask=0.97,
        no_ask_depth=9, # 9 < 10
        volume=10000
    )
    assert filter_market(market, current_ts=now) is False

def test_filter_market_float_precision():
    now = int(time.time())
    # Should pass because round(0.040000000000001, 2) is 0.04, spread is 0.03
    # Spread rule: yes_ask - yes_bid <= 0.03
    # Let's say yes_ask=0.040000000001, yes_bid=0.01
    market = Market(
        ticker="KX-FLOAT",
        title="Float Precision Market",
        status="active",
        close_ts=now + 36 * 3600,
        yes_bid=0.01,
        yes_ask=0.04000000000001,
        no_bid=0.95,
        no_ask=0.97,
        no_ask_depth=100,
        volume=10000
    )
    assert filter_market(market, current_ts=now) is True
