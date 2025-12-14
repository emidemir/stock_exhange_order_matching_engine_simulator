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

def run_simulation():
    print("=== STOCK EXCHANGE SIMULATION (SYNC MODE) ===")

    # --- CLEANUP ---
    print("\n1. Cleaning DB...")
    Order.objects.all().delete()
    Transaction.objects.all().delete()
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
    print("\n3. Placing Orders...")
    
    engine = MatchingEngine()

    # ALICE SELLS 10 @ $200
    print("-> Alice places SELL 10 @ $200.00")
    sell_order = Order.objects.create(
        user=alice, stock=tsla, side=Order.Side.SELL, 
        quantity=10, price=Decimal("200.00"), status=Order.Status.OPEN
    )
    # Trigger Engine Manually
    engine.process_order(sell_order.id)

    # BOB BUYS 10 @ $200
    print("-> Bob places BUY 10 @ $200.00")
    buy_order = Order.objects.create(
        user=bob, stock=tsla, side=Order.Side.BUY, 
        quantity=10, price=Decimal("200.00"), status=Order.Status.OPEN
    )
    # Trigger Engine Manually
    engine.process_order(buy_order.id)

    print("-> Engine processing complete.")

    # --- VERIFICATION ---
    print("\n4. Verifying Results...")
    
    alice.refresh_from_db()
    bob.refresh_from_db()
    p_alice.refresh_from_db()
    
    # Check Bob's Portfolio safely
    p_bob = Portfolio.objects.filter(user=bob, stock=tsla).first()
    bob_shares = p_bob.quantity if p_bob else 0

    sell_order.refresh_from_db()
    buy_order.refresh_from_db()

    # ASSERTIONS
    print(f"Alice Balance: ${alice.balance} (Expected: $3000.00)")
    print(f"Bob Balance:   ${bob.balance} (Expected: $8000.00)")
    print(f"Alice Shares:  {p_alice.quantity} (Expected: 40)")
    print(f"Bob Shares:    {bob_shares} (Expected: 10)")
    
    print(f"Sell Order:    {sell_order.status} (Expected: FILLED)")
    print(f"Buy Order:     {buy_order.status} (Expected: FILLED)")

    tx_count = Transaction.objects.count()
    print(f"Transactions:  {tx_count} (Expected: 1)")

if __name__ == '__main__':
    run_simulation()