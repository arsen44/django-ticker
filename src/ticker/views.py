from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from .models import CryptoPair, PriceUpdate
from .serializers import CryptoPairSerializer, PriceUpdateSerializer


class CryptoPairViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CryptoPair.objects.all()
    serializer_class = CryptoPairSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['symbol']


class PriceUpdateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PriceUpdate.objects.all().select_related('pair')
    serializer_class = PriceUpdateSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['pair__symbol']
    ordering_fields = ['timestamp', 'price']
    ordering = ['-timestamp']

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest prices for all pairs"""
        pairs = CryptoPair.objects.all()
        latest_prices = []

        for pair in pairs:
            latest_price = PriceUpdate.objects.filter(
                pair=pair
            ).order_by('-timestamp').first()

            if latest_price:
                latest_prices.append(latest_price)

        serializer = self.get_serializer(latest_prices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get price history for a specific pair and time range"""
        symbol = request.query_params.get('symbol')
        days = request.query_params.get('days', 1)

        try:
            days = int(days)
        except ValueError:
            days = 1

        if not symbol:
            return Response({"error": "Symbol parameter is required"}, status=400)

        time_threshold = timezone.now() - timedelta(days=days)

        queryset = PriceUpdate.objects.filter(
            pair__symbol__iexact=symbol,
            timestamp__gte=time_threshold
        ).order_by('timestamp')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
