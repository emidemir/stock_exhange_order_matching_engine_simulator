from rest_framework import serializers
from .models import MarketEvent

class MarketEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketEvent
        fields = ['id', 'title', 'target_industry', 'sentiment_score', 'is_active', 'created_at']