from django.db import models

class Bot(models.Model):
    class Strategy(models.TextChoices):
        NEWS_TRADER = 'NEWS', 'News Trader'       # Reacts to Events
        MARKET_MAKER = 'MM', 'Market Maker'       # Provides Liquidity
        RANDOM_WALK = 'RND', 'Random Walker'      # Adds Noise

    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='bot_profile')
    strategy = models.CharField(max_length=10, choices=Strategy.choices)
    
    # Configuration
    risk_tolerance = models.DecimalField(max_digits=3, decimal_places=2, default=0.5) # 0.0 (Safe) to 1.0 (YOLO)
    trade_frequency = models.IntegerField(default=60) # Seconds between trades
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_strategy_display()})"
