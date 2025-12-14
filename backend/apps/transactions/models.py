# apps/transactions/models.py
from django.db import models
from django.conf import settings # To access your User model

class Transaction(models.Model):
    # Relate to the specific assets/users
    stock = models.ForeignKey('stocks.Stock', on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buys')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sells')
    
    # Link back to the original orders for audit trails
    buy_order = models.ForeignKey('orders.Order', on_delete=models.PROTECT, related_name='buy_transactions')
    sell_order = models.ForeignKey('orders.Order', on_delete=models.PROTECT, related_name='sell_transactions')
    
    # Trade details
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock.symbol}: {self.quantity} @ {self.price}"