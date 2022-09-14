from django.db import models
from apps.coupon.models import Coupon


class Order(models.Model):
    """
    주문 내역 모델 (Order)
    """
    PAY_STATE = (
        (0, '결제취소'),
        (1, '결제대기'),
        (2, '결제완료'),
    )

    DELIVERY_STATE = (
        (0, '배송취소'),
        (1, '배송준비중'),
        (2, '배송중'),
        (3, '배송완료'),
    )

    date = models.DateTimeField(verbose_name='날짜', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정 날짜', auto_now=True)
    user = models.PositiveIntegerField(verbose_name='주문 고객', null=True)  # 주어진 데이터 사용을 위해 외래키 연결 x
    quantity = models.PositiveIntegerField(verbose_name='수량')
    price = models.DecimalField(verbose_name='정가', max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(verbose_name='할인가', max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(verbose_name='배송비', max_digits=10, decimal_places=2, default=1200)
    payment_amount = models.DecimalField(verbose_name='최종결제액', default=0, max_digits=10, decimal_places=2)
    coupon = models.CharField(null=True, verbose_name='사용 쿠폰', max_length=20)  # foreign key
    pay_state = models.PositiveIntegerField(verbose_name='결제 상태', default=1, choices=PAY_STATE)
    delivery_state = models.PositiveIntegerField(verbose_name='배송 상태', default=1, choices=DELIVERY_STATE)
    buyr_city = models.CharField(verbose_name='배송지(도시)', max_length=30)
    buyr_country = models.CharField(verbose_name='배송지(국가)', max_length=30)
    buyr_zipx = models.CharField(verbose_name='우편번호', max_length=20)
    vccode = models.CharField(verbose_name="국가코드", max_length=10)
    delivery_num = models.CharField(verbose_name="delivery_num", max_length=20, null=True)

    # def __str__(self):
    #     return f'주문 날짜: {self.date} \n 주문 id: {self.id}'

    class Meta:
        ordering = ["-date"]
