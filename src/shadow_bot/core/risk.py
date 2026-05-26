import math

def calculate_kalshi_fee(contracts: int, yes_price: float, no_price: float) -> float:
    """
    Calculate the Kalshi fee for a trade.
    Kalshi charges 7% of expected profit, rounded up to the nearest cent.
    If we are buying NO at no_price, expected profit is (1 - no_price).
    """
    if contracts <= 0:
        return 0.0
    
    # expected profit in cents, using int to avoid precision issues
    profit_per_contract_cents = int(round((1.0 - no_price) * 100))
    expected_profit_cents = profit_per_contract_cents * contracts
    
    # 7% of expected profit, ceil to nearest cent
    # multiply by 7 and divide by 100 to avoid float precision on 0.07 * 300
    total_fee_cents = math.ceil((7 * expected_profit_cents) / 100.0)
    
    # Kalshi caps the fee at $0.07 per contract
    total_fee_cents = min(total_fee_cents, 7 * contracts)
    
    return round(total_fee_cents / 100.0, 2)

def calculate_true_prob(implied_yes_prob: float) -> float:
    """
    Discount the implied probability to estimate the true probability.
    For Favorite-Longshot Bias, extreme longshots are overpriced.
    """
    if implied_yes_prob <= 0.10:
        return implied_yes_prob * 0.5
    return implied_yes_prob

def calculate_kelly_fraction(true_yes_prob: float, no_price: float, fee_per_contract: float) -> float:
    """
    Calculate the Kelly fraction for buying NO.
    """
    # Probability we win (YES doesn't happen)
    p = 1.0 - true_yes_prob
    q = 1.0 - p
    
    # Net odds = (payout - cost) / cost
    # Payout is 1.0, cost is no_price + fee
    cost = no_price + fee_per_contract
    payout = 1.0
    net_profit = payout - cost
    
    if cost <= 0 or net_profit <= 0:
        return 0.0
        
    b = net_profit / cost
    
    if b <= 0:
        return 0.0
        
    f_star = (b * p - q) / b
    return max(0.0, f_star)

def size_position(bankroll: float, true_prob: float, no_price: float, depth: int, kelly_fraction: float = 0.25) -> int:
    """
    Calculate the number of contracts to buy, applying all financial safety limits.
    """
    MIN_BANKROLL = 10.0
    MAX_BANKROLL_PERCENT_PER_TRADE = 0.10
    
    if bankroll < MIN_BANKROLL:
        return 0
        
    exact_fee_per_contract = calculate_kalshi_fee(1, 1.0 - no_price, no_price)
    cost_per_contract = no_price + exact_fee_per_contract
    
    # Calculate unrounded, asymptotic fee for Kelly purposes
    asymptotic_fee_per_contract = min(0.07 * (1.0 - no_price), 0.07)
    
    # Calculate optimal kelly fraction
    f_star = calculate_kelly_fraction(true_prob, no_price, asymptotic_fee_per_contract)
    target_fraction = f_star * kelly_fraction
    
    # Cap at max bankroll percentage
    target_fraction = min(target_fraction, MAX_BANKROLL_PERCENT_PER_TRADE)
    
    if target_fraction <= 0:
        return 0
        
    target_investment = bankroll * target_fraction
    
    # Calculate raw contracts using integer cent division to avoid float precision issues
    # Note: Added round() to handle cases where cost_per_contract * 100 evaluates to e.g. 14.000000000000002
    raw_contracts = int(round(target_investment * 100)) // int(round(cost_per_contract * 100))
    
    # Cap at available orderbook depth
    final_contracts = min(raw_contracts, depth)
    
    return final_contracts
