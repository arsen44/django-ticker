import json
import asyncio
import logging
import websockets
from decimal import Decimal
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from .models import CryptoPair
from django.core.cache import cache

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


class BinanceClient:
    def __init__(self):
        self.ws_url = settings.BINANCE_WS_URL
        self.pairs = ['btcusdt', 'ethusdt', 'bnbusdt']
        self.connection = None

    async def get_or_create_pairs(self):
        """Проверяем и создаем пары в БД, если они не существуют"""
        for pair in self.pairs:
            await sync_to_async(CryptoPair.objects.get_or_create)(
                symbol=pair,
                defaults={'description': f'{pair.upper()} price from Binance'}
            )
        logger.info(f"Initialized {len(self.pairs)} cryptocurrency pairs")

    async def save_price_to_cache(self, symbol, price):
        """Сохраняем цену во временный кеш (Redis)"""
        cache_key = f'crypto_price_{symbol}'
        cached_data = cache.get(cache_key, [])
        # Сохраняем в виде списка
        cached_data.append({'symbol': symbol, 'price': str(price)})
        cache.set(cache_key, cached_data, timeout=60)  # Храним данные 1 минуту

    async def connect(self):
        """Подключение к WebSocket Binance"""
        streams = "/".join([f"{pair}@trade" for pair in self.pairs])
        socket_url = f"{self.ws_url}/stream?streams={streams}&timeUnit=MICROSECOND"

        print(socket_url)
        try:
            self.connection = await websockets.connect(socket_url)
            logger.info(f"Connected to Binance WebSocket: {socket_url}")
            return True
        except Exception as e:
            logger.error(f"Connection to Binance WebSocket failed: {e}")
            return False

    async def listen(self):
        """Прослушивание и обработка сообщений"""
        if not self.connection:
            logger.error("No connection established. Call connect() first.")
            return

        try:
            while True:
                try:
                    message = await self.connection.recv()
                    data = json.loads(message)

                    if 'data' in data:
                        ticker_data = data['data']
                        symbol = ticker_data['s'].lower()
                        price = ticker_data['p']  # Текущая цена (close price)

                        # Сохраняем обновление цены в БД
                        await self.save_price_to_cache(symbol, price)
                except (websockets.exceptions.ConnectionClosed,
                        websockets.exceptions.ConnectionClosedError) as e:
                    logger.warning(f"Connection closed: {e}. Reconnecting...")
                    await asyncio.sleep(5)
                    await self.connect()

        except Exception as e:
            logger.error(f"Error in listener: {e}")
            if self.connection:
                await self.connection.close()

    async def start(self):
        """Запускает клиент"""
        await self.get_or_create_pairs()
        connected = await self.connect()

        if connected:
            await self.listen()

# Функция для запуска клиента Binance в фоновом режиме


async def start_binance_client():
    client = BinanceClient()
    await client.start()

# Эту функцию нужно вызвать при запуске Django


def run_binance_client():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_binance_client())
    loop.run_forever()
