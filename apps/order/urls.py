from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderTestViewSet

router = DefaultRouter()
router.register(r'test', OrderTestViewSet, basename='order-test')
router.register(r'', OrderViewSet, basename='orders')


urlpatterns = [
    path('', include(router.urls)),
]