from django.contrib import admin
from .models import CryptoPair, PriceUpdate

class PriceUpdateInline(admin.TabularInline):
    model = PriceUpdate
    extra = 1  # Количество пустых форм для добавления новых записей

class CryptoPairAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'description')  # Что показывать в списке
    search_fields = ('symbol', 'description')  # По каким полям будет осуществляться поиск
    ordering = ('symbol',)  # Сортировка по умолчанию
    inlines = [PriceUpdateInline]  # Встраивание PriceUpdate в CryptoPair

class PriceUpdateAdmin(admin.ModelAdmin):
    list_display = ('pair', 'price', 'timestamp')  # Показать данные по обновлению цен
    search_fields = ('pair__symbol',)  # Поиск по символу криптовалютной пары
    list_filter = ('timestamp',)  # Фильтрация по времени

# Регистрация моделей в админке
admin.site.register(CryptoPair, CryptoPairAdmin)
admin.site.register(PriceUpdate, PriceUpdateAdmin)





