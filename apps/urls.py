from django.urls import path, include

urlpatterns = [
    path('admin/', include('apps.order.urls')),
]