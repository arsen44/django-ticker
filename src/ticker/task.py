from celery import shared_task
from django.core.cache import cache
from decimal import Decimal
from .models import CryptoPair, PriceUpdate


@shared_task
def save_prices_from_cache():
    """Сохраняет накопленные цены в БД"""
    prefix = cache.make_key("crypto_price_")
    keys = list(cache.iter_keys(f"{prefix}*"))

    if not keys:
        return "No data in cache"

    bulk_data = []

    for key in keys:
        cached_data = cache.get(key, [])
        if not cached_data:
            continue

        symbol = cached_data[0]['symbol']
        pair = CryptoPair.objects.filter(symbol=symbol).first()

        if not pair:
            continue  # Пропускаем, если пары нет в БД

        for entry in cached_data:
            bulk_data.append(PriceUpdate(
                pair=pair, price=Decimal(entry['price'])))

        cache.delete(key)  # Очищаем Redis

    if bulk_data:
        # Записываем в БД одним запросом
        PriceUpdate.objects.bulk_create(bulk_data)

    return f"Saved {len(bulk_data)} price updates"
