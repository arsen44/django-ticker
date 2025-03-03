from django.urls import re_path
from ..core import consumers

websocket_urlpatterns = [
    re_path(r'ws/ticker/(?P<pair_symbol>\w+)/$', consumers.TickerConsumer.as_asgi()),
]