from django.db import transaction
from decimal import Decimal
from apps.transactions.models import Transaction 
from apps.portfolios.models import Portfolio
from apps.orders.models import Order
from .order_book import OrderBook

class MatchingEngine:
    def process_order(self, order_id):
        """
        Retrieves the order by ID and attempts to match it.
        Accepts ID (not object) to ensure we get fresh DB data.
        """
        try:
            # Lock the incoming order to prevent race conditions immediately
            with transaction.atomic():
                incoming_order = Order.objects.select_for_update().get(id=order_id)
            
            if incoming_order.status in [Order.Status.FILLED, Order.Status.CANCELLED]:
                return

            print(f"Processing {incoming_order.side} order #{incoming_order.id} for {incoming_order.stock.ticker}...")
            
            # Instantiate book
            order_book = OrderBook(incoming_order.stock)

            # LOOP: Keep matching while the order is still open/partial
            while incoming_order.remaining_quantity > 0:
                
                # 1. Atomic Match Finding
                with transaction.atomic():
                    # Re-fetch incoming to ensure we have latest state inside loop
                    incoming_order.refresh_from_db()
                    if incoming_order.remaining_quantity <= 0:
                        break

                    match = order_book.get_best_match(incoming_order)
                    
                    if not match:
                        print("-> No matching orders found. Order rests in book.")
                        break 

                    # 2. Lock the match row 
                    match = Order.objects.select_for_update().get(id=match.id)

                    # 3. Calculate Trade Details
                    # Price is determined by the MAKER (the order already in the book)
                    trade_price = match.price 
                    trade_quantity = min(incoming_order.remaining_quantity, match.remaining_quantity)

                    # Identify Buyer and Seller
                    if incoming_order.side == Order.Side.BUY:
                        buy_order, sell_order = incoming_order, match
                    else:
                        buy_order, sell_order = match, incoming_order

                    # 4. Execute Trade
                    self._execute_trade(buy_order, sell_order, trade_price, trade_quantity)

        except Order.DoesNotExist:
            print(f"Order {order_id} not found.")

    def _execute_trade(self, buy_order, sell_order, price, quantity):
        print(f"   -> MATCH! {quantity} shares @ ${price}")

        # 1. Update Balances
        buyer = buy_order.user
        seller = sell_order.user
        cost = price * Decimal(quantity)

        buyer.balance -= cost
        seller.balance += cost
        buyer.save()
        seller.save()

        # 2. Update Portfolios
        # Buyer Gets Stock
        p_buyer, _ = Portfolio.objects.get_or_create(user=buyer, stock=buy_order.stock)
        p_buyer.quantity += quantity
        # Optional: Calculate new average buy price here if you want advanced logic
        p_buyer.save()

        # Seller Loses Stock
        # Use filter().first() to avoid crash if portfolio is missing (safety check)
        p_seller = Portfolio.objects.filter(user=seller, stock=sell_order.stock).first()
        if p_seller:
            p_seller.quantity -= quantity
            if p_seller.quantity <= 0:
                p_seller.delete() 
            else:
                p_seller.save()

        # 3. Create Transaction Record
        Transaction.objects.create(
            stock=buy_order.stock,
            buyer=buyer,
            seller=seller,
            buy_order=buy_order,
            sell_order=sell_order,
            price=price,
            quantity=quantity
        )

        # --- 4. NEW FIX: UPDATE THE STOCK PRICE ---
        stock = buy_order.stock
        stock.spot_price = price      # Set current price to this trade's price
        stock.volume += quantity      # Add to total volume
        stock.save()                  # <--- CRITICAL: Save to DB
        # ------------------------------------------

        # 5. Update Orders
        for order in [buy_order, sell_order]:
            order.filled_quantity += quantity
            if order.filled_quantity >= order.quantity:
                order.status = Order.Status.FILLED
            else:
                order.status = Order.Status.PARTIAL
            order.save()