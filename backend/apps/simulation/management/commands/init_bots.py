from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.simulation.models import Bot
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates dummy bots for simulation'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- INITIALIZING BOT ARMY ---")
        
        # 1. Create Market Makers (The Whales)
        for i in range(5):
            username = f"MarketMaker_{i+1}"
            user, _ = User.objects.get_or_create(username=username)
            user.balance = Decimal("1000000.00") # Infinite money glitch
            user.save()
            
            Bot.objects.get_or_create(
                user=user,
                defaults={'strategy': Bot.Strategy.MARKET_MAKER}
            )
            self.stdout.write(f"Created Whale: {username}")

        # 2. Create News Traders (The Mob)
        for i in range(20):
            username = f"TraderBot_{i+1}"
            user, _ = User.objects.get_or_create(username=username)
            user.balance = Decimal("50000.00")
            user.save()
            
            risk = Decimal(random.uniform(0.1, 0.9)) # Random risk profile
            Bot.objects.get_or_create(
                user=user,
                defaults={
                    'strategy': Bot.Strategy.NEWS_TRADER,
                    'risk_tolerance': risk
                }
            )
        
        self.stdout.write(self.style.SUCCESS("✅ Successfully created 25 bots."))