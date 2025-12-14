from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from decimal import Decimal

# Import all models to delete them
from apps.transactions.models import Transaction
from apps.orders.models import Order
from apps.portfolios.models import Portfolio
from apps.events.models import MarketEvent
from apps.simulation.models import Bot
from apps.stocks.models import Stock

User = get_user_model()

class Command(BaseCommand):
    help = 'Wipes the database and restarts the simulation with fresh data.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("⚠️  INITIATING SYSTEM RESET..."))

        # 1. DELETE EVERYTHING (Order matters due to Foreign Keys!)
        # Child records first, then Parents.
        Transaction.objects.all().delete()
        self.stdout.write(" - Deleted Transactions")

        Order.objects.all().delete()
        self.stdout.write(" - Deleted Orders")

        Portfolio.objects.all().delete()
        self.stdout.write(" - Deleted Portfolios")

        MarketEvent.objects.all().delete()
        self.stdout.write(" - Deleted Events")

        Bot.objects.all().delete()
        self.stdout.write(" - Deleted Bots")
        
        # Delete Users (except superusers if you want to keep admin access)
        # For a full reset, we usually delete everyone.
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(" - Deleted Users")

        Stock.objects.all().delete()
        self.stdout.write(" - Deleted Stocks")

        self.stdout.write(self.style.SUCCESS("✅ CLEANUP COMPLETE."))

        # 2. CREATE STOCKS
        self.stdout.write("\n🌱 SEEDING MARKET DATA...")
        
        stocks_data = [
            {"ticker": "TSLA", "name": "Tesla Inc", "industry": Stock.Industry.Tech, "price": "200.00"},
            {"ticker": "AAPL", "name": "Apple Inc", "industry": Stock.Industry.Tech, "price": "150.00"},
            {"ticker": "NVDA", "name": "Nvidia Corp", "industry": Stock.Industry.Tech, "price": "400.00"},
            {"ticker": "XOM",  "name": "Exxon Mobil", "industry": Stock.Industry.Energy, "price": "100.00"},
            {"ticker": "JPM",  "name": "JPMorgan",    "industry": Stock.Industry.Finance, "price": "140.00"},
            {"ticker": "PFE",  "name": "Pfizer",      "industry": Stock.Industry.Health, "price": "40.00"},
        ]

        for s in stocks_data:
            Stock.objects.create(
                ticker=s["ticker"],
                name=s["name"],
                industry=s["industry"],
                spot_price=Decimal(s["price"]),
                open_price=Decimal(s["price"]),
                previous_close_price=Decimal(s["price"]),
                high_price=Decimal(s["price"]),
                low_price=Decimal(s["price"]),
                volume=0
            )
        self.stdout.write(f" - Created {len(stocks_data)} Stocks")

        # 3. RE-DEPLOY BOTS
        self.stdout.write("\n🤖 DEPLOYING BOT ARMY...")
        call_command('init_bots')
        
        self.stdout.write(self.style.SUCCESS("\n🚀 SIMULATION RESET SUCCESSFUL. SYSTEM READY."))