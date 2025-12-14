from rest_framework import serializers
from apps.users.models import User
from apps.stocks.models import Stock
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    # Use 'TSLA' instead of ID 1
    stock = serializers.SlugRelatedField(
        slug_field='ticker', 
        queryset=Stock.objects.all()
    )
    # Use 'Alice' instead of ID 5
    user = serializers.SlugRelatedField(
        slug_field='username', 
        queryset=User.objects.all()
    )

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'stock', 'side', 
            'price', 'quantity', 'filled_quantity', 
            'status', 'created_at'
        ]
        # Engine controls these, not the user
        read_only_fields = ['id', 'filled_quantity', 'status', 'created_at']