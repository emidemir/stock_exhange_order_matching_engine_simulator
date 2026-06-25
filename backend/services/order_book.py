from apps.orders.models import Order
from django.db.models import Q

class OrderBook:
    """
    The OrderBook manages the state of orders for a specific stock.
    It serves as the interface between the Database and the Matching Engine.
    """
    def __init__(self, stock):
        self.stock = stock

    def get_bids(self):
        """
        Returns active BUY orders (Bids), best price first.
        Sorting: High Price -> Early Timestamp
        """
        return Order.objects.filter(
            stock=self.stock,
            side='BUY',
            status__in=['OPEN', 'PARTIAL']
        ).order_by('-price', 'created_at')

    def get_asks(self):
        """
        Returns active SELL orders (Asks), best price first.
        Sorting: Low Price -> Early Timestamp
        """
        return Order.objects.filter(
            stock=self.stock,
            side='SELL',
            status__in=['OPEN', 'PARTIAL']
        ).order_by('price', 'created_at')

    def get_best_match(self, incoming_order):
        """
        Finds the single best counter-order for an incoming order.
        Returns None if no match is found.
        """
        # If I am Buying, I need the cheapest Seller (Ask)
        if incoming_order.side == 'BUY':
            best_ask = self.get_asks().first()
            
            # Match condition: My Buy Price >= Their Sell Price
            if best_ask and incoming_order.price >= best_ask.price:
                return best_ask
                
        # If I am Selling, I need the highest Bidder (Bid)
        elif incoming_order.side == 'SELL':
            best_bid = self.get_bids().first()
            
            # Match condition: My Sell Price <= Their Buy Price
            if best_bid and incoming_order.price <= best_bid.price:
                return best_bid
                
        return None

    def _aggregate_by_price(self, orders, limit):
        """
        Collapses individual resting orders into Level 2-style price levels:
        one row per price, with the remaining (unfilled) quantity summed
        across every order sitting at that price.

        Relies on `orders` already being sorted best-price-first, so the
        first time a price is seen is also its correct rank in the book.
        """
        levels = {}
        for o in orders:
            level = levels.setdefault(o.price, {
                'price': o.price,
                'quantity': 0,
                'order_count': 0,
            })
            # Use remaining_quantity, not the original quantity — a
            # PARTIAL order should only show what's actually still resting.
            level['quantity'] += o.remaining_quantity
            level['order_count'] += 1

        return list(levels.values())[:limit]

    def _calc_spread(self, bids, asks):
        if not bids or not asks:
            return None

        best_bid = bids[0]['price']
        best_ask = asks[0]['price']
        spread = best_ask - best_bid
        mid = (best_ask + best_bid) / 2

        return {
            'amount': spread,
            'percent': (spread / mid * 100) if mid else 0,
            'best_bid': best_bid,
            'best_ask': best_ask,
        }

    def get_depth(self, limit=10):
        """
        Returns a dictionary representation of the book for the frontend/API,
        aggregated into price levels the way a real Level 2 book is shown —
        not as one row per individual resting order.
        Example: {'bids': [{'price': 100, 'quantity': 50, 'order_count': 2}], 'asks': [...]}
        """
        bids = self._aggregate_by_price(self.get_bids(), limit)
        asks = self._aggregate_by_price(self.get_asks(), limit)

        return {
            'stock': self.stock.ticker,
            'bids': bids,
            'asks': asks,
            'spread': self._calc_spread(bids, asks),
        }