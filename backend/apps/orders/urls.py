from django.urls import path
from .views import OrderListCreateView, OrderBookView

urlpatterns = [
    # General Management
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    
    # The Visualizer (e.g., /api/orders/book/TSLA/)
    path('book/<str:ticker>/', OrderBookView.as_view(), name='order-book'),
]