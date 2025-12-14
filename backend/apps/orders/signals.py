# apps/orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Order
from .tasks import process_order_task

@receiver(post_save, sender=Order)
def trigger_matching_engine(sender, instance, created, **kwargs):
    """
    When an Order is saved:
    1. Check if it is valid for matching (OPEN or PARTIAL).
    2. Wait for the DB transaction to commit.
    3. Send the task to Celery/Redis.
    """
    if instance.status in [Order.Status.OPEN, Order.Status.PARTIAL]:
        # We pass the ID, not the object, to keep the payload small
        transaction.on_commit(lambda: process_order_task.delay(instance.id))