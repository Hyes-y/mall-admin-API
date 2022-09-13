from django.db import models


class Coupon(models.Model):
    """
    쿠폰 모델
    """
    DC_TYPE = (
        (0, '배송비 할인'),
        (1, '퍼센트(%) 할인'),
        (2, '정액 할인'),
    )

    ISS_TYPE = (
        (0, '지정 발급'),
        (1, '사용자 발급'),
    )

    is_used = models.BooleanField(verbose_name='사용 여부', default=False)
    start_date = models.DateTimeField(verbose_name='유효기간(시작)', null=True)
    end_date = models.DateTimeField(verbose_name='유효기간(종료)', null=True)
    min_price = models.PositiveIntegerField(verbose_name='조건(최소금액)', null=True)
    max_price = models.PositiveIntegerField(verbose_name='조건(최대금액)', null=True)
    dc_type = models.PositiveIntegerField(verbose_name='타입(할인종류)', choices=DC_TYPE)
    iss_type = models.PositiveIntegerField(verbose_name='타입(발급종류)', choices=ISS_TYPE)
    value = models.PositiveIntegerField(verbose_name='값', null=True)
    date = models.DateTimeField(verbose_name='사용 날짜', null=True)
    description = models.CharField(verbose_name='설명', max_length=30)
    sale_amount = models.PositiveIntegerField(verbose_name='할인금액', null=True)
    owner = models.PositiveIntegerField(verbose_name='주문 고객', null=True)  # 주어진 데이터 사용을 위해 외래키 연결 x
    amount = models.PositiveIntegerField(verbose_name='수량', null=True)  # 사용자 발급(다운로드) 쿠폰의 경우 쿠폰 수량 필드

    def __str__(self):
        return f'{self.description}  유효기간: {self.start_date} - {self.end_date}'


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
