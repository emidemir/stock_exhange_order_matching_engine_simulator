import os
import django
import random
from decimal import Decimal

# 1. Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.stocks.models import Stock
from apps.events.models import MarketEvent
from apps.simulation.models import Bot
from apps.simulation.strategies.news_trader import NewsTraderStrategy
from apps.simulation.strategies.market_maker import MarketMakerStrategy

def test_bot_logic():
    print("=== TESTING BOT BRAIN LOGIC ===")

    # --- SETUP ---
    print("\n1. creating Lab Environment...")
    
    # Create a Test Stock
    stock, _ = Stock.objects.get_or_create(
        ticker="TEST", 
        defaults={
            "name": "Test Corp", 
            "industry": Stock.Industry.Tech,
            "spot_price": Decimal("100.00"),
            "open_price": Decimal("100.00"),
            "previous_close_price": Decimal("100.00"),
            "high_price": Decimal("100.00"),
            "low_price": Decimal("100.00"),
            "volume": 0
        }
    )
    # Reset price to known anchor
    stock.spot_price = Decimal("100.00")
    stock.save()

    # Create a Bot User
    user, _ = User.objects.get_or_create(username="TestBot")
    
    # Create the Bot Profile
    bot, _ = Bot.objects.get_or_create(
        user=user,
        defaults={
            'strategy': Bot.Strategy.NEWS_TRADER,
            'risk_tolerance': Decimal("0.5") # Moderate risk
        }
    )

    # Clear old events
    MarketEvent.objects.all().delete()

    strategy = NewsTraderStrategy()

    # --- SCENARIO 1: NEUTRAL MARKET ---
    print("\n2. Scenario: Neutral Market (No Events)")
    decision = strategy.decide(bot, stock)
    
    if decision:
        side, price, qty = decision
        print(f"   -> Bot decided: {side} @ ${price}")
        # Logic Check: Price should be close to $100
        assert 98.00 <= price <= 102.00, f"Price {price} is too volatile for neutral market!"
    else:
        print("   -> Bot decided: HOLD (Correct behavior for neutral)")

    # --- SCENARIO 2: GOOD NEWS (Tech Boom) ---
    print("\n3. Scenario: POSITIVE Event (Sentiment +0.40)")
    MarketEvent.objects.create(
        title="AI Breakthrough",
        target_industry=Stock.Industry.Tech,
        sentiment_score=Decimal("0.40"),
        is_active=True
    )
    
    # Run 5 times to check probability bias
    buy_count = 0
    print("   -> Running 5 trials...")
    for i in range(5):
        decision = strategy.decide(bot, stock)
        if decision and decision[0] == 'BUY':
            buy_count += 1
            print(f"      Trial {i+1}: BUY @ ${decision[1]} (Qty: {decision[2]})")
            
            # CRITICAL CHECK: Ensure price is NOT exploding
            # A sane bot should bid $100 - $102, not $200
            assert decision[1] < 105.00, "FATAL: Bot is bidding way too high!"
    
    print(f"   -> Result: Bot bought {buy_count}/5 times.")
    
    # --- SCENARIO 3: MARKET MAKER CHECK ---
    print("\n4. Scenario: Market Maker Logic")
    mm_strat = MarketMakerStrategy()
    orders = mm_strat.create_orders(bot, stock)
    
    bid = orders[0] # (BUY, Price, Qty)
    ask = orders[1] # (SELL, Price, Qty)
    
    print(f"   -> MM Bid: ${bid[1]}")
    print(f"   -> MM Ask: ${ask[1]}")
    
    # Logic Check: Bid should be lower than Ask (Spread)
    assert bid[1] < ask[1], "FATAL: Market Maker has crossed spread (Arbitrage opportunity!)"
    assert bid[1] < 100.00 < ask[1], "FATAL: MM is not straddling the spot price"

    print("\n✅ ALL LOGIC TESTS PASSED. SAFE TO DEPLOY.")

if __name__ == '__main__':
    test_bot_logic()