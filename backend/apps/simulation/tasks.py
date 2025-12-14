# apps/simulation/tasks.py
from celery import shared_task
from django.db import transaction
from decimal import Decimal
import random

from apps.users.models import User
from apps.stocks.models import Stock
from apps.orders.models import Order
from .models import Bot
from .strategies.news_trader import NewsTraderStrategy
from .strategies.market_maker import MarketMakerStrategy

@shared_task
def run_simulation_cycle():
    """
    Heartbeat of the simulation.
    1. Market Makers provide liquidity (update their bids/asks).
    2. News Traders react to the world.
    """
    print("⏰ SIMULATION: Wake up cycle started...")
    
    # --- 1. MARKET MAKERS (Provide Liquidity First) ---
    mm_bots = Bot.objects.filter(is_active=True, strategy=Bot.Strategy.MARKET_MAKER)
    mm_strategy = MarketMakerStrategy()
    stocks = Stock.objects.all()

    for bot in mm_bots:
        # MMs work on ALL stocks to keep market alive
        for stock in stocks:
            # Clean up OLD orders from this bot (MMs update constantly)
            # In a real engine, we'd modify, but cancelling is safer for this sim
            Order.objects.filter(user=bot.user, stock=stock, status='OPEN').delete()
            
            # Place NEW orders
            orders_data = mm_strategy.create_orders(bot, stock)
            for side, price, qty in orders_data:
                Order.objects.create(
                    user=bot.user,
                    stock=stock,
                    side=side,
                    price=price,
                    quantity=qty,
                    status=Order.Status.OPEN
                )

    # --- 2. NEWS TRADERS (React to Liquidity) ---
    trader_bots = Bot.objects.filter(is_active=True, strategy=Bot.Strategy.NEWS_TRADER)
    trader_strategy = NewsTraderStrategy()

    for bot in trader_bots:
        # Pick one random stock to focus on (too expensive to process all stocks for all bots)
        stock = stocks.order_by('?').first()
        if not stock: continue

        decision = trader_strategy.decide(bot, stock)
        
        if decision:
            side, price, qty = decision
            print(f"   🤖 Bot {bot.user.username} is placing {side} on {stock.ticker} @ ${price}")
            
            Order.objects.create(
                user=bot.user,
                stock=stock,
                side=side,
                price=price,
                quantity=qty,
                status=Order.Status.OPEN
            )
            
    print("✅ SIMULATION: Cycle complete.")