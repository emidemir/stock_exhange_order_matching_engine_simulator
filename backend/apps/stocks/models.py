from django.db import models

class Stock(models.Model):
    # General
    name = models.CharField(max_length=50)
    ticker = models.SlugField()

    class Industry(models.TextChoices):
        Tech = 'Technology'
        Health = 'Health'
        Finance = 'Finance'
        Energy = 'Energy'
        ConsGood = 'ConsumerGoods'
    industry = models.CharField(max_length=15, choices=Industry.choices)

    # Price related
    spot_price = models.DecimalField(max_digits=5, decimal_places=2)
    open_price = models.DecimalField(max_digits=5, decimal_places=2)
    previous_close_price = models.DecimalField(max_digits=5, decimal_places=2)
    high_price = models.DecimalField(max_digits=5, decimal_places=2)
    low_price = models.DecimalField(max_digits=5, decimal_places=2)

    # Market related
    volume = models.BigIntegerField()

    # Time related
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)