# django rest api
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
# local modules
from .models import Coupon, CouponType
from .serializers import CouponSerializer, CouponTypeSerializer
from .permissions import IsAdminOrCreateOnly


class CouponTypeViewSet(viewsets.ModelViewSet):
    queryset = CouponType.objects.all()
    serializer_class = CouponTypeSerializer
    # permission_classes = [IsAdminUser]


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    # permission_classes = [IsAdminOrCreateOnly]
