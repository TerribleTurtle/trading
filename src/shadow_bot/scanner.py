import time
from src.shadow_bot.core.ports import MarketDataPort, RepoPort, AlertPort
from src.shadow_bot.core.filter import filter_market
from src.shadow_bot.core.risk import calculate_true_prob, size_position, calculate_kalshi_fee
from src.shadow_bot.core.models import Order, Trade

class Scanner:
    def __init__(self, api: MarketDataPort, repo: RepoPort, alerter: AlertPort):
        self.api = api
        self.repo = repo
        self.alerter = alerter
        
    def run_once(self):
        current_ts = int(time.time())
        bankroll = self.repo.get_bankroll()
        
        for market in self.api.get_active_markets():
            try:
                if filter_market(market, current_ts):
                    true_prob = calculate_true_prob(market.yes_ask)
                    
                    contracts = size_position(
                        bankroll=bankroll,
                        true_prob=true_prob,
                        no_price=market.no_ask,
                        depth=market.no_ask_depth
                    )
                    
                    if contracts > 0:
                        fee = calculate_kalshi_fee(contracts, market.yes_ask, market.no_ask)
                        total_cost = (market.no_ask * contracts) + fee
                        
                        # Shadow execute the trade
                        order = Order(
                            ticker=market.ticker,
                            action="buy",
                            side="no",
                            count=contracts,
                            price=market.no_ask
                        )
                        trade = Trade(
                            order=order,
                            filled_count=contracts,
                            filled_price=market.no_ask,
                            total_cost=total_cost,
                            status="shadow_filled"
                        )
                        
                        self.repo.save_trade(trade)
                        self.repo.deduct_bankroll(total_cost)
                        
                        self.alerter.send_alert(
                            f"SHADOW TRADE EXECUTED: Bought {contracts} NO on {market.ticker} at {market.no_ask}. Cost: ${total_cost:.2f}"
                        )
                        
                        # Update local bankroll for next iterations in the same run
                        bankroll -= total_cost
            except Exception as e:
                pass
