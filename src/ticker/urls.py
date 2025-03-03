from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'pairs', views.CryptoPairViewSet)
router.register(r'prices', views.PriceUpdateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]