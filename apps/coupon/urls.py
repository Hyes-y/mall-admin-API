from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, CouponTypeViewSet, CouponStatisticsViewSet

router = DefaultRouter()
router.register(r'types', CouponTypeViewSet, basename='coupon-type')
router.register(r'statistics', CouponStatisticsViewSet, basename='coupon-statistics')
router.register(r'', CouponViewSet, basename='coupons')

urlpatterns = [
    path('', include(router.urls)),
]