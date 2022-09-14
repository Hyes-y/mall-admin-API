from rest_framework.serializers import ModelSerializer
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
        """
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        period = data.get('period', None)
        dc_type = data.get('dc_type', None)
        iss_type = data.get('iss_type', None)
        amount = data.get('amount', None)
        code = data.get('code', None)

        if start_date > end_date:
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

        return data


class CouponSerializer(ModelSerializer):
    """ 쿠폰 발급 시리얼라이저 """
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['expired_date', 'code']

    def create(self, validated_data):
        coupon_type = validated_data.get('type', None)

        if not coupon_type:
            raise ValidationError("ERROR: 올바르지 않은 입력값입니다.")

        coupon_type_obj = CouponType.objects.get(id=coupon_type.id)

        # 쿠폰 타입이 유효하지 않음 (비활성화 되어있거나 유효 기간이 지난 경우)
        if not (coupon_type_obj.is_active and
                coupon_type_obj.end_date.strftime('%Y-%m-%d') >= get_current_date()):
            raise ValidationError("ERROR: 유효하지 않은 쿠폰 타입입니다.")

        # iss_type 1인 경우 사용자 발급
        if coupon_type_obj.iss_type == 1:
            owner = self.request.user
            code = coupon_type_obj.code

            if len(Coupon.objects.filter(
                    owner=owner,
                    code=code,
                    type=coupon_type
            )) >= 1:
                raise ValidationError("ERROR: 이미 발급받은 쿠폰입니다.")

        else:
            owner = validated_data.get('user', 1)
            code = code_generator(coupon_type)

        expired_date = add_period(get_current_date(), coupon_type_obj.period)

        return self.Meta.model.objects.create(
                type=coupon_type,
                expired_date=expired_date,
                owner=owner,
                code=code,
            )
