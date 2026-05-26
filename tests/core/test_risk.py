import pytest
from src.shadow_bot.core.risk import (
    calculate_kalshi_fee,
    calculate_true_prob,
    calculate_kelly_fraction,
    size_position
)

def test_calculate_kalshi_fee():
    fee = calculate_kalshi_fee(contracts=100, yes_price=0.03, no_price=0.97)
    assert fee == 0.21

def test_calculate_kalshi_fee_cap():
    # Force expected profit to be large (invalid price, just to test cap)
    fee = calculate_kalshi_fee(contracts=10, yes_price=0.0, no_price=-1.0)
    assert fee <= 0.70

def test_calculate_true_prob():
    assert calculate_true_prob(0.03) == 0.015
    assert calculate_true_prob(0.10) == 0.05
    assert calculate_true_prob(0.25) == 0.25
    assert calculate_true_prob(0.50) == 0.50

def test_calculate_kelly_fraction():
    frac = calculate_kelly_fraction(true_yes_prob=0.01, no_price=0.90, fee_per_contract=0.007)
    assert round(frac, 4) == 0.8925

def test_size_position_asymptotic_fee():
    # We need a case where the asymptotic fee results in a fraction < 0.10,
    # but the old 1c fee results in a much smaller (or negative) fraction!
    # Let's say true prob = 0.02, no_price = 0.97.
    # Asymptotic fee: 0.07 * (1.0 - 0.97) = 0.0021
    # Cost = 0.9721. Net = 0.0279. b = 0.0287.
    # p = 0.98, q = 0.02
    # f_star = (0.0287 * 0.98 - 0.02) / 0.0287 = (0.028126 - 0.02) / 0.0287 = 0.283.
    # target_fraction = 0.283 * 0.25 = 0.07075
    # bankroll = 100 -> target_investment = 7.075
    # real cost = 0.98 (0.97 + 0.01). 7.075 / 0.98 = 7.21 -> 7 contracts.
    
    # If using old code, fee=0.01: cost=0.98, net=0.02, b=0.0204.
    # p=0.98, q=0.02. f_star = (0.0204 * 0.98 - 0.02) / 0.0204 = (0.019992 - 0.02) -> negative!
    # f_star = 0.0 -> target_fraction = 0 -> 0 contracts.
    
    contracts = size_position(bankroll=100.0, true_prob=0.02, no_price=0.97, depth=100, kelly_fraction=0.25)
    assert contracts == 7

def test_size_position_float_truncation():
    # If we use int division: target_investment * 100 // cost_per_contract * 100
    # Say we cap at 0.10. bankroll = 140.0 -> target = 14.0.
    # no_price = 0.07. expected profit 93. fee = 7c = 0.07.
    # real cost = 0.14.
    # 14.0 / 0.14 in floats is 99.99999999999999. old code floor(99.99999) = 99.
    # With int division: 1400 // 14 = 100.
    contracts = size_position(bankroll=140.0, true_prob=0.001, no_price=0.07, depth=1000, kelly_fraction=0.25)
    assert contracts == 100

def test_minimum_bankroll_floor():
    contracts = size_position(bankroll=5.0, true_prob=0.05, no_price=0.90, depth=100, kelly_fraction=0.25)
    assert contracts == 0
