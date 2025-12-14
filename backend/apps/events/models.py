from django.db import models

class MarketEvent(models.Model):
    class Industry(models.TextChoices):
        # Must match your Stock industries
        Tech = 'Technology'
        Health = 'Health'
        Finance = 'Finance'
        Energy = 'Energy'
        ConsGood = 'ConsumerGoods'
        # 'GLOBAL' affects all stocks
        GLOBAL = 'GLOBAL', 'Global Market'

    title = models.CharField(max_length=100)
    
    # Who does this affect?
    target_industry = models.CharField(max_length=50, choices=Industry.choices)
    
    # The "Psychological Push"
    # 0.0 = Neutral
    # +0.5 = Strong Buy Pressure (Bots 50% -> 75% likely to buy)
    # -0.5 = Strong Sell Pressure (Bots 50% -> 25% likely to buy)
    sentiment_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_target_industry_display()}: {self.sentiment_score})"