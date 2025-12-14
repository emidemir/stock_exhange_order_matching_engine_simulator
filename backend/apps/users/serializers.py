from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 
            'last_name', 'phone_number', 'balance', 'date_joined'
        ]
        # Security: These fields can be SEEN but not TOUCHED by the user
        read_only_fields = ['id', 'username', 'balance', 'date_joined']