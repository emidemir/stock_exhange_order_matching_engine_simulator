# backend/services/bot_brain.py
import random
from decimal import Decimal
from apps.events.models import MarketEvent
from apps.stocks.models import Stock

class BotBrain:
    def decide_action(self, stock):
        """
        Returns a tuple: (Side, Price_Multiplier)
        e.g., ('BUY', 1.02) means Buy at 102% of current market price.
        """
        # 1. Base Buy Probability (50%)
        buy_probability = 0.50
        
        # 2. Adjust for Events
        events = MarketEvent.objects.filter(is_active=True)
        for event in events:
            if event.target_industry == stock.industry or event.target_industry == 'GLOBAL':
                # Convert decimal to float for probability math
                buy_probability += float(event.sentiment_score)
        
        # Clamp probability between 5% and 95% (always some contrarians)
        buy_probability = max(0.05, min(0.95, buy_probability))
        
        # 3. Roll the Dice
        action = 'BUY' if random.random() < buy_probability else 'SELL'
        
        # 4. Determine Aggressiveness (Price)
        # Random variance so bots don't all bid the exact same penny
        volatility = random.uniform(0.00, 0.02) # 0% to 2% variance
        
        if action == 'BUY':
            # If I want to buy, I might bid slightly HIGHER to get filled fast
            # Sentiment adds urgency. High Buy Prob = Higher Bids.
            urgency = (buy_probability - 0.50) if buy_probability > 0.5 else 0
            price_multiplier = 1.0 + volatility + (urgency * 0.1)
            
        else: # SELL
            # If I want to sell, I might ask slightly LOWER to dump fast
            # Low Buy Prob = High Sell Pressure = Lower Asks.
            panic = (0.50 - buy_probability) if buy_probability < 0.5 else 0
            price_multiplier = 1.0 - volatility - (panic * 0.1)

        return action, Decimal(str(round(price_multiplier, 4)))