import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CryptoPair, PriceUpdate

class TickerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.pair_symbol = self.scope['url_route']['kwargs']['pair_symbol'].lower()
        self.room_group_name = f'ticker_{self.pair_symbol}'
        
        # Проверяем, существует ли пара
        pair_exists = await self.pair_exists(self.pair_symbol)
        if not pair_exists:
            await self.close()
            return
        
        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Отправляем последнее значение цены
        latest_price = await self.get_latest_price(self.pair_symbol)
        if latest_price:
            await self.send(text_data=json.dumps({
                'pair': self.pair_symbol,
                'price': str(latest_price['price']),
                'timestamp': latest_price['timestamp'].isoformat()
            }))

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Обработка сообщения от WebSocket
    async def receive(self, text_data):
        # Клиенты только получают данные, этот метод не используется
        pass

    # Обработка сообщения от group
    async def ticker_update(self, event):
        # Отправить сообщение клиенту
        await self.send(text_data=json.dumps({
            'pair': event['pair'],
            'price': event['price'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def pair_exists(self, symbol):
        return CryptoPair.objects.filter(symbol__iexact=symbol).exists()
    
    @database_sync_to_async
    def get_latest_price(self, symbol):
        try:
            pair = CryptoPair.objects.get(symbol__iexact=symbol)
            price = PriceUpdate.objects.filter(pair=pair).order_by('-timestamp').first()
            if price:
                return {
                    'price': price.price,
                    'timestamp': price.timestamp
                }
            return None
        except CryptoPair.DoesNotExist:
            return None