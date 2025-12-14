from rest_framework import serializers
from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = [
            'id', 'ticker', 'name', 'industry', 
            'spot_price', 'open_price', 'previous_close_price', 
            'high_price', 'low_price', 'volume', 
            'created_at', 'updated_at'
        ]