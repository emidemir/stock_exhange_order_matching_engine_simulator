from django.db import models
from django.conf import settings

class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    stock = models.ForeignKey('stocks.Stock', on_delete=models.CASCADE, related_name='held_in_portfolios')
    
    quantity = models.PositiveIntegerField(default=0)
    
    # Optional: Track average buy price to calculate simulated Profit/Loss
    average_buy_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        # A user cannot have two separate portfolio entries for the same stock
        unique_together = ('user', 'stock')
        indexes = [
            models.Index(fields=['user', 'stock']),
        ]

    def __str__(self):
        return f"{self.user.username} owns {self.quantity} of {self.stock.ticker}"