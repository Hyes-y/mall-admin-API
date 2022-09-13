# django rest api
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.filters import SearchFilter

# local modules
from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    """
    주문 내역 조회, 수정 API
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # 검색 기능
    filter_backends = [SearchFilter]
    search_fields = ['user']

    def get_queryset(self):
        """
        주어진 날짜 범위에 속하거나 결제, 배송 상태에 따른 필터링
        query_params : start, end, pay_state, delivery_state
        """
        queryset = self.queryset
        params = self.request.query_params
        if params.get('start'):
            queryset = queryset.filter(date__gte=params.get('start'))

        if params.get('end'):
            queryset = queryset.filter(date__lte=params.get('end'))

        if params.get('pay_state'):
            queryset = queryset.filter(pay_state=params.get('pay_state'))

        if params.get('delivery_state'):
            queryset = queryset.filter(delivery_state=params.get('delivery_state'))

        return queryset

