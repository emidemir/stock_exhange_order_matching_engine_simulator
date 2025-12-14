from rest_framework import generics, filters
from .models import Portfolio
from .serializers import PortfolioSerializer

class PortfolioListView(generics.ListAPIView):
    """
    GET: List all asset holdings.
    Filtering:
      - /api/portfolios/?search=Alice  (See everything Alice owns)
      - /api/portfolios/?search=TSLA   (See everyone who owns TSLA)
    """
    queryset = Portfolio.objects.all().order_by('user__username')
    serializer_class = PortfolioSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'stock__ticker']
    ordering_fields = ['quantity', 'average_buy_price']