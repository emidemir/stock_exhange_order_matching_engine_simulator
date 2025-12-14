from rest_framework import generics, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.stocks.models import Stock
from .models import Order
from .serializers import OrderSerializer
from services.order_book import OrderBook  # Import our Engine Service

# 1. Standard Management: List all Orders or Place a new one
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # Filter by Ticker or Username
    search_fields = ['stock__ticker', 'user__username', 'status']

# 2. Visualization: The "Level 2" Market Data
class OrderBookView(APIView):
    """
    GET /api/orders/book/TSLA/
    Returns the aggregated Bids and Asks for a specific stock.
    Directly uses the Service Layer, bypassing the DB query overhead in Serializers.
    """
    def get(self, request, ticker):
        stock = get_object_or_404(Stock, ticker=ticker)
        
        # Initialize our Service
        book = OrderBook(stock)
        
        # Get the structured data (dict with 'bids' and 'asks')
        depth_data = book.get_depth(limit=20) 
        
        return Response(depth_data, status=status.HTTP_200_OK)