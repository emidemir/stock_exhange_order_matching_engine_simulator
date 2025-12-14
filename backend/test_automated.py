import os
import django
import time
from decimal import Decimal

# 1. Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.stocks.models import Stock
from apps.orders.models import Order
from apps.portfolios.models import Portfolio
from apps.transactions.models import Transaction

# IMPORT THE SERVICE DIRECTLY
from services.matching_engine import MatchingEngine

def run_automated_simulation():
    
    print("=== STOCK EXCHANGE SIMULATION (SYNC MODE) ===")

    # --- CLEANUP ---
    print("--- 1. CLEANING OLD DATA ---")
    
    # 1. Delete Transactions FIRST (This removes the protection)
    Transaction.objects.all().delete()
    
    # 2. NOW you can delete the Orders
    Order.objects.all().delete()
    
    # 3. Portfolios can be deleted anytime
    Portfolio.objects.all().delete()
    
    # --- SETUP ---
    print("2. Setting up Assets & Users...")
    tsla, _ = Stock.objects.get_or_create(
        ticker="TSLA", 
        defaults={
            "name": "Tesla", 
            "industry": Stock.Industry.Tech,
            "spot_price": Decimal("200.00"),
            "open_price": Decimal("195.00"),
            "previous_close_price": Decimal("190.00"),
            "high_price": Decimal("205.00"),
            "low_price": Decimal("190.00"),
            "volume": 0
        }
    )

    alice, _ = User.objects.get_or_create(username="Alice")
    alice.balance = Decimal("1000.00")
    alice.save()

    bob, _ = User.objects.get_or_create(username="Bob")
    bob.balance = Decimal("10000.00") 
    bob.save()

    # Give Alice stock
    p_alice, _ = Portfolio.objects.get_or_create(user=alice, stock=tsla)
    p_alice.quantity = 50
    p_alice.save()

    print(f"   Stock: TSLA")
    print(f"   Alice: ${alice.balance} | {p_alice.quantity} shares")
    print(f"   Bob:   ${bob.balance} | 0 shares")

    # --- EXECUTION ---

    print("\n--- 3. EXECUTING ORDERS (ASYNC) ---")
    
    # Alice places a SELL order
    print("-> Alice is placing a SELL order...")
    # This .create() triggers the signal -> redis -> celery
    sell_order = Order.objects.create(
        user=alice, stock=tsla, side=Order.Side.SELL, 
        quantity=10, price=Decimal("200.00"), status=Order.Status.OPEN
    )
    
    time.sleep(1) # Just to ensure order of operations in log view

    # Bob places a BUY order
    print("-> Bob is placing a BUY order...")
    buy_order = Order.objects.create(
        user=bob, stock=tsla, side=Order.Side.BUY, 
        quantity=10, price=Decimal("200.00"), status=Order.Status.OPEN
    )
    
    print("-> Orders submitted to DB. Listening for Celery...")
    
    # Poll for status change (since we can't control Celery speed perfectly)
    for i in range(10):
        print(f"   Checking status... ({i+1}/10)")
        sell_order.refresh_from_db()
        buy_order.refresh_from_db()
        
        if sell_order.status == 'FILLED' and buy_order.status == 'FILLED':
            print("   SUCCESS: Both orders FILLED!")
            break
        time.sleep(1)

    # ... Verify Balances (Same as before) ...

if __name__ == '__main__':
    run_automated_simulation()