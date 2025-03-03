from django.db import models

class CryptoPair(models.Model):
    symbol = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.symbol

class PriceUpdate(models.Model):
    pair = models.ForeignKey(CryptoPair, on_delete=models.CASCADE, related_name='price_updates')
    price = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['pair', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.pair} - {self.price} at {self.timestamp}"