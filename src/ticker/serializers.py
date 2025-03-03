from rest_framework import serializers
from .models import CryptoPair, PriceUpdate

class CryptoPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoPair
        fields = ['id', 'symbol', 'description']

class PriceUpdateSerializer(serializers.ModelSerializer):
    pair_symbol = serializers.CharField(source='pair.symbol', read_only=True)
    
    class Meta:
        model = PriceUpdate
        fields = ['id', 'pair_symbol', 'price', 'timestamp']