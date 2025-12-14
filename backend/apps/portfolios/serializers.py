from rest_framework import serializers
from apps.users.models import User
from apps.stocks.models import Stock
from .models import Portfolio

class PortfolioSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', 
        queryset=User.objects.all()
    )
    stock = serializers.SlugRelatedField(
        slug_field='ticker', 
        queryset=Stock.objects.all()
    )

    class Meta:
        model = Portfolio
        fields = ['id', 'user', 'stock', 'quantity', 'average_buy_price']
        # Portfolios are managed exclusively by the Matching Engine.
        # No one should be editing these manually via API.
        read_only_fields = ['id', 'user', 'stock', 'quantity', 'average_buy_price']