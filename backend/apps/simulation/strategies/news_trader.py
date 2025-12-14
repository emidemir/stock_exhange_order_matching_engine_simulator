import random
from decimal import Decimal
from apps.orders.models import Order
from apps.events.models import MarketEvent

class NewsTraderStrategy:
    def decide(self, bot, stock):
        """
        Returns (Side, Price, Quantity) or None
        """
        # 1. Get Base Sentiment from Events
        # Start neutral (0.5). Events push this to 0.8 (Buy) or 0.2 (Sell)
        sentiment = 0.5 
        active_events = MarketEvent.objects.filter(is_active=True)
        
        for event in active_events:
            if event.target_industry == stock.industry or event.target_industry == 'GLOBAL':
                sentiment += float(event.sentiment_score)

        # 2. Add "Noise" based on Bot's Risk Tolerance
        # A risky bot might misinterpret news (randomness)
        noise = random.uniform(-0.1, 0.1) * float(bot.risk_tolerance)
        final_score = sentiment + noise
        
        # 3. Decision Thresholds
        if final_score > 0.60:
            side = Order.Side.BUY
        elif final_score < 0.40:
            side = Order.Side.SELL
        else:
            return None # Hold

        # 4. PRICING LOGIC (The Safety Mechanism)
        # Fetch the last trade price to anchor our decision
        last_trade = stock.spot_price # Assuming spot_price is updated on trade
        if last_trade <= 0: last_trade = Decimal("100.00")

        # volatility factor: 0.5% to 2% movement max
        volatility = Decimal(random.uniform(0.005, 0.02)) 

        if side == Order.Side.BUY:
            # Bid slightly higher than market to chase, but capped
            price = last_trade * (1 + volatility)
        else:
            # Ask slightly lower than market to dump
            price = last_trade * (1 - volatility)

        # Round to 2 decimals
        price = round(price, 2)
        quantity = random.randint(1, 10) # Keep sizes small for testing

        return side, price, quantity