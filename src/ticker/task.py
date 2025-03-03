from celery import shared_task
from django.core.cache import cache
from decimal import Decimal
from .models import CryptoPair, PriceUpdate

@shared_task
def save_prices_from_cache():
    """Сохраняет накопленные цены в БД"""
    keys = cache.keys('crypto_price_*')  # Получаем все ключи с ценами

    if not keys:
        return "No data in cache"

    bulk_data = []
    
    for key in keys:
        cached_data = cache.get(key, [])
        if not cached_data:
            continue

        symbol = cached_data[0]['symbol']
        pair = CryptoPair.objects.get(symbol=symbol)  # Получаем объект пары

        for entry in cached_data:
            bulk_data.append(PriceUpdate(pair=pair, price=Decimal(entry['price'])))

        cache.delete(key)  # Удаляем записанные данные из кеша

    if bulk_data:
        PriceUpdate.objects.bulk_create(bulk_data)  # Сохраняем одним запросом

    return f"Saved {len(bulk_data)} price updates"

        