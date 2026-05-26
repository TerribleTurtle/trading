from src.shadow_bot.core.models import Market

def filter_market(market: Market, current_ts: int) -> bool:
    """
    Filter markets based on the Favorite-Longshot Bias strategy rules.
    """
    # Rule 1: Market must be active
    if market.status != "active":
        return False
        
    # Rule 2: Minimum depth available ($10 worth)
    if market.no_ask_depth < 10:
        return False
        
    # Rule 3: Time to expiration between 24 and 48 hours
    hours_to_close = (market.close_ts - current_ts) / 3600.0
    if not (24.0 <= hours_to_close <= 48.0):
        return False
        
    # Rule 4: Dynamic Time-Decay Band (3c to 10c YES ask)
    # Maximum YES ask linearly decays from 10c at 48 hours to 3c at 24 hours.
    max_yes_ask = 0.03 + (0.10 - 0.03) * ((hours_to_close - 24.0) / 24.0)
    
    if not (0.03 <= round(market.yes_ask, 2) <= round(max_yes_ask, 2)):
        return False
        
    # Corresponding NO ask must be logical (90c to 97c)
    if not (0.90 <= round(market.no_ask, 2) <= 0.97):
        return False
        
    # Rule 5: Ensure yes_ask + no_ask >= 0.99 (avoid crossed books)
    if round(market.yes_ask + market.no_ask, 2) < 0.99:
        return False
        
    # Rule 6: Ensure yes_ask - yes_bid <= 0.03 (avoid wide spreads)
    if round(market.yes_ask - market.yes_bid, 2) > 0.03:
        return False
        
    return True
