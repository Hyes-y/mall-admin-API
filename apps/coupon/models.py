from django.db import models


class CouponType(models.Model):
    """
    쿠폰 타입 모델
    """
    DC_TYPE = (
        (0, '배송비 할인'),
        (1, '퍼센트(%) 할인'),
        (2, '정액 할인(KRW)'),
        # (3, '정액 할인(USD)'),
    )

    ISS_TYPE = (
        (0, '지정 발급'),
        (1, '사용자 발급'),
        (2, '자동 발급'),
    )

    start_date = models.DateTimeField(verbose_name='유효기간(시작)', null=True)
    end_date = models.DateTimeField(verbose_name='유효기간(종료)', null=True)
    period = models.PositiveIntegerField(verbose_name='유효기간(기한)', null=True)
    min_price = models.DecimalField(verbose_name='조건(최소금액)', null=True, max_digits=20, decimal_places=2)
    max_dc_price = models.DecimalField(verbose_name='조건(최대할인금액)', null=True, max_digits=20, decimal_places=2)
    dc_type = models.PositiveIntegerField(verbose_name='타입(할인종류)', choices=DC_TYPE)
    iss_type = models.PositiveIntegerField(verbose_name='타입(발급종류)', choices=ISS_TYPE)
    value = models.DecimalField(verbose_name='값', null=True, max_digits=20, decimal_places=2)
    description = models.CharField(verbose_name='설명', max_length=30)
    amount = models.PositiveIntegerField(verbose_name='수량', null=True)  # 사용자 발급(다운로드) 쿠폰의 경우 쿠폰 수량 필드
    code = models.CharField(verbose_name='쿠폰 코드', max_length=20, null=True)
    is_active = models.BooleanField(verbose_name='활성화', default=True)


class Coupon(models.Model):
    """
    쿠폰 모델
    """
    type = models.ForeignKey(CouponType, on_delete=models.DO_NOTHING, db_column='type', related_name='coupons')
    issue_date = models.DateTimeField(verbose_name='발급 날짜', auto_now_add=True)
    expired_date = models.DateTimeField(verbose_name='만료 날짜')
    is_used = models.BooleanField(verbose_name='사용 여부', default=False)
    date = models.DateTimeField(verbose_name='사용 날짜', null=True)
    sale_amount = models.DecimalField(verbose_name='할인 금액', max_digits=20, decimal_places=2, null=True)
    owner = models.PositiveIntegerField(verbose_name='소유자', blank=True, null=True)  # 주어진 데이터 사용을 위해 외래키 연결 x
    code = models.CharField(verbose_name='발급 코드', max_length=20)
    is_expired = models.BooleanField(verbose_name='만료 여부', default=False)
