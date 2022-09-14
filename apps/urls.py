from django.urls import path, include

urlpatterns = [
    path('admin/orders/', include('apps.order.urls')),
    path('admin/coupons/', include('apps.coupon.urls')),
]