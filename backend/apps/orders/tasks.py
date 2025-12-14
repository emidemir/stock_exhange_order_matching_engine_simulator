# apps/orders/tasks.py
from celery import shared_task
from services.matching_engine import MatchingEngine
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_order_task(order_id):
    """
    This task is picked up by the Celery Worker.
    It initializes the Matching Engine and processes the specific order.
    """
    try:
        logger.info(f"⚡ Celery: Starting matching for Order #{order_id}")
        engine = MatchingEngine()
        engine.process_order(order_id)
        logger.info(f"✅ Celery: Finished matching for Order #{order_id}")
    except Exception as e:
        logger.error(f"❌ Celery Error processing Order #{order_id}: {e}")
        # Optional: retry logic could go here