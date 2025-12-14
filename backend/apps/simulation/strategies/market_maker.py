from decimal import Decimal
from apps.orders.models import Order

class MarketMakerStrategy:
    def create_orders(self, bot, stock):
        center_price = stock.spot_price
        
        # OLD: spread = Decimal("0.05")  (Gap is too wide!)
        # NEW: Tighten the spread to 1%
        spread = Decimal("0.01") 

        buy_price = round(center_price * (1 - spread/2), 2)
        sell_price = round(center_price * (1 + spread/2), 2)

        return [
            (Order.Side.BUY, buy_price, 100),
            (Order.Side.SELL, sell_price, 100)
        ]