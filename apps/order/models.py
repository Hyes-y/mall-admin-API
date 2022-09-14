from django.db import models
from apps.coupon.models import Coupon


class Order(models.Model):
    """
    주문 내역 모델 (Order)
    """
    PAY_STATE = (
        (0, '결제취소'),
        (1, '결제완료'),
    )

    DELIVERY_STATE = (
        (0, '배송준비중'),
        (1, '배송중'),
        (2, '배송완료'),
    )

    date = models.DateTimeField(verbose_name='날짜', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정 날짜', auto_now=True)
    user = models.PositiveIntegerField(verbose_name='주문 고객', null=True)  # 주어진 데이터 사용을 위해 외래키 연결 x
    quantity = models.PositiveIntegerField(verbose_name='수량')
    price = models.FloatField(verbose_name='정가')
    sale_price = models.FloatField(verbose_name='할인가')
    delivery_cost = models.PositiveIntegerField(verbose_name='배송비', default=1200)
    payment_amount = models.FloatField(verbose_name='최종결제액')
    coupon = models.PositiveIntegerField(null=True, verbose_name='사용 쿠폰')  # foreign key
    pay_state = models.PositiveIntegerField(verbose_name='결제 상태', choices=PAY_STATE)
    delivery_state = models.PositiveIntegerField(verbose_name='배송 상태', choices=DELIVERY_STATE)
    buyr_city = models.CharField(verbose_name='배송지(도시)', max_length=30)
    buyr_country = models.CharField(verbose_name='배송지(국가)', max_length=30)
    buyr_zipx = models.CharField(verbose_name='우편번호', max_length=20)
    vccode = models.CharField(verbose_name="국가코드", max_length=10)
    delivery_num = models.CharField(verbose_name="delivery_num", max_length=20)

    def __str__(self):
        return f'주문 날짜: {self.date} \n 주문 id: {self.id}'

    class Meta:
        ordering = ["-date"]
