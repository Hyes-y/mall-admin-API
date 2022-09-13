# django rest api
from rest_framework import viewsets, mixins
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
        start_date = self.kwargs.get('start', None)
        end_date = self.kwargs.get('end', None)
        queryset = Order.objects.all()
        if start_date or end_date:
            queryset = Order.objects.filter(date__range=[start_date, end_date])

        return queryset
