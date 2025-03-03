from django.apps import AppConfig
import threading

class TickerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticker'
    
    def ready(self):
        # Запускаем Binance клиент в отдельном потоке
        # Только если не запускаемся через командную строку или тесты
        import sys
        if not any(['manage.py', 'pytest', 'test']) in sys.argv:
            from .binance_client import run_binance_client
            binance_thread = threading.Thread(target=run_binance_client)
            binance_thread.daemon = True
            binance_thread.start()