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

    def get_depth(self, limit=10):
        """
        Returns a dictionary representation of the book for the frontend/API.
        Example: {'bids': [{'price': 100, 'qty': 50}], 'asks': [...]}
        """
        # Helper to format list
        def format_orders(orders):
            return [
                {'price': o.price, 'quantity': o.quantity, 'id': o.id} 
                for o in orders[:limit]
            ]

        return {
            'stock': self.stock.ticker,
            'bids': format_orders(self.get_bids()),
            'asks': format_orders(self.get_asks())
        }