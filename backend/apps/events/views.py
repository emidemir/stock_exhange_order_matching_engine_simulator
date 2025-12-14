from rest_framework import generics
from .models import MarketEvent
from .serializers import MarketEventSerializer

class MarketEventListCreateView(generics.ListCreateAPIView):
    """
    GET: See active news.
    POST: Create a new news event (and watch the bots react!).
    """
    queryset = MarketEvent.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = MarketEventSerializer