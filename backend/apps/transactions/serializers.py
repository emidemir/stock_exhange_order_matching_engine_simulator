from rest_framework import serializers
from apps.users.models import User
from apps.stocks.models import Stock
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    # Readable names instead of IDs
    stock = serializers.SlugRelatedField(slug_field='ticker', read_only=True)
    buyer = serializers.SlugRelatedField(slug_field='username', read_only=True)
    seller = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'stock', 'buyer', 'seller', 
            'price', 'quantity', 'timestamp', 
            'buy_order', 'sell_order' # Linking back to original orders
        ]
        read_only_fields = fields # Transactions are immutable history