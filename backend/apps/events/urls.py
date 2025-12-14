from django.urls import path
from .views import MarketEventListCreateView

urlpatterns = [
    path('', MarketEventListCreateView.as_view(), name='event-list-create'),
]