from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.transactions.models import Transaction
from apps.orders.models import Order
from apps.portfolios.models import Portfolio
from apps.events.models import MarketEvent
from apps.simulation.models import Bot
from apps.stocks.models import Stock

User = get_user_model()

class Command(BaseCommand):
    help = 'Debug Reset: 1 Stock, 3 Bots, 1 Major Event.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("⚠️  WIPING DATA FOR DEBUG MODE..."))

        # 1. CLEAN SLATE
        Transaction.objects.all().delete()
        Order.objects.all().delete()
        Portfolio.objects.all().delete()
        MarketEvent.objects.all().delete()
        Bot.objects.all().delete()
        Stock.objects.all().delete()
        # Keep superuser, nuke the rest
        User.objects.filter(is_superuser=False).delete()

        # 2. CREATE 1 STOCK
        self.stdout.write("🌱 Creating Stock: TSLA...")
        stock = Stock.objects.create(
            ticker="TSLA",
            name="Tesla Debug",
            industry=Stock.Industry.Tech,
            spot_price=Decimal("100.00"),
            open_price=Decimal("100.00"),
            previous_close_price=Decimal("100.00"),
            high_price=Decimal("100.00"),
            low_price=Decimal("100.00"),
            volume=0
        )

        # 3. CREATE 1 WHALE (Market Maker)
        # This bot will place SELL orders at $101, $102...
        whale_user = User.objects.create(username="Whale_MM", balance=Decimal("1000000.00"))
        Bot.objects.create(
            user=whale_user,
            strategy=Bot.Strategy.MARKET_MAKER,
            risk_tolerance=Decimal("0.5"),
            is_active=True
        )
        # Give the whale some stock to sell
        Portfolio.objects.create(user=whale_user, stock=stock, quantity=1000, average_buy_price=Decimal("100.00"))

        # 4. CREATE 2 TRADERS (Buyers)
        # These bots will try to BUY because of the event
        for i in range(2):
            user = User.objects.create(username=f"Buyer_{i+1}", balance=Decimal("50000.00"))
            Bot.objects.create(
                user=user,
                strategy=Bot.Strategy.NEWS_TRADER,
                risk_tolerance=Decimal("0.9"), # High risk = Aggressive bidding
                is_active=True
            )

        # 5. CREATE 1 MASSIVE EVENT
        # This ensures the Buyers will bid HIGH (e.g., $102), crossing the Whale's ask ($101).
        MarketEvent.objects.create(
            title="TEST: Super Bull Run",
            target_industry=Stock.Industry.Tech,
            sentiment_score=Decimal("0.80"), # 80% Buy Probability Increase
            is_active=True
        )

        self.stdout.write(self.style.SUCCESS("\n✅ DEBUG ENVIRONMENT READY."))
        self.stdout.write(" -> Monitor 'TSLA'.")
        self.stdout.write(" -> 'Buyer_1' and 'Buyer_2' should aggressively attack 'Whale_MM'.")