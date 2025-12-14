from rest_framework import generics, filters
from .models import Stock
from .serializers import StockSerializer

class StockListView(generics.ListAPIView):
    """
    GET: List all tradeable assets.
    Supports filtering: /api/stocks/?search=Tech
    """
    queryset = Stock.objects.all().order_by('ticker')
    serializer_class = StockSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ticker', 'name', 'industry']
    ordering_fields = ['spot_price', 'volume']

class StockDetailView(generics.RetrieveAPIView):
    """
    GET: Details for a single stock (e.g., TSLA).
    Lookup field is 'ticker' (not ID) for better URLs: /api/stocks/TSLA/
    """
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    lookup_field = 'ticker'