from django.db.models import Sum
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.serializers import ValidationError
from .models import Coupon, CouponType
from apps.utils import code_generator, get_current_date, add_period


class CouponTypeSerializer(ModelSerializer):
    """ 쿠폰 타입 관련 시리얼라이저 """
    class Meta:
        model = CouponType
        fields = '__all__'
        read_only_fields = ['id']

    def validate(self, data):
        """
        쿠폰 타입 생성 및 수정 시 데이터 검증
        1) start_date <= end_date
        2) period < 0
        3) types in valid range
        4) 사용자 발급의 경우 수량, 쿠폰 코드 반드시 지정
        5) 퍼센트 할인의 경우 100 초과 값은 불가능
        """
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        period = data.get('period', None)
        dc_type = data.get('dc_type', None)
        iss_type = data.get('iss_type', None)
        amount = data.get('amount', None)
        code = data.get('code', None)
        value = data.get('value', None)

        if start_date > end_date:
            raise ValidationError("ERROR: 유효 기간이 올바르지 않습니다.")

        if get_current_date() > end_date.strftime('%Y-%m-%d %H:%M:%S'):
            raise ValidationError("ERROR: 유효 기간이 올바르지 않습니다.")

        if period < 0:
            raise ValidationError("ERROR: 유효 기한이 올바르지 않습니다.")

        if dc_type not in (0, 1, 2, 3) or iss_type not in (0, 1, 2):
            raise ValidationError("ERROR: 올바르지 않은 쿠폰 종류입니다.")

        if iss_type == 1:
            if not (amount and code):
                raise ValidationError("ERROR: 사용자 발급의 경우 수량과 쿠폰 코드를 지정해주세요.")
            if len(CouponType.objects.filter(is_active=True, code=code)) > 0:
                raise ValidationError("ERROR: 동일한 쿠폰 코드가 존재합니다. 다시 지정해주세요.")

        if dc_type == 1 and value > 100:
            raise ValidationError("ERROR: 퍼센트 할인은 100 초과 값을 입력할 수 없습니다.")

        return data


class CouponSerializer(ModelSerializer):
    """ 쿠폰 발급 시리얼라이저 """
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['expired_date', 'code']

    def create(self, validated_data):
        coupon_type = validated_data.get('type', None)
        owner = validated_data.get('owner', None)

        if not coupon_type:
            raise ValidationError("ERROR: 올바르지 않은 입력값입니다.")

        coupon_type_obj = CouponType.objects.get(id=coupon_type.id)

        # 쿠폰 타입이 유효하지 않음 (비활성화 되어있거나 유효 기간이 지난 경우)
        if not (coupon_type_obj.is_active and
                coupon_type_obj.end_date.strftime('%Y-%m-%d %H:%M:%S') >= get_current_date()):
            raise ValidationError("ERROR: 유효하지 않은 쿠폰 타입입니다.")

        # 이미 발급 받은 경우
        if len(Coupon.objects.filter(owner=owner, type=coupon_type_obj)) != 0:
            raise ValidationError("ERROR: 이미 발급받은 쿠폰입니다.")

        # iss_type 1인 경우 사용자 발급
        if coupon_type_obj.iss_type == 1:
            code = coupon_type_obj.code

            # 해당 타입 쿠폰의 수량이 0인 경우(소진)
            if coupon_type_obj.amount <= 0:
                raise ValidationError("ERROR: 해당 쿠폰이 소진되었습니다.")

            coupon_type_obj.amount -= 1
            coupon_type_obj.save()

        else:
            code = code_generator(coupon_type)

        # 기간(period)이 있는 경우 현재 날짜에서 그만큼 더한 날짜를 만료 날짜로 지정
        # 없는 경우 쿠폰 타입의 end_date를 만료 날짜로 지정
        if coupon_type_obj.period:
            expired_date = add_period(get_current_date(), coupon_type_obj.period)
        else:
            expired_date = coupon_type_obj.end_date

        return self.Meta.model.objects.create(
                type=coupon_type,
                expired_date=expired_date,
                owner=owner,
                code=code,
            )


class CouponStatisticsSerializer(ModelSerializer):
    """
    쿠폰 타입별 사용 내역 시리얼라이저
    쿠폰 타입별 발급된 쿠폰 내역과, 총 할인 금액, 사용 횟수, 발급 횟수 조회 가능
    coupons: 해당 쿠폰 타입인 쿠폰
    total_sale: 사용한 쿠폰의 총 할인액 (원화기준)
    use_counts: 쿠폰 사용 횟수
    issue_counts: 쿠폰 발행 횟수
    """
    coupons = CouponSerializer(many=True, read_only=True)
    total_sale = SerializerMethodField()
    use_count = SerializerMethodField()
    issue_count = SerializerMethodField()

    class Meta:
        model = CouponType
        fields = ('id', 'description', 'coupons', 'total_sale', 'use_count', 'issue_count')

    def get_total_sale(self, obj):
        """ 쿠폰 총 할인액(타입별) """
        total_sale = Coupon.objects.filter(type=obj.id, is_used=True).aggregate(Sum('sale_amount'))
        return total_sale['sale_amount__sum']

    def get_use_count(self, obj):
        """ 쿠폰 총 사용 횟수 """
        return Coupon.objects.filter(type=obj.id, is_used=True).count()

    def get_issue_count(self, obj):
        """ 쿠폰 총 발급 횟수 """
        return Coupon.objects.filter(type=obj.id).count()
