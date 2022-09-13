# django rest api
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAdminUser
# local modules
from .models import Coupon, CouponType
from .serializers import CouponSerializer, CouponTypeSerializer


class CouponTypeViewSet(viewsets.ModelViewSet):
    queryset = CouponType.objects.all()
    serializer_class = CouponTypeSerializer
    # permission_classes = [IsAdminUser]


class CouponViewSet(viewsets.ModelViewSet):
    pass
