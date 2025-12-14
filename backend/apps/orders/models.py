# apps/orders/models.py
from django.db import models
from django.conf import settings

class Order(models.Model):
    class Side(models.TextChoices):
        BUY = 'BUY', 'Buy'   # Stored value, Display value
        SELL = 'SELL', 'Sell'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open' # Changed PENDING to OPEN (standard term)
        PARTIAL = 'PARTIAL', 'Partial'
        FILLED = 'FILLED', 'Filled'
        CANCELLED = 'CANCELLED', 'Cancelled'

    side = models.CharField(max_length=4, choices=Side.choices) # Renamed from order_type
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    
    # Price is REQUIRED for the order book sorting logic
    price = models.DecimalField(max_digits=10, decimal_places=2) 

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    stock = models.ForeignKey('stocks.Stock', on_delete=models.PROTECT, related_name='orders')
    
    # quantity = initial amount user wants
    quantity = models.PositiveIntegerField() 
    
    # remaining_quantity = amount left to fill (starts equal to quantity)
    filled_quantity = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def remaining_quantity(self):
        return self.quantity - self.filled_quantity

    def __str__(self):
        return f"{self.side} {self.stock.ticker} - {self.quantity} @ {self.price}"