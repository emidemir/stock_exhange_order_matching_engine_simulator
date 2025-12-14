from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model for the Stock Exchange.
    Extends Django's default auth system to include financial data.
    """
    # Financial Information
    # Using DecimalField is crucial for money to avoid floating point errors
    balance = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0.00,
        help_text="Current cash balance available for trading"
    )

    # Optional: Identity/KYC (Know Your Customer) fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Optional: User Type (if you want to distinguish regular traders from admins/bots)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} (${self.balance})"

    class Meta:
        db_table = 'users'