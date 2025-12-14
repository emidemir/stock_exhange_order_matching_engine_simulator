from rest_framework import generics, filters
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionListView(generics.ListAPIView):
    """
    GET: Global trade history.
    Filtering:
      - /api/transactions/?search=TSLA (All trades for Tesla)
      - /api/transactions/?ordering=-timestamp (Latest trades first)
    """
    queryset = Transaction.objects.all().order_by('-timestamp')
    serializer_class = TransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['stock__ticker', 'buyer__username', 'seller__username']
    ordering_fields = ['price', 'timestamp']